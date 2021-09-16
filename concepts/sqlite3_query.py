
# Quick things I want to test here:
# 1) function to query a sqlite3 database on disk
# 2) return data in json format

# import os
# os.listdir()
from datetime import datetime, timezone
utcdt = datetime.now(tz=timezone("America/Chicago"))
print(utcdt)
utcdt.timetz()
type(utcdt)


utcdt.tzinfo is None  # "unaware"
utcdt.tzinfo.tzoffset(None)


import sqlite3
import pandas as pd



con = sqlite3.connect("rv.db")
cur = con.cursor()

# cur.execute("select * from rv_sensor;").fetchall()


# pretty convenient... this is the template query I think we care most about...
# probably best to split these up in the actual JSON so we can more easily choose which one to 
# look at in the Javascript.
df = pd.concat([
        pd.read_sql_query("select * from rv_sensor where measurement='temperature' order by vm_timestamp desc limit 20;", con=con)
        ,pd.read_sql_query("select * from rv_sensor where measurement='humidity' order by vm_timestamp desc limit 20;", con=con)
    ])

print(df.head(2))
print(df.tail(2))


df = df.head(2)
# orient options: "split", "records", "index", "columns", "values", "table"
df.to_json(orient="records")

help(df.to_json)


