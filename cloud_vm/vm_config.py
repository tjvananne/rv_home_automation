

import os

# splitting this into separate file because multiple modules / files rely on it and
# it will make testing much easier...

# decision: should I just have one "config" dict and put both prod / test items in it?
# or is it best to do it this way and 
config = {
    # "prod" (lol)
    "SQLITE_PATH": "/home/taylor/home_automation/rv.db"
    ,"VM_USER": os.environ["RV_CLOUD_VM_USER"]
    ,"VM_PW": os.environ["RV_CLOUD_VM_PW"]

}
 
config_test = {
    # test
    "SQLITE_PATH": "rv_test.db"
    ,"VM_USER": os.environ["RV_CLOUD_VM_USER_TEST"]
    ,"VM_PW": os.environ["RV_CLOUD_VM_PW_TEST"]
}


