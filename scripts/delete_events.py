#!/usr/bin/env python3

import requests
import sys
import socket
import time
import json

#------------------------------------------------------------------------------

server_url = 'http://localhost:8080/api'
server_username = 'mvsjober'
server_password = 'tBaiTwIIAjB+YGg24F59zH9p'

#------------------------------------------------------------------------------

r = requests.post(server_url + '/ping')

if r.status_code != requests.codes.ok:
    print('No connection to DiMe server!')
    sys.exit(1)

r = requests.get(server_url + '/data/events?' + sys.argv[1],
                  headers={'content-type': 'application/json'},
                  auth=(server_username, server_password),
                  timeout=10)

rj = r.json()

if len(rj) == 0:
    print('No events found.')
    sys.exit(1)

print('These would be deleted:', json.dumps(rj, indent=2))

input('Press enter to continue (or Ctrl-C to cancel)')


for item in rj:
    item_id = item['id']
    r = requests.delete(server_url + '/data/event/' + str(item_id),
                        headers={'content-type': 'application/json'},
                        auth=(server_username, server_password),
                        timeout=10)

    if r.status_code == requests.codes.ok:
        print('Successfully deleted event', item_id)
    else:
        print('Error deleting event', item_id, r)
