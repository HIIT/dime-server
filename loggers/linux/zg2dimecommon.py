#!/usr/bin/env python

import json
import hashlib
import requests

from zg2dimeglobals import config

# -----------------------------------------------------------------------

def to_json_sha1(payload):
    """Convert to JSON and return a SHA-1 digest."""     
    json_payload = json.dumps(payload)
    sha1 = hashlib.sha1()
    sha1.update(json_payload)
    return sha1.hexdigest()

# -----------------------------------------------------------------------

def str_to_sha1(json_payload):
    """Return a SHA-1 digest for a string."""     
    sha1 = hashlib.sha1()
    sha1.update(json_payload)
    return sha1.hexdigest()

# -----------------------------------------------------------------------

def json_dumps(obj):
    """Convert (serialize) to JSON."""
    return json.dumps(obj)

# -----------------------------------------------------------------------

def json_dump(obj, fn):
    """Save as JSON."""
    with open(fn, 'w') as fp: 
        json.dump(obj, fp)

# -----------------------------------------------------------------------

def json_load(fn):
    """Load JSON from file object."""
    with open(fn, 'r') as fp: 
        return json.load(fp)

# -----------------------------------------------------------------------

def json_loads(text):
    """Load JSON from string."""
    return json.loads(text)

# -----------------------------------------------------------------------

def ping_server():
    """Ping DiMe, returns boolean for success."""
    try:
        r = requests.post(config['server_url']+'/ping')
        #print r.text
    except requests.exceptions.ConnectionError:
        return False
    return True

# -----------------------------------------------------------------------

def post_json(payload):
    """HTTP POST JSON-format payload to DiMe."""
    headers = {'content-type': 'application/json'}
    return requests.post(config['server_url']+"/data/zgevent",
                         data=payload,
                         headers=headers,
                         auth=(config['username'],
                               config['password']))

# -----------------------------------------------------------------------


