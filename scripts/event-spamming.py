#!/usr/bin/env python3

import threading
import time
import requests
import socket
import json

#------------------------------------------------------------------------------

server_url = 'http://localhost:8080/api'
server_username = 'testuser'
server_password = 'testuser123'

#------------------------------------------------------------------------------

class PostingThread(threading.Thread):
    def __init__(self, payload):
        threading.Thread.__init__(self)
        self.payload = payload

    def run(self):
        print('Sleeping 1 sec ...')
        time.sleep(1)
        r = requests.post(server_url + '/data/event',
                          data=json.dumps(self.payload),
                          headers={'content-type': 'application/json'},
                          auth=(server_username, server_password),
                          timeout=10)

# Set all the standard event fields
payload = {
    '@type':    'SearchEvent',
    'actor':    'event-spamming.py',
    'origin':   socket.gethostbyaddr(socket.gethostname())[0],
    'type':     'http://www.hiit.fi/ontologies/dime/#ExampleSearchEvent',
    'start':    time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
    'appId':    'Oocheth5muQuu8jathah3EewTheiReo0veryrandomindeed'
}

threads = []
for i in range(1):
    p = payload.copy()
    p['query'] = 'dummy search new {}'.format(i)
    threads.append(PostingThread(p))

for t in threads:
    t.start()

print('Sleeping 5 secs ...')
time.sleep(5)
r = requests.get(server_url + '/data/events?appid=' + payload['appId'],
                 headers={'content-type': 'application/json'},
                 auth=(server_username, server_password),
                 timeout=10)

print('DiMe returns:', json.dumps(r.json(), indent=2))
print('Items: ', len(r.json()))
