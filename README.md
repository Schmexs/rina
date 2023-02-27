# RINA Performance Evaluation
## Prerequisites

### RINA (rlite) Installation
Follow the instructions in the [rlite installation guide](https://github.com/rlite/rlite#2-software-**requirements**).

### Installing additional components
- iperf3
- netperf
- bird 

### bird.conf
If you are using Bird version 1, you need to change the "protocol kernel" section in the bird.conf as follows
```conf
 protocol kernel {
      import all;	
  	  export all;
    };
```

## Create your own RINA/IP-Structure with Networknamespaces
```bash
sudo python3 rina.py 
```

### Create the RINA/IP-Structure and make automatic tests
```bash
sudo python3 rina_test.py --help 
```
## Evaluation

Run `python3 -m http.server`

Open `http://127.0.0.1:8000/result.html?file=data-<REPLACE>.json` in your webbrowser.
