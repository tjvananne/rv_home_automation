#!/user/bin/bash

# RV Sensor service for Raspberry Pi running on RV LAN 

# activate our venv, cd to project directory, run script
source ~/.venv/rvsensor/bin/activate
cd /home/taylor/home_automation/rv_home_automation
python ./raspberry/rasp_api.py

