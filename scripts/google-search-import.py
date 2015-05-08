#!/usr/bin/env python3

import requests
import sys
import socket
import time
import json
import os, os.path

#------------------------------------------------------------------------------

server_url = 'http://localhost:8080/api'
server_username = 'testuser'
server_password = 'testuser123'

#------------------------------------------------------------------------------

def ping():
    r = requests.post(server_url + '/ping')

    if r.status_code != requests.codes.ok:
        print('No connection to DiMe server!')
        return False
    return True

#------------------------------------------------------------------------------

def post_item(item, endpoint):
    global server_url, server_username, server_password

    # Fill in all the standard event fields
    item['actor']  = 'google-search-import.py'
    item['origin'] = socket.gethostbyaddr(socket.gethostname())[0]
    item['type']   = 'http://www.hiit.fi/ontologies/dime/#GoogleSearchEvent'

    requests.post(server_url + endpoint,
                  data=json.dumps(item),
                  headers={'content-type': 'application/json'},
                  auth=(server_username, server_password),
                  timeout=10)

#------------------------------------------------------------------------------

def process_file(filename):
    with open(filename, 'r') as fp:
        events = json.load(fp)['event']
        for event in events:
            query = event['query']
            timestamp = int(query['id'][0]['timestamp_usec'])

            item = {}
            item['query'] = query['query_text']
            item['start']  = time.strftime("%Y-%m-%dT%H:%M:%S%z",
                                           time.localtime(timestamp/1000000))

            print('QUERY: "{}" at {}'.format(item['query'], item['start']))

            post_item(item, '/data/searchevent')
    
#------------------------------------------------------------------------------

if not ping():
    sys.exit(1)

search_path = sys.argv[1]
for root, _, files in os.walk(search_path):
    for f in files:
        if f.endswith('.json'):
            process_file(os.path.join(root, f))
