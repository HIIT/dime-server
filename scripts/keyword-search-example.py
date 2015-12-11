#!/usr/bin/env python3

import requests
import sys
import json

#------------------------------------------------------------------------------

server_url = 'http://localhost:8080/api'
server_username = 'testuser'
server_password = 'testuser123'

#------------------------------------------------------------------------------

# Define query as a JSON object
query = [
    {"weight":0.5, "term":"dime"},
    {"weight": 0.1, "term":"reknow"}
]

r = requests.post(server_url + '/keywordsearch',
                  data=json.dumps(query),
                  headers={'content-type': 'application/json'},
                  auth=(server_username, server_password),
                  timeout=10)

if r.status_code != requests.codes.ok:
    print('ErrorNo connection to DiMe server!')
    sys.exit(1)

print('DiMe returns:', json.dumps(r.json(), indent=2))
