#!/usr/bin/env python

import json
import hashlib

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

