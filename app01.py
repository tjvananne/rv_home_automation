
# first steps: https://fastapi.tiangolo.com/tutorial/first-steps/

from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run("app01:app", port=4999, reload=True, debug=True, workers=1)

# http://127.0.0.1:4999
# http://127.0.0.1:4999/docs
# http://127.0.0.1:4999/redoc
# http://127.0.0.1:4999/openapi.json

