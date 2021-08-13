
import json
import base64
from urllib.request import urlopen, Request


# # to cloud VM (or localhost)
# curl --header "Content-Type: application/json" \
#     --request POST \
#     --insecure \
#     -u 'rvsensor_user:this_is_a_secret' \
#     --data '{
#         "raspi_timestamp": "2021-08-09 13:22:53.640151", 
#         "sensor_name": "RV_bedroom_temp", 
#         "measurement": "humidity", 
#         "value": "60.2", 
#         "units": "%"
#         }' \
#     https://taylorvananne.com:5000/sensor/

auth_str = "Basic " + base64.b64encode(":".join(["rvsensor_user", "this_is_a_secret"]).encode()).decode()

data = {
        "raspi_timestamp": "2021-08-09 13:22:53.640151", 
        "sensor_name": "RV_bedroom_temp", 
        "measurement": "humidity", 
        "value": "60.2", 
        "units": "%"
        }

json_record = json.dumps(data).encode("utf-8")


url = "https://taylorvananne.com/sensor/"
# url_clean = urllib.parse.quote(self.url)
req = Request(url)
req.add_header('Content-Type', 'application/json; charset=utf-8')
req.add_header('Content-Length', len(json_record))
req.add_header("Authorization", auth_str)
resp = urlopen(req, json_record)
print(resp.status)
