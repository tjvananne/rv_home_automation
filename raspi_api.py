
# Raspberry Pi API:
# this will collect data from hubitat, cache it to local sqlite database, and send it off to cloud server


# stdlib
import os
from datetime import datetime

# external
from fastapi import FastAPI
import uvicorn
from typing import Optional
from pydantic import BaseModel

# local
from rasp_db import setup_db


# handle database
con, cur = setup_db()

# defining my own pedantic model for what one of these records will look like coming from the Hubitat
class SensorRecord(BaseModel):
    device_id: int  # "1"
    label: str      # "RV_bedroom_temp" (the name I assigned in Hubitat UI)
    name: str       # "temperature"
    value: float    # "71.7"  (it's quoted, by FastAPI should parse it based on pydantic model)
    date: str       # "2021-06-08T01:08:20+0000" - I'm going to keep as string, I don't really need date functionality
    unit: Optional[str] = None
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
    # 1. receive data
    # 2. parse that data (what I care about)
    # 3. take a raspberry pi system timestamp (even though it'll be wrong...)
    # 4a. if JSON cache file exist, read it into memory, append "this" record to it
    # 4b. otherwise, just do nothing, you should have "this" record as JSON anyway
    # 5. attempt to pass JSON data (either one or many based on how step 4 went) to cloud VM
    # 6a. success:  delete JSON cache if it existed
    # 6b. fail:     write the JSON data back to disk (but now it'll have the newly appended record as well)

    # build row to be inserted
    raspi_timestamp = str(datetime.now())
    row_to_insert = {
        "hub_timestamp": record.date,
        "raspi_timestamp": raspi_timestamp,
        "sensor_name": record.label,
        "measurement": record.name,
        "value": record.value,
        "units": record.unit
    }

    # execute the insertion
    cur.execute(
    """
    INSERT INTO rv_sensor ( 
    hub_timestamp, raspi_timestamp, sensor_name, measurement, value, units)
    values (:hub_timestamp, :raspi_timestamp, :sensor_name, :measurement, :value, :units)
    """, row_to_insert)
    con.commit()
    print("done.")
    return
    



if __name__ == "__main__":
    uvicorn.run("raspi_api:app", port=5000, reload=True, debug=True, workers=1)



# {
#   "device_id":"1",
#   "label":"RV_bedroom_temp",
#   "name":"temperature",
#   "value":"71.7",
#   "date":"2021-06-08T01:08:20+0000",
#   "unit":"\u00b0F",
#   "isStateChange":null,
#   "source":"DEVICE"},


# {"device_id":"1","label":"RV_bedroom_temp","name":"lastCheckin","value":"2021-06-07 17:57:07","date":"2021-06-08T00:57:07+0000","unit":null,"isStateChange":null,"source":"DEVICE"}


