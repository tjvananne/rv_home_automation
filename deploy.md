# notes on deployment

This is an ultra tiny project. I'm only going to use rsync over ssh to deploy this. I also don't really care about deploying the entire project to the raspberry pi and the cloud VM, even though each of those only need to run their own scripts. I didn't feel the need to separate these pieces out.

```bash
# deploy to cloud VM 
taylor@taylor-UX305LA:~/Documents/home_automation/rv_home_automation$ rsync -ae ssh ./ taylor@198.58.103.20:~/home_automation/rv_home_automation/
# deploy to raspberry pi on LAN
taylor@taylor-UX305LA:~/Documents/home_automation/rv_home_automation$ rsync -ae ssh ./ taylor@192.168.8.249:~/home_automation/rv_home_automation/
```

raspberry pi info (at least where we're shipping all of the hubitat data from Maker API for now)

```
http://192.168.8.249:8000
```

On both the raspberry pi on my LAN and the cloud VM, I'm using a python3 venv called `rvsensor` which I activate with:
`source ~/.venv/rvsensor/bin/activate`




