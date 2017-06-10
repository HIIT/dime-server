#!/usr/bin/env python3

import dime
import json
import sys
import requests

#------------------------------------------------------------------------------

class DiMeConnection:
    def __init__(self, url, username, uid=None):
        self.url = url
        self.username = username
        self.uid = uid
        self.password = dime.password(self.username)

    def ping(self, verbose=True):
        r = requests.post(self.url + '/ping')

        if r.status_code != requests.codes.ok:
            if verbose:
                print('No connection to DiMe server!', file=sys.stderr)
            return None
        else:
            if verbose:
                print('Connected to DiMe: {} @ {}, version {}.'.
                      format(self.username, self.url, r.json()['version']),
                      file=sys.stderr)
            return r.json()

    def post(self, url, data=None):
        print("POST", url)
        r = requests.post(self.url + url, headers={'content-type': 'application/json'},
                          data=data, auth=(self.username, self.password), timeout=10)
        return r

    def get(self, url):
        print("GET", url)
        r = requests.get(self.url + url, headers={'content-type': 'application/json'},
                          auth=(self.username, self.password), timeout=10)
        return r

#------------------------------------------------------------------------------

with open(sys.argv[1], 'r') as fp:
    data = json.loads(fp.read())
    dime = DiMeConnection('http://localhost:8081/api', 'demouser')
    res=dime.post("/data/events", data=json.dumps(data))
    if res.status_code == 200:
        print("Uploaded {} events.".format(len(res.json())))
    else:
        print(res.text)

