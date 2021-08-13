# Raspberry Pi API:
# this will collect data from hubitat, cache it to local sqlite database, and send it off to cloud server

# TODO: I think there's a big issue here. I can't be so picky with Pydantic here b/c I don't really know exactly 
# what the JSON pattern looks like that I'll be consistently receiving...


# what does a raw record look like coming from the Hubitat to the Pi? (when I click the button on the temp sensor)
# {'content': 
#   {
#    'name': 'lastCheckin', 
#    'value': '2021-08-08 07:43:42', 
#    'displayName': 'RV_bedroom_temp', 
#    'deviceId': '1', 
#    'descriptionText': None, 
#    'unit': None, 
#    'type': None, 
#    'data': None
#   }
# }

# humidity:
# {'content': 
#   {
#       'name': 'humidity', 
#       'value': '62.5', 
#       'displayName': 'RV_bedroom_temp', 
#       'deviceId': '1', 
#       'descriptionText': None, 
#       'unit': '%', 
#       'type': None, 
#       'data': None
#   }
# }

# temperature:
# {'content': 
#   {
#       'name': 'temperature', 
#       'value': '65.7', 
#       'displayName': 'RV_bedroom_temp', 
#       'deviceId': '1', 
#       'descriptionText': None, 
#       'unit': '°F', 
#       'type': None, 
#       'data': None
#   }
# }





# stdlib
import base64
from urllib.request import urlopen, Request
import urllib.parse
import os
from datetime import datetime
import json

# external
import uvicorn
import fastapi
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

# process these
SENSOR_DISPLAYNAMES = ["RV_bedroom_temp"]
SENSOR_NAMES = ["temperature", "humidity"]


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
                    print("Sending Basic Auth POST request for data: ", json.dumps(_record))
                    req = Request(self.url)
                    req.add_header('Content-Type', 'application/json; charset=utf-8')
                    req.add_header('Content-Length', len(json_record))
                    req.add_header("Authorization", auth_str)
                    resp = urlopen(req, json_record)
                    print(resp.status)
                else:
                    # resp = requests.post(url=self.url, json=_record)
                    print("Sending POST request with no Auth for data: ", json.dumps(_record))
                    req = Request(self.url)
                    req.add_header('Content-Type', 'application/json; charset=utf-8')
                    req.add_header('Content-Length', len(json_record))
                    resp = urlopen(req, json_record)
                    print(resp.status)

                if resp.status != 200:
                    raise ConnectionError("Received something other than a 200 HTTP status code")
                else:
                    # remove any records that may have successfully been sent to cloud
                    print("data successfully sent.")
                    self.buffer_data = self.buffer_data[i:]
                    
            except Exception as e:  #(ConnectionError, requests.exceptions.ConnectionError):
                
                print(e)

                if self.buffer_path:
                    print("Couldn't send this record, writing buffer to disk...")
                    self._write_buffer()

                return

        # if we make it here without crash or exception, we've written all the data - delete buffer
        if self.buffer_path: 
            if os.path.exists(self.buffer_path):
                print("Removing buffer from disk if it exists...")
                os.remove(self.buffer_path)
        
        return


# handle database - should we really do this every time?
print("Setting up database connection...")
con, cur = setup_db(db_path = SQLITE_PATH)

# create data shipper instance
print("Creating data handler...")
ds = DataHandler(url=VM_URL, username=VM_USER, password=VM_PW, buffer_path=JSON_BUFFER_PATH)
 


# defining my own pydantic model for what one of these records will look like coming from the Hubitat
class SensorRecord(BaseModel):
    name: str        # "temperature"
    value: float     # "71.7"  (it's quoted, by FastAPI should parse it based on pydantic model)
    displayName: str # RV_bedroom_temp
    deviceId: int    # "1"
    descriptionText: Optional[str] = None
    unit: Optional[str] = None  # "F" or "%"
    type: Optional[str] = None
    data: Optional[str] = None


# create the app itself.
app = FastAPI()


# just for testing the web endpoint.
@app.get("/")
async def root():
    return {"message": "Hello World"}


# this will be the actual API for data collection.
@app.post("/sensor/")
async def process_data(record: fastapi.Request):

    print("Entering /sensor/ route on raspberry pi...")

    data = await record.json()  # "data" is a dictionary

    # how/if we further process a record depends on "name" and "displayName"
    try:
        print("parsing record...")
        content = data.get("content")
        rec_name = content.get("name")
        rec_displayname = content.get("displayName")
    except AttributeError as e:
        print("Error while parsing JSON input:", e)
        pass

    if (not rec_name in SENSOR_NAMES) or (not rec_displayname in SENSOR_DISPLAYNAMES):
        print(f"'name' of {rec_name} and/or 'displayName' of {rec_displayname} are excluded from this analysis... skipping these records")
        return


    # parse / build row to be inserted into sqlite and sent to cloud vm
    print("JSON content: ", content)

    raspi_timestamp = str(datetime.now())
    row_to_insert = {
        # "hub_timestamp": record.date,
        "raspi_timestamp": raspi_timestamp,
        "sensor_name": content.get("displayName"),
        "measurement": content.get("name"),
        "value": content.get("value"),
        "units": content.get("unit")
    }

    # execute the insertion - this should happen no matter what, errors here are critical, crashing is appropriate
    print("executing insert...")
    cur.execute(
    """
    INSERT INTO rv_sensor ( 
    raspi_timestamp, sensor_name, measurement, value, units)
    values (:raspi_timestamp, :sensor_name, :measurement, :value, :units)
    """, row_to_insert)
    con.commit()

    # send data to VM (buffer to disk if connectivity issue)
    ds.send_data(row_to_insert)
    



if __name__ == "__main__":
    print("Service starting up...")
    uvicorn.run("rasp_api:app", host="0.0.0.0", port=5000, reload=False, debug=False, workers=1, log_level="trace")


