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


#### Hubitat and sensor specific questions:

- Aqara temp sensor:
    - How often does it report?
        - https://community.hubitat.com/t/xiaomi-aqara-zigbee-device-drivers-possibly-may-no-longer-be-maintained/631/930


#### Near realtime visualization options:

Building real time data visualization of my temperature sensor:

Concept of the day: WEBHOOKS

API: when you need to pull data from a resource
WEBHOOKS: when you need data pushed to you when an event happens
- aka: "reverse API"

I think we can combine HTTP POST / webhooks / websockets to create some interesting near-real-time patterns for displaying the temperature data from my RV.

Potential resources:

**Python tornado websockets with d3.js visualization - interesting...**
- https://medium.com/@benjaminmbrown/real-time-data-visualization-with-d3-crossfilter-and-websockets-in-python-tutorial-dba5255e7f0e

**this SO post makes leads me to some interesting thoughts...**
- https://stackoverflow.com/questions/63099518/sending-a-websocket-message-from-a-post-request-handler-in-express
-- I need to learn more about web hooks
-- I think a web hook is an API that can convert a POST http req to a websocket.send()?
--- if that isn't what it is, then I want what I said lol

**let's figure out exactly what a web hook is:**
**Clearly there's some SEO competition for this question....**
- https://sendgrid.com/blog/whats-webhook/
-- "A webhook (also called a web callback or HTTP push API) is a way for an app to provide other applications with real-time information. A webhook delivers data to other applications as it happens, meaning you get data immediately. Unlike typical APIs where you would need to poll for data very frequently in order to get it real-time. This makes webhooks much more efficient for both provider and consumer. The only drawback to webhooks is the difficulty of initially setting them up."
- https://www.twilio.com/docs/glossary/what-is-a-webhook
- https://zapier.com/blog/what-are-webhooks/


**ok so webhooks are sick; this will be super helpful for testing:**
- https://webhook.site


so.. if I tell my hubitat device to push to www.taylorvananne.com:9000, I can have an HTTP server listening for POST requests there. I can then take that JSON associated with that POST command, and send it to a websocket at localhost:9001 (keep in mind, we're already on the www.taylorvananne.com server, so it's localhost now). THEN I can set up d3.js visualizations to update based on the data coming in from the websocket.



**testing maker API**
**I only have this set up for local LAN access, no remote/cloud**

**Event History Template**
http://192.168.8.107/apps/api/6/devices/[Device ID]/events?access_token=0d38a5e8-f4d8-4bed-a792-619615659af9

**Event History for aqara temp / humidity sensor**
http://192.168.8.107/apps/api/6/devices/1/events?access_token=0d38a5e8-f4d8-4bed-a792-619615659af9

**NICE, that works!**

So now I've got this working to where I'll be able to poll (GET) my hubitat for changes from the aqara temperature sensor. That's great and all, but it would be way more slick to instead set up some logic to POST from my hubitat TO my raspberry pi device whenever something changes. Ideally, it would only be whenever the TEMP changes. So I'm thinking I need "Apps Code" for this. 

But, before I go about writing code for this. In the maker API, there is a section that says "URL to send device events to by POST" - so that sounds super interesting...

I'm thinking I could:

1) set up raspberry pi with static IP address
2) set up a simple http server listening on that IP address / port combination
3) pass that data to my cloud (linode?) server
4) maybe that cloud linode server is running some websocket logic where I can update the charts/graphs in real time? Like have a tile for current temp, but then show the history somewhere as well? Just a rolling history of like the past 10-20 readings?

**Other hubitat maker api questions...**
Can I control which devices send data by POST?

Maybe I could set up my own pub/sub type of deal where I route the data to different places based on it's "label" / "name" combination (the name I gave the sensor?):
* label = name I gave to the sensor
* name = ["humidity"|"temperature"]


I don't think it's feasible or worth-while to run kafka on my pi. But maybe there's like a super slim version of Kafka or something I could run instead? I think I could easily do what I need in Python, but I'd rather it be in something ultra efficient.
Rust? Go?




