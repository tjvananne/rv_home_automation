
# Raspberry Pi API:
# this will collect data from hubitat, cache it to local sqlite database, and send it off to cloud server

# TODO: the requests POST will absolutely fail unless I get
# my certificate and private key off of my server.
# https://stackoverflow.com/questions/17576324/python-requests-ssl-error-for-client-side-cert
# https://superuser.com/questions/1194523/lets-encrypt-certbot-where-is-the-private-key
# I CANNOT use verify=False; I want to do this the right way.


# stdlib
from collections import deque
import os
from datetime import datetime
import json

# external
from fastapi import FastAPI
import uvicorn
from typing import Optional
from pydantic import BaseModel
import requests
from requests.auth import HTTPBasicAuth

# local
from rasp_db import setup_db
from rasp_config import config as config


# config:
JSON_BUFFER_PATH = config["JSON_BUFFER_PATH"]
SQLITE_PATH      = config["SQLITE_PATH"]
VM_URL           = config["VM_URL"]
VM_USER          = config["VM_USER"]
VM_PW            = config["VM_PW"]


def make_buffer(buffer_path, current_record):
    """
    args:
        - JSON_BUFFER_PATH (str): the path for where to check for buffered JSON data
                                    to be sent to the cloud VM.
        - current_record (dict):  the data that initiated this POST method function that
                                    needs to be sent to cloud VM.

    returns:
        - deque object of one or more records (dicts) to be sent to cloud VM 
    """
    
    if os.path.exists(buffer_path):
        with open(buffer_path, "r") as f:
            buff = deque(json.load(f))
            buff.append(current_record)
    else:
        buff = deque([current_record])
    
    return buff





def send_data(buffer, url, user, pw):
    for _record in buffer:
        resp = requests.post(url=url, json=list(_record), auth=HTTPBasicAuth(user, pw))
        if resp.status_code != 200:
            raise ConnectionError("Received something other than a 200 HTTP status code")


# handle database - should we really do this every time?
con, cur = setup_db(db_path = SQLITE_PATH)


# defining my own pydantic model for what one of these records will look like coming from the Hubitat
class SensorRecord(BaseModel):
    device_id: int  # "1"
    label: str      # "RV_bedroom_temp" (the name I assigned in Hubitat UI)
    name: str       # "temperature"
    value: float    # "71.7"  (it's quoted, by FastAPI should parse it based on pydantic model)
    date: str       # "2021-06-08T01:08:20+0000" - I'm going to keep as string, I don't really need date functionality
    unit: str
    isStateChange: Optional[str] = None
    source: str     # "DEVICE"


# create the app itself.
app = FastAPI()


# just for testing the web endpoint.
@app.get("/")
async def root():
    return {"message": "Hello World"}


# this will be the actual API for data collection.
@app.post("/sensor/")
async def process_data(record: SensorRecord):

    # parse / build row to be inserted into sqlite and sent to cloud vm
    raspi_timestamp = str(datetime.now())
    row_to_insert = {
        "hub_timestamp": record.date,
        "raspi_timestamp": raspi_timestamp,
        "sensor_name": record.label,
        "measurement": record.name,
        "value": record.value,
        "units": record.unit
    }

    # execute the insertion - this should happen no matter what, errors here are critical, crashing is appropriate
    print("executing insert...")
    cur.execute(
    """
    INSERT INTO rv_sensor ( 
    hub_timestamp, raspi_timestamp, sensor_name, measurement, value, units)
    values (:hub_timestamp, :raspi_timestamp, :sensor_name, :measurement, :value, :units)
    """, row_to_insert)
    con.commit()
    print(cur.execute("SELECT * from rv_sensor;").fetchall())
    con.close()

    # "buff" has one or more records we need to pass to cloud VM
    buff = make_buffer(JSON_BUFFER_PATH, row_to_insert)

    try:
        send_data(buff, url=VM_URL, user=VM_USER, pw=VM_PW)  #TODO: need to add certificate/key of cloud VM here
        os.remove(JSON_BUFFER_PATH)
    except ConnectionError:  # KeyError on os.environ[] or ConnectionError on requests.post()
        with open(JSON_BUFFER_PATH, "w") as f:
            json.dump(buff, f)

    # should we be returning something?
    # return  # no, this makes it a coroutine?
    



if __name__ == "__main__":
    uvicorn.run("raspi_api:app", port=5000, reload=False, debug=True, workers=1)
