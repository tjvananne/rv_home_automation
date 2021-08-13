
# Can I create an async FastAPI endpoint and execute urllib request inside of it?


# external
import uvicorn # to run stuff.
import fastapi
from fastapi import FastAPI
from urllib.request import urlopen, Request

app = FastAPI()

# just for testing the web endpoint.
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/reverse/")
async def reverse_api(record: fastapi.Request):
    
    data = await record.json()
    print(data)
    
    print("now we're going to try and use urllib to request some stuff...")
    req = Request("https://jsonplaceholder.typicode.com/todos/1")
    resp = urlopen(req)
    print(resp.data)
    print("done.")
    

if __name__ == "__main__":
    uvicorn.run("fastapi_reverse_api:app", port=5001, reload=False, debug=False, workers=1, log_level="debug")

