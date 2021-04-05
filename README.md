> vyos_cfg_v2 is the new shiny version of https://github.com/MelHiour/vyos_cfg. The main difference is the "backend" used. In case of VYOS_CFG it is the good old paramiko, VYOS_CFG_V2 uses VYOS_API instead. 

> Please note you need to use VyOS rolling release at the moment to get the [API](https://docs.vyos.io/en/latest/configuration/service/https.html) support. 

# vyos_cfg.py
A simple script for pushing config to one or more instances of VyOS. It can send a predifined list of commands to devices using API. You can specify the logic using YAML syntaxis to support different scenarious (es. pre-deployment checks, deployment, post-deployment activities).
The list of supported commands is
- show - `show configuration interfaces`
- get - `show vvrp`, `show arp`
- set - `set system host-name BLAH`
- delete - `delete system host-name BLAH`

## Files
```
.
├── deployment.yaml             YAML file with deployment logic
├── helpers.py                  Just a bunch of functions
├── inventory.yaml              Use this to specify your devices 
├── key.py                      Contains API key(s). Please gitignore this
├── README.md                   This very file
├── requirements.txt            All you need to have to run the script
├── tests                       Pretending that I can write tests here...
└── vyos_cfg.py                 Main script
```

#### inventory.yaml
Contains just a host list with IP addresses and API key name from key.py
```
cat inventory.yaml
vyos1:
    address: 192.168.0.11
    port: 443
    key_name: default
vyos2:
    address: 192.168.0.12
    port: 443
    key_name: default
vyos3:
    address: 192.168.0.13
    port: 443
    key_name: default
vyos4:
    address: 192.168.0.14
    port: 443
    key_name: default
```

#### deployments.yaml
You can specify whatever logic you want here using YAML syntaxis. You can use **show**, **get**, **set**, **delete** and **comment** operations. Here are a few examples.

Most common scenarios with PRE and POST steps which allows us to check the state of the device before and after the changes.
```
# cat deployment.yaml
pre:
    - show interfaces ethernet
commands:
    - delete interfaces ethernet eth3 description API
post:
    - show interfaces ethernet
```

Just throw a bunch of commands towards device...
```
# cat deployment.yaml
one-off:
    - set system hostname
    - delete interfaces ethernet eth3 
    - delete interfaces ethernet eth4
```

You can also mix show and config commands in every block
```
# cat deployment.yaml
BEFORE:
    - show interfaces ethernet
    - delete interfaces ethernet eth3 
DEPLOYMENT:
    - set interfaces etherent eth3 description API
AFTER:
    - get interfaces 
```


#### Execution example
```
[root@localhost vyos_cfg_v2]# python3 vyos_cfg.py --help
Usage: vyos_cfg.py [OPTIONS]

Options:
  -i, --inventory TEXT   Inventory YAML  [required]
  -d, --deployment TEXT  Deployment file (YAML)  [required]
  -s, --skip-save        Whether to skip save config or not
  -b, --brave            No "Are you sure?" prompt. For brave hearts only
  --help                 Show this message and exit.
  
[root@localhost vyos_cfg_v2]# python3 vyos_cfg.py -i inventory.yaml -d deployment.yaml --brave
#######################################  DEPLOYMENT STARTED  #######################################
########################################  Starting "VYOS1"  ########################################
# PRE PHASE  #######################################################################################
['show interfaces ethernet']
# RESULTS  #########################################################################################

# COMMAND: show interfaces ethernet
# SUCCESS: True
# ERROR: None
# RESULT: {'ethernet': {'eth0': {'address': '192.168.0.11/24',
                       'hw-id': '50:01:00:01:00:00'},
              'eth1': {'description': 'API'},
              'eth2': {'description': 'BLAH', 'hw-id': '50:01:00:01:00:02'},
              'eth3': {'description': 'TESTING', 'hw-id': '50:01:00:01:00:03'}}}

# COMMANDS PHASE  ##################################################################################
['delete interfaces ethernet eth3']
# RESULTS  #########################################################################################

# COMMAND: delete interfaces ethernet eth3
# SUCCESS: True
# ERROR: None
# RESULT: None

# POST PHASE  ######################################################################################
['show interfaces ethernet']
# RESULTS  #########################################################################################

# COMMAND: show interfaces ethernet
# SUCCESS: True
# ERROR: None
# RESULT: {'ethernet': {'eth0': {'address': '192.168.0.11/24',
                       'hw-id': '50:01:00:01:00:00'},
              'eth1': {'description': 'API'},
              'eth2': {'description': 'BLAH', 'hw-id': '50:01:00:01:00:02'}}}

######################################  SAVING CONFIGURATION  ######################################

# COMMAND: Save config
# SUCCESS: True
# ERROR: None
# RESULT: Saving configuration to '/config/config.boot'...
Done


########################################  Starting "VYOS2"  ########################################
# PRE PHASE  #######################################################################################
['show interfaces ethernet']
# RESULTS  #########################################################################################

# COMMAND: show interfaces ethernet
# SUCCESS: True
# ERROR: None
# RESULT: {'ethernet': {'eth0': {'address': '192.168.0.12/24',
                       'hw-id': '50:01:00:02:00:00'},
              'eth1': {'description': 'API'},
              'eth2': {'description': 'BLAH', 'hw-id': '50:01:00:02:00:02'},
              'eth3': {'description': 'TESTING', 'hw-id': '50:01:00:02:00:03'}}}

# COMMANDS PHASE  ##################################################################################
['delete interfaces ethernet eth3']
# RESULTS  #########################################################################################

# COMMAND: delete interfaces ethernet eth3
# SUCCESS: True
# ERROR: None
# RESULT: None

# POST PHASE  ######################################################################################
['show interfaces ethernet']
# RESULTS  #########################################################################################

# COMMAND: show interfaces ethernet
# SUCCESS: True
# ERROR: None
# RESULT: {'ethernet': {'eth0': {'address': '192.168.0.12/24',
                       'hw-id': '50:01:00:02:00:00'},
              'eth1': {'description': 'API'},
              'eth2': {'description': 'BLAH', 'hw-id': '50:01:00:02:00:02'}}}

######################################  SAVING CONFIGURATION  ######################################

# COMMAND: Save config
# SUCCESS: True
# ERROR: None
# RESULT: Saving configuration to '/config/config.boot'...
Done


```
