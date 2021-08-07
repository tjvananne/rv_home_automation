
import base64
from urllib.request import urlopen, Request

user = "taylor"
pw  = "TAYLORPW"

# NO - don't base64 encode these separately first. Join by ":" then base64 the whole string.
# auth_str = "Basic " + ":".join([base64.b64encode(user).decode(), base64.b64encode(pw).decode()])
auth_str = "Basic " + base64.b64encode(":".join([user, pw]).encode()).decode()
print(auth_str)


req = Request("http://127.0.0.1:5001/users/me")
req.add_header("Authorization", auth_str)
# req.add_header("Authorization", "taylor:TAYLORPW")
resp = urlopen(req)
print("response status is: ", resp.status)









