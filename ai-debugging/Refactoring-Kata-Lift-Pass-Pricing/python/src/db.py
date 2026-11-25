"""Database connection and schema setup helpers.

This module isolates SQL-driver selection and driver-specific compatibility.
It is used by the HTTP pricing module, but deliberately has no Flask dependency.
"""

from pathlib import Path


def create_lift_pass_db_connection(connection_options):
    """Try the supported database drivers and return the first working connection.

    Reads:
        connection_options for database host, user, password, and database name;
        the local environment to discover ODBC drivers and available libraries.
    Modifies:
        Installs no application state; driver attempts may initialize an SQLite
        file and create seed tables in that database.
    Returns:
        A live database connection.
    Business logic:
        Prefers ODBC, then PyMySQL, then SQLite. A failed attempt is reported and
        the next option is tried.
    """
    connection_functions = [
        try_to_connect_with_odbc,
        try_to_connect_with_pymysql,
        try_to_connect_with_sqlite3,
    ]
    for fun in connection_functions:
        try:
            connection = fun(connection_options)
            if connection is not None:
                return connection
        except Exception as e:
            print(f"unable to connect to db with {fun}")
    raise RuntimeError("Unable to connect to the database.")


def try_to_connect_with_sqlite3(connection_options):
    """Create or open the fallback SQLite lift-pass database.

    Reads:
        The local ``lift_pass.db`` file and an ignored connection_options value.
        The existing database is probed for the holidays table.
    Modifies:
        Creates the SQLite file, base_price and holidays tables, and seed rows
        when the schema probe indicates the database is not initialized.
    Returns:
        An SQLite connection, or raises sqlite3.OperationalError for a setup failure.
    Business logic:
        SQLite is the local fallback and supplies the default 1jour/night prices
        and winter-holiday dates used by the pricing service.
    """
    import sqlite3
    connection = sqlite3.connect("lift_pass.db")
    try:
        connection.execute(
            'SELECT * FROM holidays '
            'WHERE holiday = 2019-03-04'
        )
    except sqlite3.OperationalError:
        pass
    else:
        return connection

    create_statements = [
        """CREATE TABLE IF NOT EXISTS base_price (
            pass_id INTEGER PRIMARY KEY AUTOINCREMENT,
            type VARCHAR(255) NOT NULL UNIQUE,
            cost INTEGER NOT NULL
        );""",
        """INSERT INTO base_price (type, cost) VALUES ('1jour', 35);""",
        """INSERT INTO base_price (type, cost) VALUES ('night', 19);""",
        """CREATE TABLE IF NOT EXISTS holidays (
            holiday DATE NOT NULL,
            description VARCHAR(255) NOT NULL
        );""",
        "INSERT INTO holidays (holiday, description) VALUES ('2019-02-18', 'winter');",
        "INSERT INTO holidays (holiday, description) VALUES ('2019-02-25', 'winter');",
        "INSERT INTO holidays (holiday, description) VALUES ('2019-03-04', 'winter');",
    ]
    for statement in create_statements:
        connection.execute(statement)
        connection.commit()

    return connection


def try_to_connect_with_pymysql(connection_options):
    """Open a MySQL-compatible connection using PyMySQL.

    Reads:
        Host, user, password, and database values from connection_options.
    Modifies:
        Creates a PyMySQL connection and cursor wrapper type.
    Returns:
        A PyMySQL connection configured to use the compatible cursor wrapper.
    Business logic:
        Converts SQL ``?`` placeholders to PyMySQL's ``%s`` form so shared route
        code can work consistently with SQLite and MySQL.
    """
    import pymysql.cursors

    class PyMySQLCursorWrapper(pymysql.cursors.Cursor):
        """
        The pymysql.cursors.Cursor class very nearly works the same as the odbc equivalent. Unfortunately it doesn't
        understand the '?' in a SQL statement as an argument placeholder, and instead uses '%s'. This wrapper fixes that.
        """
        def mogrify(self, query: str, args: object = ...) -> str:
            """Read a query and return it with ``?`` placeholders rewritten.

            Reads: SQL text and argument data.
            Modifies: Creates a rewritten copy of the query.
            Returns: A PyMySQL-formatted query string.
            Business logic: Preserves the application's SQL placeholder contract.
            """
            query = query.replace('?', '%s')
            return super().mogrify(query, args)

    connection = pymysql.connect(host=connection_options["host"],
                                 user=connection_options["user"],
                                 password=connection_options["password"],
                                 database=connection_options["database"],
                                 cursorclass=PyMySQLCursorWrapper)

    return connection


def try_to_connect_with_odbc(connection_options):
    """Open a MySQL-compatible database through an available ODBC driver.

    Reads:
        Installed ODBC drivers and connection_options host/user/database/password.
    Modifies:
        Creates a pyodbc connection when a MySQL or MariaDB driver is available.
    Returns:
        A pyodbc connection, or None when no suitable driver exists.
    Business logic:
        ODBC is the first-preference database transport, but is optional in the
        fallback sequence.
    """
    driver = get_mariadb_driver()
    if driver:
        import pyodbc
        connection_string = make_connection_string_template(driver) % (
            connection_options["host"],
            connection_options["user"],
            connection_options["database"],
            connection_options["password"],
        )
        return pyodbc.connect(connection_string)
    return None


def get_mariadb_driver():
    """Find the preferred installed MySQL or MariaDB ODBC driver.

    Reads:
        The names returned by pyodbc.drivers().
    Modifies:
        None.
    Returns:
        The lexicographically greatest matching driver name, or None.
    Business logic:
        Selecting a matching driver enables the ODBC connection attempt.
    """
    import pyodbc
    drivers = []
    for driver in pyodbc.drivers():
        if driver.startswith("MySQL") or driver.startswith("MariaDB"):
            drivers.append(driver)

    if drivers:
        return max(drivers)
    else:
        return None


def make_connection_string_template(driver):
    """Build the ODBC connection-string format for a selected driver.

    Reads:
        The ODBC driver name.
    Modifies:
        None.
    Returns:
        A template containing positional placeholders for server, user,
        database, and password.
    Business logic:
        Centralizes the ODBC setup needed for MySQL/MariaDB authentication.
    """
    return 'DRIVER={' + driver + '};SERVER=%s;USER=%s;OPTION=3;DATABASE=%s;PASSWORD=%s'
