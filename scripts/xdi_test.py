#!/usr/bin/env python3

import requests
import sys
# import socket
# import time
import json
import dime
import urllib

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

dime_a = DiMeConnection('http://localhost:8081/api', 'mvsjober')

dime_b = DiMeConnection('http://localhost:8082/api', 'bob',
                        '=!:did:sov:TJrPGZ3e6uWC4xmSZrJPar')

#------------------------------------------------------------------------------

if not dime_a.ping() or not dime_b.ping():
    sys.exit(1)

dime_a.post('/requests/send/' + dime_b.uid)

reqs = dime_b.get('/requests/view').json()
print("Current requests (b):")
print(json.dumps(reqs, indent=2))

# dime_b.post('/requests/delete?address=' + reqs[0]['address'])
# dime_b.post('/requests/approve/' + reqs[0]['address'])

# reqs = dime_b.get('/requests/view').json()
# print("Current requests (b) (AFTER):")
# print(reqs)


# contracts_a = dime_a.get('/linkcontracts/view').json()
# print("Contracts (a)")
# print(contracts_a)

# contracts_b = dime_b.get('/linkcontracts/view').json()
# print("Contracts (b)")
# print(contracts_b)

# if len(contracts_b) > 0:
#     address_quoted = urllib.parse.quote_plus(contracts_b[0]['address'])
#     #ret = dime_b.post('/linkcontracts/delete?address=' + address_quoted)

#     # contracts_b = dime_b.get('/linkcontracts/view').json()
#     # print("Contracts (b) (AFTER)")
#     # print(contracts_b)


data = dime_a.get('/linkcontracts/data/' + dime_b.uid)
print(json.dumps(data.json(), indent=2))

