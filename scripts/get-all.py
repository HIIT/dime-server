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

json_filename = 'dime-elements.json'

#------------------------------------------------------------------------------

# ping server (not needed, but fun to do :-)
r = requests.post(server_url + '/ping')

if r.status_code != requests.codes.ok:
    print('No connection to DiMe server!')
    sys.exit(1)

params = ""
if len(sys.argv) > 1:
    params = "?" + quote_plus("&".join(sys.argv[1:]), safe='&=')

get_url = server_url + '/data/informationelements' + params
print("GET", get_url)

r = requests.get(get_url,
                 headers={'content-type': 'application/json'},
                 auth=(server_username, server_password),
                 timeout=10)

if r.status_code > 299:
    print('HTTP Error:', r.status_code)
    sys.exit(1)

j = r.json()

print("Got {} InformationElements from DiMe.".format(len(j)), file=sys.stderr)

with open(json_filename, 'w') as fp:
    json.dump(j, fp, indent=2)
    print("Wrote", json_filename)

# for elem in j:
#     print(elem['id'])
