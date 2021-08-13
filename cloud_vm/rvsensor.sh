#!/user/bin/bash

# RV Sensor service for cloud vm

# activate our venv, cd to project directory, run script
source ~/.venv/rvsensor/bin/activate
cd /home/taylor/home_automation/rv_home_automation
python ./cloud_vm/vm_api.py


