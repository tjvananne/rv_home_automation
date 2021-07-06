# RV_Temp_Sensor Project

In my RV, I have a temperature sensor that transmits data (zigbee) to my [Hubitat device](https://hubitat.com/). When the Hubitat receives event data, that data is automatically sent to my Raspberry Pi through my router whenever an event is received by the Hubitat. 

The goal is to receive that data on my Raspberri Pi, cache the data to a local sqlite database, and then attempt to pass that data to a cloud VM I have running up in Linode - dependent on if we have cell data on our hotspot. The functionality I'm aiming for is to be able to see the temperature of my RV from anywhere.

---

## components of the project

* `rasp*` files refer to logic that will be hosted on my LAN raspberry pi
* `cloud*` files refer to logic that will be hosted on my Linode cloud server - these are primarily for receiving and processing data from the raspberry pi
* finally, there will be a web visualization component, but I don't yet have that part thought through


---

## Technology I specifically want to experiment with

* `FastAPI` - I really like how similar this is to Flask, but it's async and fast out of the box, and the integration with `pydantic` for modeling your JSON input is super interesting to me
* `Docker`, I simply don't have much experience deploying apps from a local docker registry, I want to try that (for back-end and front-end of cloud VM; likely won't do that for Raspberry Pi)
* `unittest` - I generally just write a bunch of assert statements for testing, but I actually want to use the built-in test framework. Also may test out `pytest` which works with raw assert statements...


## Dependencies

* see `requirements.txt` file
* using miniconda Python 3.9 environment
* developing on Ubuntu 20.04 Desktop


## Lessons Learned



### separation of business logic and routes

It seems really challenging to do any type of testing or debugging within a `async def` "route function" in fast API. I think my strategy to resolve this will be to pull all of the logic of a route out into its own class. That way I'll keep the logic within my routes very short. And I can test whatever I want with the class itself. I've created the `DataShipper` class for this. I don't want this tightly coupled at all to FastAPI. I want this to be a useful class outside the context of this project if I ever wanted to reuse it.

pseudocode: 
```
fastAPI route:
    async def function:
        <create my class here>
        <call super high level class methods here>
        done.
```


### testing ideas

**developing testing strategy for APIs**

So my API is going to need to make a `POST` to yet another API...
In order to make testing more automated, I think I'd like to set up a test case that spins up a fast API end point in a separate process that I can control within the scope of the test itself. Going to try and set this up with `multiprocessing.Process` first to see if that works out.

Alright, so I can successfully create and run the `uvicorn.run()` method in it's own `Process`, but it does still depend on the name of the file where the `FastAPI()` (`app`) class is created. I don't think there's a way around this? It's honestly fine though. I will probably need a way to kill that Process after the test has completed. `Process.terminate()` should do the trick it sounds like, otherwise we can get the `pid` as an attribute of the Process object itself and then fire off a terminal command to kill the process from Python. I do need to make sure this properly shuts down the API so that the port can be reused in future tests. 


### Issues along the way...

* `RuntimeError: deque mutated during iteration`:

so what I'm trying to do is have a deque object, iterate through it, then if that item within the deque object is sent to VM server successfully, then `popleft` so we aren't looking at that one anymore... 


### Questions along the way...

* I need to really think about what nginx is doing vs FastAPI. The cloud VM only has one public IP address. FastAPI and Nginx can't both be listening on the same port (I don't think... test this?). I can listen on Nginx and forward stuff to FastAPI, but that's probably only for client-facing dynamic stuff. What I'm trying to do is just backend data collection, so I can just send it to whatever port and it doesn't atter at all. The reason I bring all of this up is because I'm trying to think about where to put my HTTP Basic Auth logic. I just realized that I don't actually need nginx to do this. There's a way to use [HTTP Basic Auth within FastAPI itself](https://fastapi.tiangolo.com/advanced/security/http-basic-auth/)

