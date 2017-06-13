#!/usr/bin/env python3

import datetime
import dime
import json
import requests
import time

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

def remove_fields(res, *fields):
    for f in fields:
        if f in res:
            del res[f]
#------------------------------------------------------------------------------

dime = DiMeConnection('http://localhost:8081/api', 'mvsjober')

day = "2017-06-09"
req = '/data/events?after={0}T00:00:00&before={0}T23:59:59&orderBy=start&desc=false'.format(day)
print(req)
events = dime.get(req).json()

activities = ["Re:Know", "Admin", "Focus area", "Misc"]

act_events = []
act_start = None
prev_end = None

for e in events:
    start = e['start']
    end = e['end']

    if act_start is None:
        act_start = start

    desc = ''
    if 'targettedResource' in e:
        res = e['targettedResource']
        if 'title' in res:
            desc = res['title']

        if 'plainTextContent' in res and len(res['plainTextContent']) > 0:
            res['plainTextContent'] = '[removed]'

        if 'uri' in res and len(res['uri']) > 0:
            res['plainTextContent'] = 'http://example.com'
            
        remove_fields(res, 'frequentTerms', 'title', 'tags', 'html', 'hyperLinks', 'imgURLs', 'metaTags', 'id', 'user', 'profileIds', 'timeCreated', 'timeModified')
        
    if prev_end is not None:
        diff = start-prev_end
        if diff > 15*60*1000: # five minutes
            act_events.append({
                '@type':    'ActivityEvent',
                'actor':    'generate_activities.py',
                'origin':   'localhost',
                'type':     'http://www.hiit.fi/ontologies/dime/#ActivityEvent',
                'start':    act_start,
                'end':      prev_end,
                'activity': choice(activities, 1, p=[0.5, 0.2, 0.2, 0.1])[0]
            })
            act_start = start
            

    print(e['@type'], ':', start, '->', end)
    print(desc)

    prev_end = end
    del e['id']
    del e['user']
    del e['timeCreated']
    del e['timeModified']
    del e['profileIds']

with open('demo_activities.json', 'w') as fp:
    json.dump(act_events, fp, indent=2)
    
with open('demo_events.json', 'w') as fp:
    json.dump(events, fp, indent=2)
