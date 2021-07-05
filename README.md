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
