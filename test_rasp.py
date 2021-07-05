
# easy way to set up tests the same way they look in prod
from rasp_config import config_test as config



# if testing:
    
#     raspi_timestamp = str(datetime.now())
#     row_to_insert = {
#         "hub_timestamp": "2021-06-07 17:00:02",
#         "raspi_timestamp": raspi_timestamp,
#         "sensor_name": "RV_bedroom_temp",
#         "measurement": "temperature",
#         "value": 81.3,
#         "units": "F"
#     }

#     cur.execute(
#         """
#         INSERT INTO rv_sensor ( 
#         hub_timestamp, raspi_timestamp, sensor_name, measurement, value, units)
#         values (:hub_timestamp, :raspi_timestamp, :sensor_name, :measurement, :value, :units)
#         """, row_to_insert)
#     con.commit()

#     print(cur.execute("SELECT * from rv_sensor;").fetchall())




