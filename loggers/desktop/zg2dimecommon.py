#!/usr/bin/env python

import json
import hashlib
import requests
import subprocess

from zg2dimeglobals import config

# -----------------------------------------------------------------------

def to_json_sha1(payload):
    """Convert to JSON and return a SHA-1 digest."""     
    json_payload = json_dumps(payload)
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

def payload_to_json(payload, alt_text=None):
    try:
        return json.dumps(payload)
    except UnicodeDecodeError:
        pass

    try:
        payload['subject']['text'] = payload['subject']['text'].decode('utf-8', 'ignore')
        return json.dumps(payload)
    except UnicodeDecodeError:
        pass
    
    if alt_text is not None:
        payload['subject']['text'] = alt_text
        try:
            return json.dumps(payload)
        except UnicodeDecodeError:
            pass

    payload['subject']['text'] = ''
    try:
        return json.dumps(payload)
    except UnicodeDecodeError:
        pass

    return ''

# -----------------------------------------------------------------------

def json_dumps(obj):
    """Convert (serialize) to JSON."""
    try:
        return json.dumps(obj)
    except UnicodeDecodeError:
        return ''

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

def ping_server(verbose=False):
    """Ping DiMe, returns boolean for success."""
    try:
        r = requests.post(config['server_url']+'/ping',
                          timeout=config['server_timeout'])
        #print r.text
    except requests.exceptions.RequestException:
        return False
    if verbose:
        print r.text
    if r.status_code != requests.codes.ok:
        return False
    if r.json()['message'] != 'pong':
        return False
    return True

# -----------------------------------------------------------------------

def post_json(payload):
    """HTTP POST JSON-format payload to DiMe."""
    headers = {'content-type': 'application/json'}
    try:
        return requests.post(config['server_url']+"/data/zgevent",
                             data=payload,
                             headers=headers,
                             auth=(config['username'],
                                   config['password']),
                             timeout=config['server_timeout'])
    except requests.exceptions.RequestException:
        return None        

# -----------------------------------------------------------------------

def uri_info(uri):
    """HTTP HEAD request for uri."""
    if uri.startswith('file://'):
        return ('local', get_mimetype(uri[7:]))

    try:
        r = requests.head(uri)
    except requests.exceptions.RequestException:
        return ('deleted', 'unknown')

    if r.status_code != requests.codes.ok:
        return ('deleted', 'unknown')

    return ('net', r.headers['content-type'])

# -----------------------------------------------------------------------

def blacklisted(item, blacklist):
    """Check if item matches (has as substring) a blacklisted string."""
    if not config.has_key(blacklist):
        return False
    for bl_substr in config[blacklist]:
        if bl_substr in item:
            print "Item [%s] matches a blacklist item [%s], skipping" % \
                   (item, bl_substr)
            return True
    return False

# -----------------------------------------------------------------------

def pdf_to_text(fn):
    print "Detected as PDF, converting to text"
    shell_command = config['pdftotext_command'] % fn
    try:
        return subprocess.check_output(shell_command, shell=True)
    except subprocess.CalledProcessError:
        return None

# -----------------------------------------------------------------------

def uri_to_text(uri, alt_text=''):
    lynx_command = config['fulltext_command'] % uri
    try:
        text = subprocess.check_output(lynx_command, shell=True)
    except subprocess.CalledProcessError:
        text = alt_text
    if (config['maxtextlength_web']>0 and
        len(text)>config['maxtextlength_web']):
        text = text[0:config['maxtextlength_web']]
    return text

# -----------------------------------------------------------------------

def get_mimetype(fn):
    shell_command = config['mimetype_command'] % fn
    try:
        mimetype = subprocess.check_output(shell_command,
                                           shell=True)
        return mimetype.rstrip()
    except subprocess.CalledProcessError:
        return "unknown"

# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

