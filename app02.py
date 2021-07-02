
# first steps: https://fastapi.tiangolo.com/tutorial/first-steps/

from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("app02:app", port=5000, reload=True, debug=True, workers=1)



# {"device_id":"1","label":"RV_bedroom_temp","name":"temperature","value":"71.7","date":"2021-06-08T01:08:20+0000","unit":"\u00b0F","isStateChange":null,"source":"DEVICE"},
# {"device_id":"1","label":"RV_bedroom_temp","name":"lastCheckin","value":"2021-06-07 17:57:07","date":"2021-06-08T00:57:07+0000","unit":null,"isStateChange":null,"source":"DEVICE"}


