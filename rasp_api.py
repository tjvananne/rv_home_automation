
# Raspberry Pi API:
# this will collect data from hubitat, cache it to local sqlite database, and send it off to cloud server

# TODO: set up key-based ssh from: 
# - laptop to cloud VM


# stdlib
import base64
from urllib.request import urlopen, Request
import os
from datetime import datetime
import json

# external
import uvicorn
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

# local
from rasp_db import setup_db
from rasp_config import config as config


# config:
SQLITE_PATH      = config["SQLITE_PATH"]
JSON_BUFFER_PATH = config["JSON_BUFFER_PATH"]
VM_URL           = config["VM_URL"]
VM_USER          = config["VM_USER"]
VM_PW            = config["VM_PW"]


# set up HTTP Basic auth connection string
auth_str = "Basic " + base64.b64encode(":".join([VM_USER, VM_PW]).encode()).decode()


class DataHandler:
    """
    Sends data to a http(s) endpoint through POST method and JSON request body data. Config options for: 
        - using a buffer on disk for potential connectivity issues
    
    Initialize class attributes:
        - url (str): where to send the data
        - username (str): in case we're using HTTP Basic Auth
        - password (str): in case we're using HTTP Basic Auth
        - buffer_path Optional(str): where to check for buffered data in case of connectivity issues
    
    Methods:
        - send_data()
    """
    def __init__(self, url: str, username=None, password=None, buffer_path=None):
        self.url = url
        self.username = username
        self.password = password
        self.buffer_path = buffer_path
    
    def _make_buffer(self, current_record):
        """
        args:
            - current_record (dict):  the data we want to ship

        returns:
            - deque object of one or more records (dicts) to be sent to cloud VM 
        """

        # must short-circuit check if self.buffer_path is None, then check existence
        if self.buffer_path and os.path.exists(self.buffer_path):
            with open(self.buffer_path, "r") as f:
                buff = json.load(f)
                buff.append(current_record)
        # if either are false, skip the read from disk and create from current record
        else:
            buff = [current_record]
        
        self.buffer_data = buff

    def _write_buffer(self):

        with open(self.buffer_path, "w") as f:
            json.dump(self.buffer_data, f)


    def send_data(self, current_record: dict):
        
        self._make_buffer(current_record=current_record)
        
        for i, _record in enumerate(self.buffer_data):

            json_record = json.dumps(_record).encode("utf-8")

            try:

                if self.username and self.password:
                    # resp = requests.post(url=self.url, json=_record, auth=HTTPBasicAuth(self.username, self.password))
                    req = Request(VM_URL)
                    req.add_header('Content-Type', 'application/json; charset=utf-8')
                    req.add_header('Content-Length', len(json_record))
                    req.add_header("Authorization", auth_str)
                    resp = urlopen(req, json_record)
                else:
                    # resp = requests.post(url=self.url, json=_record)
                    req = Request(VM_URL)
                    req.add_header('Content-Type', 'application/json; charset=utf-8')
                    req.add_header('Content-Length', len(json_record))
                    resp = urlopen(req, json_record)
                if resp.status_code != 200:
                    raise ConnectionError("Received something other than a 200 HTTP status code")
                else:
                    # remove any records that may have successfully been sent to cloud
                    self.buffer_data = self.buffer_data[i:]
                    
            except Exception:  #(ConnectionError, requests.exceptions.ConnectionError):

                if self.buffer_path:
                    self._write_buffer()

                return

        # if we make it here without crash or exception, we've written all the data - delete buffer
        if self.buffer_path: 
            os.remove(self.buffer_path)
        
        return


# handle database - should we really do this every time?
con, cur = setup_db(db_path = SQLITE_PATH)

# create data shipper instance
ds = DataHandler(url=VM_URL, username=VM_USER, password=VM_PW, buffer_path=JSON_BUFFER_PATH)
 


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

    # send data to VM (buffer to disk if connectivity issue)
    ds.send_data(row_to_insert)
    



if __name__ == "__main__":
    uvicorn.run("raspi_api:app", port=5000, reload=False, debug=True, workers=1)
