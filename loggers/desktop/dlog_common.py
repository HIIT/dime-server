#!/usr/bin/env python

import json
import hashlib
import requests
import subprocess
import urllib
import tempfile
from BeautifulSoup import BeautifulSoup

from dlog_globals import config

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

def _payload_to_json(payload, alt_text):
    try:
        return json.dumps(payload)
    except UnicodeDecodeError:
        pass

    try:
        payload['targettedResource']['plainTextContent'] = payload['targettedResource']['plainTextContent'].decode('utf-8', 'ignore')
        return json.dumps(payload)
    except UnicodeDecodeError:
        pass
    
    if alt_text is not None:
        payload['targettedResource']['plainTextContent'] = alt_text
        try:
            return json.dumps(payload)
        except UnicodeDecodeError:
            pass

    payload['targettedResource']['plainTextContent'] = ''
    try:
        return json.dumps(payload)
    except UnicodeDecodeError:
        pass

    return ''

def payload_to_json(payload, alt_text=None):
    json_payload = _payload_to_json(payload, alt_text)
    print "PAYLOAD: " + str(type(json_payload))
    print json_payload
    return json_payload

# -----------------------------------------------------------------------

def json_dumps(obj, **keywords):
    """Convert (serialize) to JSON."""
    try:
        return json.dumps(obj, **keywords)
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

def post_json(payload, event="desktopevent"):
    """HTTP POST JSON-format payload to DiMe."""
    headers = {'content-type': 'application/json'}
    try:
        return requests.post(config['server_url']+"/data/event",
                             data=payload,
                             headers=headers,
                             auth=(config['username'],
                                   config['password']),
                             timeout=config['server_timeout'])
    except requests.exceptions.RequestException:
        return None        

# -----------------------------------------------------------------------

def post_payload(payload, event="desktopevent"):
    """Send payload to DiMe and check response.

    Use this if DiMe response is not needed for anything else.
    """
    res = _post_payload(payload, event)
    print "---###---###---###---###---###---###---###---###---###---###---"
    print ""
    return res

def _post_payload(payload, event="desktopevent"):
    r = post_json(payload, event)
    return check_response(r)

# -----------------------------------------------------------------------

def check_response(r):
    """Check response from DiMe, returns boolean."""
    print "RESPONSE:"
    if r is None:
        print "<None>"
        return False

    try: 
        print r.text.encode('utf-8')
    except UnicodeEncodeError:
        print "<UnicodeEncodeError>"

    if r.status_code != requests.codes.ok:
        print ("Post to DiMe failed: "
               "error=[%s], message=[%s]") % (r.json()['error'],
                                              r.json()['message'])
        return False
        
    return True

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

    temp = tempfile.NamedTemporaryFile()
    try:
      urllib.urlretrieve(uri, temp.name)
    except IOError:
      return "", ""

    title = ""
    try:
        soup = BeautifulSoup(temp)
        if soup.title is not None:
            title = soup.title.string
    except UnicodeEncodeError:
        pass

    #print 'Page title: ', title

    lynx_command = config['fulltext_command'] % temp.name
    try:
        text = subprocess.check_output(lynx_command, shell=True)
    except subprocess.CalledProcessError:
        print ("WARNING: uri_to_text(): CalledProcessError for: "+
               lynx_command)
        text = alt_text
    temp.close()

    if (config['maxtextlength_web']>0 and
        len(text)>config['maxtextlength_web']):
        text = text[0:config['maxtextlength_web']]

    return text, title

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

def o(entry):
    """Safe ontology item access, up to two levels."""
    if config.has_key(entry):
        oitem = config[entry]
        if config.has_key(oitem):
            return config[oitem]
        return oitem
    return '[unknown ontology entry: %s]' % entry

# -----------------------------------------------------------------------

def o_match_replace(target, o_from, o_to):
    """Replace target with o_to if it matches o_from."""
    o_from = o(o_from)
    idxhash = o_from.rfind('#')
    if idxhash<0:
        return target
    if o_from[idxhash:] in target:
        return o(o_to)
    return target

# -----------------------------------------------------------------------
# -----------------------------------------------------------------------

