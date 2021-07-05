

import sys
from raspi_api import process_data
from datetime import datetime

raspi_timestamp = str(datetime.now())
row_to_insert = {
    "device_id": 1  # "1"
    ,"label":"RV_bedroom_temp"  #(the name I assigned in Hubitat UI)
    ,"name": "temperature"
    ,"value": "71.7" # (it's quoted, by FastAPI should parse it based on pydantic model)
    ,"date":"2021-06-08T01:08:20+0000"  #- I'm going to keep as string, I don't really need date functionality
    ,"unit": "F"
    ,"isStateChange": "None"
    ,"source": "DEVICE"
}

async def mytest():
    k = await(process_data(row_to_insert))

sys.exit(0)


from rasp_db import setup_db
from rasp_config import config
from datetime import datetime


raspi_timestamp = str(datetime.now())
row_to_insert = {
    "device_id": 1  # "1"
    ,"label":"RV_bedroom_temp"  #(the name I assigned in Hubitat UI)
    ,"name": "temperature"
    ,"value": "71.7" # (it's quoted, by FastAPI should parse it based on pydantic model)
    ,"date":"2021-06-08T01:08:20+0000"  #- I'm going to keep as string, I don't really need date functionality
    ,"unit": "F"
    ,"isStateChange": "None"
    ,"source": "DEVICE"
}


# quick test - ok so this returns a 405...
import requests
# resp = requests.post("https://taylorvananne.com/not/a/page")
resp = requests.post("http://127.0.0.1:5000/sensor/", json=row_to_insert)
print(resp.text)
resp.status_code  # 405 Not allowed / 404 Not found



con, cur = setup_db(config["SQLITE_PATH"])
print(cur.execute("SELECT * from rv_sensor").fetchall())


import sqlite3
con = sqlite3.connect(config["SQLITE_PATH"])
cur = con.cursor()
print(cur.execute("SELECT * from rv_sensor").fetchall())











# adhoc testing...
import json

x = {
    "field": "value",
    "field2": 9
}

json.dumps(x)
json.dumps([x])


from collections import deque

q = deque()
x = {"field": "value", "field2": 9}
x2 = {"field": "value", "field2": 77}
q.append(x)
print(q)
q.append(x2)
print(q)

q[0]

# you can convert deque of two dict-like objects to list then JSON string
mystrj = json.dumps(list(q))
print(mystrj)

# you can convert that json string back to list of dicts then a deque() object
q = deque(json.loads(mystrj))

q.popleft()
print(q)
# recap: if you only q.append() and q.popleft(), then you basically have a FIFO queue

# also, you have to convert to list prior to dumping to JSON string
json.dumps(list(q))

