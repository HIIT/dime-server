#!/usr/bin/env python3

import requests
import sys
import json

#------------------------------------------------------------------------------

server_url = 'http://localhost:8080/api'
server_username = 'testuser'
server_password = 'testuser123'

#------------------------------------------------------------------------------

r = requests.post(server_url + '/ping')

if r.status_code != requests.codes.ok:
    print('No connection to DiMe server!')
    sys.exit(1)

r = requests.get(server_url + '/profiles',
                  headers={'content-type': 'application/json'},
                  auth=(server_username, server_password),
                  timeout=10)

profile_id = None
for item in r.json():
    if item["name"] == "Test":
        profile_id = item["id"]

if profile_id is None:
    print("Unable to find Test profile!")
    sys.exit(1)

payload = { 
    "informationelement": { 
        "@type": "InformationElement", 
        "id": 15773
    }, 
    "weight": 0.22, 
    "actor": "FooAlgorithm" 
}

r = requests.post(server_url + '/profiles/{}/suggestedinformationelements'.format(profile_id),
                  data=json.dumps(payload),
                  headers={'content-type': 'application/json'},
                  auth=(server_username, server_password),
                  timeout=10)
print(r.status_code)
print('DiMe returns:', json.dumps(r.json(), indent=2))
