#!/usr/bin/env python

import os.path
import sys
import subprocess
import socket
import requests
import json
import hashlib
import urllib
import time

from gi.repository import GLib
from ConfigParser import SafeConfigParser
from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import *

# -----------------------------------------------------------------------

def process_config_item(parser, oldval, section, option):
    if parser.has_section(section) and parser.has_option(section, option):
        return parser.get(section, option)
    return oldval

# -----------------------------------------------------------------------

def process_config():
    global config_server_url, config_nevents

    print "Processing config file: " + config_file

    if not os.path.isfile(config_file):
        print "ERROR: Config file not found"
        return False

    config_fp = open(config_file)     
    parser = SafeConfigParser()    
    parser.readfp(config_fp)

    config_server_url = process_config_item(parser, config_server_url, 'DiMe', 'server_url')
    config_nevents = process_config_item(parser, config_nevents, 'DiMe', 'nevents')

    other_actors = ''
    other_actors = process_config_item(parser, other_actors, 'Zeitgeist', 'other_actors')
    if other_actors:
        print other_actors
        oa_list = other_actors.split(';')
        for oa in oa_list:
            oa = oa.strip()
            print oa
            oa_kv = oa.split('->')            
            if len(oa_kv)==2:
                print oa_kv[0] +" " + oa_kv[1]
                config_actors[oa_kv[0]]=oa_kv[1]                
            else:
                print "ERROR: Unable to parse Zeitgeist/other_actors: " + oa

    return True

# -----------------------------------------------------------------------

def json_to_md5(payload):
    json_payload = json.dumps(payload)
    md5 = hashlib.md5()
    md5.update(json_payload)
    return md5.hexdigest()

# -----------------------------------------------------------------------
 
def _get_app_paths():
    paths = os.environ.get('XDG_DATA_HOME', 
        os.path.expanduser('~/.local/share/')).split(os.path.pathsep)
    paths.extend(os.environ.get('XDG_DATA_DIRS', 
        '/usr/local/share/:/usr/share/').split(os.path.pathsep))
    return paths

# -----------------------------------------------------------------------

def locate_desktop_file(filename, _paths=_get_app_paths()):
    print filename
    for path in _paths:
        for thispath, dirs, files in os.walk(os.path.join(path, 'applications')):
            if filename not in files:
                continue
            fullname = os.path.join(thispath, filename)
            print fullname
            return fullname
    else:
        raise IOError

# -----------------------------------------------------------------------

def map_actor(actor):
    if actor.startswith('application://'):
        actor = actor[14:]
    if actors.has_key(actor):
        return actors[actor]
    try:
        desktop_file = locate_desktop_file(actor)
    except IOError:
        actors[actor] = actor
        return actors[actor]
    parser = SafeConfigParser()
    parser.read(desktop_file)
    if parser.has_section('Desktop Entry') and parser.has_option('Desktop Entry', 'Name'):
        actors[actor] = parser.get('Desktop Entry', 'Name')
    else:
        actors[actor] = actor
    return actors[actor]

# -----------------------------------------------------------------------

def send_event(event):

    storage = 'deleted'
    text = ''
    filename = urllib.unquote(event.subjects[0].uri)
    if filename.startswith('file://'):
        filename = filename[7:]
    print filename
    if os.path.isfile(filename):
        storage = uuid
        if event.subjects[0].mimetype == 'application/pdf':
            shell_command = 'pdftotext "%s" - | head -20 | tr "\n" " " | fmt | head' % filename
            text = subprocess.check_output(shell_command, shell=True)
            text = text.rstrip()
        elif 'text/' in event.subjects[0].mimetype:
            shell_command = 'head -20 "%s" | tr "\n" " " | fmt | head' % filename
            text = subprocess.check_output(shell_command, shell=True)
            text = text.rstrip()

    payload = {'origin':                 hostname,
               'actor':                  map_actor(event.actor), 
               'interpretation':         event.interpretation,
               'manifestation':          event.manifestation,               
               'timestamp':              event.timestamp,
               'subject': {
                   'uri':            event.subjects[0].uri,
                   'interpretation': event.subjects[0].interpretation,
                   'manifestation':  event.subjects[0].manifestation,
                   'mimetype':       event.subjects[0].mimetype,
                   'storage':        storage,
                   'text':           text}
               }

    headers = {'content-type': 'application/json'}
 
    payload['subject']['id'] = json_to_md5(payload['subject'])
    payload['id'] = json_to_md5(payload)
    json_payload = json.dumps(payload)
    print(json_payload)

    r = requests.post(config_server_url, data=json_payload, headers=headers)
    print(r.text)
    print "---------------------------------------------------------"

# -----------------------------------------------------------------------

def on_insert(time_range, events):
    send_event(events[0])

# -----------------------------------------------------------------------

def on_events_received(events):
    for event in events:
        send_event(event)

# -----------------------------------------------------------------------

def on_delete(time_range, event_ids):
    print event_ids

# -----------------------------------------------------------------------

def foo():
    print "foo"
    return True

# -----------------------------------------------------------------------

print "Starting the zg2dime.py logger on " + time.strftime("%c")

config_file = "zg2dime.ini"
config_nevents = 10
config_server_url = ''
config_actors = {}

process_config()

if len(sys.argv)>1:
    if sys.argv[-1] == 'debug':
        config_server_url = 'http://httpbin.org/post'
        config_nevents = 1
    elif sys.argv[-1] == 'all':
        config_nevents = 1000

print "DiMe server location: " + config_server_url

actors = config_actors

zeitgeist = ZeitgeistClient()
 
template = Event.new_for_values(subject_interpretation=Interpretation.DOCUMENT)

zeitgeist.find_events_for_template(template, on_events_received, num_events=config_nevents)
zeitgeist.install_monitor(TimeRange.always(), [template], on_insert, on_delete)

hostname = socket.gethostbyaddr(socket.gethostname())[0]

uuid = subprocess.check_output("udevadm info -q all -n /dev/sda1 | grep ID_FS_UUID= | sed 's:^.*=::'", shell=True)
uuid = uuid.rstrip()

# -----------------------------------------------------------------------

if __name__ == '__main__':
    try:
        GLib.timeout_add(60*1000, foo)
        GLib.MainLoop().run()
    except KeyboardInterrupt:
        print("Exiting")

# -----------------------------------------------------------------------
