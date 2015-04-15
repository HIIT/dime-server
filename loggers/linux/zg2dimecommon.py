#!/usr/bin/env python

import json
import hashlib
import requests

from zg2dimeglobals import config

# -----------------------------------------------------------------------

def json_to_sha1(payload):
    json_payload = json.dumps(payload)
    sha1 = hashlib.sha1()
    sha1.update(json_payload)
    return sha1.hexdigest()

# -----------------------------------------------------------------------

def json_dumps(text):
    return json.dumps(text)

# -----------------------------------------------------------------------

def ping_server():
    try:
        r = requests.post(config['server_url']+'/ping')
        #print r.text
    except requests.exceptions.ConnectionError:
        return False
    return True

# -----------------------------------------------------------------------

def post_json(payload):
    headers = {'content-type': 'application/json'}
    return requests.post(config['server_url']+"/data/zgevent",
                         data=payload,
                         headers=headers,
                         auth=(config['username'],
                               config['password']))

# -----------------------------------------------------------------------


