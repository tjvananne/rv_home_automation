

import os

# splitting this into separate file because multiple modules / files rely on it and
# it will make testing much easier...

# decision: should I just have one "config" dict and put both prod / test items in it?
# or is it best to do it this way and 
config = {
    # "prod" (lol)
     "JSON_BUFFER_PATH": "buffer.json"
    ,"SQLITE_PATH": "/home/taylor/home_automation/rasp.db"
    ,"VM_URL": os.environ["RV_CLOUD_VM_URL"]
    ,"VM_USER": os.environ["RV_CLOUD_VM_USER"]
    ,"VM_PW": os.environ["RV_CLOUD_VM_PW"]
}
 
config_test = {
    # test
    "JSON_BUFFER_PATH": "buffer_test.json"
    ,"SQLITE_PATH": "rasp_test.db"
    ,"VM_URL": os.environ["RV_CLOUD_VM_URL_TEST"]
    ,"VM_USER": os.environ["RV_CLOUD_VM_USER_TEST"]
    ,"VM_PW": os.environ["RV_CLOUD_VM_PW_TEST"]
}


