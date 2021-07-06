




import sys
from multiprocessing import Process
from fastapi import FastAPI, Request
import uvicorn
import requests
from raspi_api import DataShipper
from datetime import datetime



# test starts here...
app = FastAPI()
ds = DataShipper(url="http://127.0.0.1:9999")


# using just the generic "Request" object, you can receive any generic JSON data passed to the endpoint.
# https://stackoverflow.com/questions/64379089/fastapi-how-to-read-body-as-any-valid-json
@app.post("/")
async def root(data: Request):
    return await data.json() 


api_proc = Process(target=uvicorn.run, kwargs={"app":"rasp_adhoc_query:app", "port":9999})
# uvicorn.run(app="rasp_adhoc_query:app", port=9999)
api_proc.start()


raspi_timestamp = str(datetime.now())
row_to_insert = {
    "hub_timestamp": raspi_timestamp,
    "raspi_timestamp": raspi_timestamp,
    "sensor_name": "RV_bedroom_temp",
    "measurement": "temp",
    "value": "77.8",
    "units": "F"
}

ds.send_data(row_to_insert)

# # generic test...
# resp = requests.post("http://127.0.0.1:9999", json={"my":"data"})
# resp.status_code
# resp.text


2 + 2

sys.exit(0)



# testing my own class

import sys
from raspi_api import DataShipper
from datetime import datetime
from rasp_config import config

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


ds = DataShipper(
    # url=config["VM_URL"],
    url="https://not-a-real-website-at-all.com",
    username=config["VM_USER"],
    password=config["VM_PW"],
    buffer_path=config["JSON_BUFFER_PATH"]
    )


ds.send_data(row_to_insert)


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
json.dumps([x])  # I want this, should be a list regardless of if 1 or more records


from collections import deque

q = deque()
x = {"field": "value", "field2": 9}
x2 = {"field": "value", "field2": 77}
q.append(x)
print(q)
q.append(x2)
print(q)

q[0]

list(q)

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

