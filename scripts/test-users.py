#!/usr/bin/env python3

import requests
import sys
import socket
import time
import json

#------------------------------------------------------------------------------

server_url = 'http://localhost:8080/api'
server_username = 'testuser2'
server_password = 'testuser123'

#------------------------------------------------------------------------------

payload = {
    "username": server_username,
    "password": server_password
}

# Add user
r = requests.post(server_url + '/users',
                  data=json.dumps(payload),
                  headers={'content-type': 'application/json'},
                  timeout=10)

if r.status_code != requests.codes.ok:
    print('HTTP Error:', r.status_code)
    print(json.dumps(r.json(), indent=2))
    #sys.exit(1)
else:
    print('DiMe returns:', json.dumps(r.json(), indent=2))

# Check user
r = requests.get(server_url + '/users',
                 headers={'content-type': 'application/json'},
                 auth=(server_username, server_password),
                 timeout=10)

if r.status_code != requests.codes.ok:
    print('HTTP Error:', r.status_code)
    print(json.dumps(r.json(), indent=2))
    sys.exit(1)

print('DiMe returns:', json.dumps(r.json(), indent=2))

user_id = r.json()[0]["id"]
print('USER ID:', user_id)

# Delete user
r = requests.delete(server_url + '/users/{}'.format(user_id),
                 headers={'content-type': 'application/json'},
                 auth=(server_username, server_password),
                 timeout=10)

if r.status_code < 200 or r.status_code >= 300:
    print('HTTP Error:', r.status_code)
    print(json.dumps(r.json(), indent=2))
    sys.exit(1)

print('DiMe returns:', r.status_code)
