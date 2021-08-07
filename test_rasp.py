


# easy way to set up tests the same way they look in prod
from rasp_config import config_test as config
from raspi_api import DataHandler

ds = DataHandler()


import unittest

# TODO: think of test cases and build them out here.
class DataShipperTest(unittest.TestCase):

    # note: setUp and tearDown will each run once per test...

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # Let's plan out all that I want to test for the data shipper class:
    # 1. valid URL supplied with nothing else
    # 2. invalid URL supplied with nothing else
    # 3. valid URL supplied with buffer path (both with existing buffer path and without)
    # 4. invalid URL supplied with buffer path (both with existing buffer path and without)

    
# raspi_timestamp = str(datetime.now())
# row_to_insert = {
#     "hub_timestamp": "2021-06-07 17:00:02",
#     "raspi_timestamp": raspi_timestamp,
#     "sensor_name": "RV_bedroom_temp",
#     "measurement": "temperature",
#     "value": 81.3,
#     "units": "F"
# }

# cur.execute(
#     """
#     INSERT INTO rv_sensor ( 
#     hub_timestamp, raspi_timestamp, sensor_name, measurement, value, units)
#     values (:hub_timestamp, :raspi_timestamp, :sensor_name, :measurement, :value, :units)
#     """, row_to_insert)
# con.commit()

# print(cur.execute("SELECT * from rv_sensor;").fetchall())




