

import sqlite3

def setup_db(db_path):
    """
    args:
        * testing: boolean - this is a simple flag for testing the database table. Defaults to False.
    
    returns:
        * con (sqlite3 connection object)
        * cur (sqlite3 cursor object for the connection)
    """

    # connect to (or create) the database
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # TODO: fix DDL for this table
    # DDL for creating the table
    qry_create_table = """
    CREATE TABLE IF NOT EXISTS rv_sensor (
        vm_timestamp       TEXT NOT NULL   -- "date" from the VM itself
        ,raspi_timestamp    TEXT NOT NULL   -- NOT FROM HUB - this is the raspberry pi timestamp
        ,sensor_name        TEXT NOT NULL   -- "label" from hub
        ,measurement        TEXT NOT NULL   -- "name" from hub
        ,value              REAL NOT NULL   -- "value" from hub
        ,units              TEXT NOT NULL   -- "unit"  from hub
    ) --WITHOUT ROWID
    """

    # create table if it doesn't exist
    con.execute(qry_create_table)
    con.commit()

    return con, cur