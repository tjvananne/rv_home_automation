

import os
import sqlite3
from datetime import datetime



def setup_db(testing=False):
    """
    args:
        * testing: boolean - this is a simple flag for testing the database table. Defaults to False.
    
    returns:
        * con (sqlite3 connection object)
        * cur (sqlite3 cursor object for the connection)
    """

    # let's make sure this function is testable in the simplest way possible
    if testing:
        dbname = "rasp_test.db"
        if dbname in os.listdir():
            os.remove(dbname)
    else:
        dbname = "rasp.db"

    # connect to (or create) the database
    con = sqlite3.connect(dbname)
    cur = con.cursor()

    # DDL for creating the table
    qry_create_table = """
    CREATE TABLE IF NOT EXISTS rv_sensor (
        hub_timestamp       TEXT NOT NULL   -- "date" from hub
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

    if testing:
        
        raspi_timestamp = str(datetime.now())
        row_to_insert = {
            "hub_timestamp": "2021-06-07 17:00:02",
            "raspi_timestamp": raspi_timestamp,
            "sensor_name": "RV_bedroom_temp",
            "measurement": "temperature",
            "value": 81.3,
            "units": "F"
        }

        cur.execute(
            """
            INSERT INTO rv_sensor ( 
            hub_timestamp, raspi_timestamp, sensor_name, measurement, value, units)
            values (:hub_timestamp, :raspi_timestamp, :sensor_name, :measurement, :value, :units)
            """, row_to_insert)
        con.commit()

        print(cur.execute("SELECT * from rv_sensor;").fetchall())
    return con, cur



if __name__ == "__main__":
    con, cur = setup_db(testing=True)
    print(type(con))
    print(type(cur))


