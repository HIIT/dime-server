#!/usr/bin/env python3

import requests
import sys
import socket
import time
import json

#------------------------------------------------------------------------------

server_url = 'http://localhost:8080/api'
server_username = 'testuser'
server_password = 'testuser123'

json_filename = 'dime-elements.json'

#------------------------------------------------------------------------------

# ping server (not needed, but fun to do :-)
r = requests.post(server_url + '/ping')

if r.status_code != requests.codes.ok:
    print('No connection to DiMe server!')
    sys.exit(1)

r = requests.get(server_url + '/data/informationelements',
                 headers={'content-type': 'application/json'},
                 auth=(server_username, server_password),
                 timeout=10)

if r.status_code != requests.codes.ok:
    print('HTTP Error:', r.status_code)
    sys.exit(1)

j = r.json()

print("Got {} InformationElements from DiMe.".format(len(j)), file=sys.stderr)

with open(json_filename, 'w') as fp:
    json.dump(j, fp)
    print("Wrote", json_filename)

# field = 'plainTextContent'
# for elem in j:
#     if field in elem:
#         print('"'+elem[field][:70]+'"')
