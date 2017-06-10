#!/usr/bin/env python3

import datetime
import dime
import json
import requests
import time
import sys

from numpy.random import choice


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

    def post(self, url):
        print("POST", url)
        r = requests.post(self.url + url, headers={'content-type': 'application/json'},
                          auth=(self.username, self.password), timeout=10)
        return r

    def get(self, url):
        print("GET", url)
        r = requests.get(self.url + url, headers={'content-type': 'application/json'},
                          auth=(self.username, self.password), timeout=10)
        return r

#------------------------------------------------------------------------------

dime = DiMeConnection('http://localhost:8081/api', 'demouser')

req = '/data/events?orderBy=start&desc=false'
events = dime.get(req).json()

for e in events:
    start = datetime.datetime.fromtimestamp(e['start']/1000.0)
    end = datetime.datetime.fromtimestamp(e['end']/1000.0)
    print(e['@type'], start, end)
