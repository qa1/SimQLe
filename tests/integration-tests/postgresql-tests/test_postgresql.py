"""Integrate test the recordset function.py."""


from simqle import load_connections, recordset, execute_sql, reset_connections
import os
from sqlalchemy.exc import ProgrammingError


def setup_function():
    """Clear connections each test."""
    reset_connections()


def teardown_function():
    """Remove the database used in the tests."""
    try:
        os.remove("/tmp/database.db")
    except OSError:
        pass


def test_recordset():
    """Test the recordset function.py."""
    load_connections("./tests/integration-tests/mysql-tests"
                     "/.connections.yaml")

    # create a table
    sql = "drop table if exists TestTable"
    execute_sql(con_name="mysql-database", sql=sql)

    sql = """
        create table TestTable (
            id serial,
            TestField text
        )
        """
    execute_sql(con_name="mysql-database", sql=sql)

    # insert some data
    sql = """
        insert into TestTable (TestField) values
        ('some data 1'),
        ('some data 2')
        """
    execute_sql(con_name="mysql-database", sql=sql)

    # collect the data into a recordset
    sql = """
        select id, TestField
        from TestTable
        """
    rst = recordset(con_name="mysql-database", sql=sql)

    # assert the recordset takes the form we would expect
    assert rst == (

        # data first - a list of tuples
        [(1, "some data 1"),
         (2, "some data 2")],

        # headings second for convenience
        ["id", "TestField"]
    )

    # test named parameters
    sql = """
        select id
        from TestTable
        where TestField = :TestParameter
        and id = :id
        """
    params = {
        # string parameter
        "TestParameter": "some data 2",

        # number parameter
        "id": 2
        }

    rst = recordset(con_name="mysql-database", sql=sql, params=params)

    assert rst == (

        # data first - a list of tuples
        [(2,)],

        # headings second for convenience
        ["id"]
    )


def test_sql_with_errors():
    """Test the exception handling of execute_sql."""
    load_connections("./tests/integration-tests/mysql-tests"
                     "/.connections.yaml")

    # create a table
    sql = "drop table if exists TestTable"
    execute_sql(con_name="mysql-database", sql=sql)

    # An otherwise valid SQL statement with a typo
    sql = """
        creat table TestTable (
            id serial,
            TestField text
        )
        """

    try:
        execute_sql(con_name="mysql-database", sql=sql)
    except Exception as exception:
        assert type(exception) == ProgrammingError

    # create a table
    sql = "drop table if exists TestTable"
    execute_sql(con_name="mysql-database", sql=sql)

    sql = """
        create table TestTable (
            id serial,
            TestField text
        )
        """
    execute_sql(con_name="mysql-database", sql=sql)

    sql = "select * from TestTable2"
    try:
        recordset(con_name="mysql-database", sql=sql)
    except Exception as exception:
        assert type(exception) == ProgrammingError
