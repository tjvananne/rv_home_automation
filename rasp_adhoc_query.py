

from rasp_db import setup_db

con, cur = setup_db()
print(cur.execute("SELECT * from rv_sensor").fetchall())


# adhoc testing...
import json

