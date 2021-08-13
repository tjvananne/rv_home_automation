
# these will be mini curl commands to help debug my endpoints...


# to raspberry pi (or localhost)
curl --header "Content-Type: application/json" \
    --request POST \
    --data '{"content": {
    "name": "temperature", 
    "value": "65.7", 
    "displayName": "RV_bedroom_temp", 
    "deviceId": "1", 
    "descriptionText": "None", 
    "unit": "°F", 
    "type": "None", 
    "data": "None"}}' \
    http://localhost:5000/sensor/


# to cloud VM (or localhost)
curl --header "Content-Type: application/json" \
    --request POST \
    --insecure \
    -u 'rvsensor_user:this_is_a_secret' \
    --data '{
        "raspi_timestamp": "2021-08-09 13:22:53.640151", 
        "sensor_name": "RV_bedroom_temp", 
        "measurement": "humidity", 
        "value": "60.2", 
        "units": "%"
        }' \
    https://taylorvananne.com:5000/sensor/


