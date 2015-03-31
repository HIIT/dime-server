#!/usr/bin/env python

import os.path
import sys
import subprocess
import requests
import json
import hashlib
import urllib
import time

from gi.repository import GLib
from ConfigParser import SafeConfigParser
from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import *

from zg2dimeglobals import config
import zg2dimeconf as conf
import chrome2dime

# -----------------------------------------------------------------------

def json_to_sha1(payload):
    json_payload = json.dumps(payload)
    sha1 = hashlib.sha1()
    sha1.update(json_payload)
    return sha1.hexdigest()

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

    payload = {'origin':                 config['hostname'],
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
 
    payload['subject']['id'] = json_to_sha1(payload['subject'])
    payload['id'] = json_to_sha1(payload)
    json_payload = json.dumps(payload)
    print(json_payload)

    r = requests.post(config['server_url'], data=json_payload, headers=headers)
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

if __name__ == '__main__':

    print "Starting the zg2dime.py logger on " + time.strftime("%c")

    conf.configure()

    if len(sys.argv)>1:
        if sys.argv[-1] == 'debug':
            config['server_url'] = 'http://httpbin.org/post'
            config['nevents'] = 1
        elif sys.argv[-1] == 'all':
            config['nevents'] = 1000

    print "DiMe server location: " + config['server_url']

    actors = config['actors'].copy()

    if config['use_zeitgeist']:

        zeitgeist = ZeitgeistClient()

        template = Event.new_for_values(subject_interpretation=Interpretation.DOCUMENT)

        zeitgeist.find_events_for_template(template, on_events_received, num_events=config['nevents'])
        zeitgeist.install_monitor(TimeRange.always(), [template], on_insert, on_delete)

    uuid = subprocess.check_output("udevadm info -q all -n /dev/sda1 | grep ID_FS_UUID= | sed 's:^.*=::'", shell=True)
    uuid = uuid.rstrip()

    try:
        if config['use_chrome']:
            c2d = chrome2dime.Browserlogger('chrome')
            GLib.timeout_add(config['interval_chrome']*1000, c2d.run)

        if config['use_chromium']:
            c2d = chrome2dime.Browserlogger('chromium')
            GLib.timeout_add(config['interval_chromium']*1000, c2d.run)

        if config['use_firefox']:
            c2d = chrome2dime.Browserlogger('firefox')
            GLib.timeout_add(config['interval_firefox']*1000, c2d.run)

        GLib.MainLoop().run()

    except KeyboardInterrupt:
        print("Exiting")

# -----------------------------------------------------------------------
