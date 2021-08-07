
# stdlib
import secrets

# external
import uvicorn # to run stuff.
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()

security = HTTPBasic()

@app.get("/users/me")
def read_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "taylor")
    correct_password = secrets.compare_digest(credentials.password, "TAYLORPW")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
    
    
    return {
        "username": credentials.username, 
        "password": credentials.password
    }



if __name__ == "__main__":
    uvicorn.run("example_fastapi_basic_auth:app", port=5001, reload=False, debug=True, workers=1)

