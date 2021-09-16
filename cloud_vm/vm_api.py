
# Cloud VM Server API:
# this will collect data from the raspberry PI on my LAN and cache it to 
# sqlite database (is this a bad idea?) for my web app to visualize.

# TODO: if my blog is also hosted on this site. What are my options and requirements here?
# Does the RV temp visualization have to be at a different port?
# Can it be same port but just a different path like "/rv-temp/"?
#   - how would that work? Nginx could forward to different port?
#   - could be flask app running

# FastAPI and Nginx can't be listening on the same host/port, can they?
# would this mean I need to connect nginx to uvicorn in the same 
# way that gunicorn does? Like through a HTTP or unix socket? Is
# that even possible?


# stdlib
from datetime import datetime
import secrets

# external
import uvicorn
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

# local
from vm_db import setup_db
from vm_config import config


# config:
SQLITE_PATH      = config["SQLITE_PATH"]
HTTP_USER        = config["VM_USER"]
HTTP_PASSWORD    = config["VM_PW"]


# defining my own pydantic model for what one of these records will look like coming from the Hubitat
class SensorRecord(BaseModel):
    raspi_timestamp: str
    sensor_name: str
    measurement: str
    value: float
    units: str



# handle database - should we really do this every time?
con, cur = setup_db(db_path = SQLITE_PATH)
 


# create the app itself.
app = FastAPI()


# just for testing the web endpoint.
# no security here so we can just test connectivity.
@app.get("/")
async def root():
    return {"message": "Hello World"}

# what even is this? just holds data maybe?
security = HTTPBasic()

# this will be the actual API for data collection.
@app.post("/sensor/")
async def process_data(record: SensorRecord, 
    credentials: HTTPBasicCredentials = Depends(security)):

    # HTTP Basic Auth security check
    correct_username = secrets.compare_digest(credentials.username, HTTP_USER)
    correct_password = secrets.compare_digest(credentials.password, HTTP_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"}
        )

    # TODO: think about how to process relative timestamps?
    # parse / build row to be inserted into sqlite and sent to cloud vm
    vm_timestamp = str(datetime.utcnow())
    row_to_insert = {
        "vm_timestamp": vm_timestamp,  
        "raspi_timestamp": record.raspi_timestamp,
        "sensor_name": record.sensor_name,
        "measurement": record.measurement,
        "value": record.value,
        "units": record.units
    }

    # execute the insertion - this should happen no matter what, errors here are critical, crashing is appropriate
    print("executing insert...")
    cur.execute(
    """
    INSERT INTO rv_sensor ( 
    vm_timestamp, raspi_timestamp, sensor_name, measurement, value, units)
    values (:vm_timestamp, :raspi_timestamp, :sensor_name, :measurement, :value, :units)
    """, row_to_insert)
    con.commit()
    # print(cur.execute("SELECT * from rv_sensor;").fetchall())
    # con.close()


@app.post("/get-sensor-data/")
async def get_data():
    pass


if __name__ == "__main__":
    uvicorn.run("vm_api:app", host="0.0.0.0", port=5000, 
            reload=False, debug=False, workers=1, log_level="trace")
