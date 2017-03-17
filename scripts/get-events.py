#!/usr/bin/env python3

import requests
import sys
import socket
import time
import json
import dime

#------------------------------------------------------------------------------

server_url = 'http://localhost:8080/api'
server_username = 'testuser'
server_password = dime.password(server_username)

json_filename = 'dime-events.json'

#------------------------------------------------------------------------------

# ping server (not needed, but fun to do :-)
r = requests.post(server_url + '/ping')

if r.status_code != requests.codes.ok:
    print('No connection to DiMe server!')
    sys.exit(1)

params = ""
if len(sys.argv) > 1:
    params = "?" + "&".join(sys.argv[1:])

request_url = server_url + '/data/events' + params
print('GET', request_url)

r = requests.get(request_url,
                 headers={'content-type': 'application/json'},
                 auth=(server_username, server_password))

if r.status_code > 299:
    print('HTTP Error:', r.status_code)
    sys.exit(1)

j = r.json()

print("Got {} events from DiMe.".format(len(j)), file=sys.stderr)

# for elem in j[:2]:
#     print(json.dumps(elem, indent=2))

with open(json_filename, 'w') as fp:
    json.dump(j, fp, indent=2)
    print("Wrote", json_filename)
