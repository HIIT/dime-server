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

from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import *

from zg2dimeglobals import config
import zg2dimeconf as conf
import chrome2dime
import zg2dimeind

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
    #print filename
    for path in _paths:
        for thispath, dirs, files in os.walk(os.path.join(path, 'applications')):
            if filename not in files:
                continue
            fullname = os.path.join(thispath, filename)
            #print fullname
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

    actors[actor] = conf.parse_desktop_file(desktop_file, actor)
    return actors[actor]

# -----------------------------------------------------------------------

def blacklisted(fn):
    if not config.has_key('blacklist_zeitgeist'):
        return False
    for bl_substr in config['blacklist_zeitgeist']:
        if bl_substr in fn:
            print "File %s matches a blacklist item [%s], skipping" % (fn, bl_substr) 
            return True
    return False

# -----------------------------------------------------------------------

def send_event(event):

    filename = urllib.unquote(event.subjects[0].uri)
    print ("Starting to process " + filename + " on " + time.strftime("%c") + 
               " with " + str(len(subjects)) + " known subjects")

    if blacklisted(filename):
        return

    if filename.startswith('file://'):
        filename = filename[7:]

    payload = {'origin':                 config['hostname'],
               'actor':                  map_actor(event.actor), 
               'interpretation':         event.interpretation,
               'manifestation':          event.manifestation,               
               'timestamp':              event.timestamp}

    subject = {'uri':            event.subjects[0].uri,
               'interpretation': event.subjects[0].interpretation,
               'manifestation':  event.subjects[0].manifestation,
               'mimetype':       event.subjects[0].mimetype}

    subject['id'] = json_to_sha1(subject)
    payload['subject'] = {}
    payload['subject']['id'] = subject['id']
    payload['id'] = json_to_sha1(payload)

    if not subject['id'] in subjects:
        print "Not found in known subjects, sending full data"
        subjects.add(subject['id'])
 
        if os.path.isfile(filename):
            subject['storage'] = uuid
            if config['pdftotext'] and event.subjects[0].mimetype == 'application/pdf':
                print "Detected as PDF, converting to text"
                shell_command = config['pdftotext_command'] % filename
                try:
                    subject['text'] = subprocess.check_output(shell_command, shell=True)
                except subprocess.CalledProcessError:
                    pass
            elif 'text/' in event.subjects[0].mimetype:
                with open (filename, "r") as myfile:
                    subject['text'] = myfile.read()
        else:
            subject['storage'] = 'deleted'

        if config['maxtextlength_zg']>0 and len(subject['text'])>config['maxtextlength_zg']:
            subject['text'] = subject['text'][0:config['maxtextlength_zg']]

        payload['subject'] = subject.copy()

    json_payload = json.dumps(payload)
    print(json_payload)

    headers = {'content-type': 'application/json'}
    r = requests.post(config['server_url'], data=json_payload, headers=headers)
    stats['nevents'] = stats['nevents'] + 1 
    stats['data_sent'] = stats['data_sent'] + len(json_payload)
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

def update_ind():
    ind.update(stats)
    return True

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

    subjects = set()

    actors = config['actors'].copy()

    stats = { 'nevents': 0,
              'data_sent': 0,
              'last_event': None }

    if config['use_zeitgeist']:

        zeitgeist = ZeitgeistClient()

        template = Event.new_for_values(subject_interpretation=Interpretation.DOCUMENT)

        zeitgeist.find_events_for_template(template, on_events_received, num_events=config['nevents'])
        zeitgeist.install_monitor(TimeRange.always(), [template], on_insert, on_delete)

    uuid = subprocess.check_output("udevadm info -q all -n /dev/sda1 | grep ID_FS_UUID= | sed 's:^.*=::'", shell=True)
    uuid = uuid.rstrip()

    try:
        if config['use_indicator']:
            ind = zg2dimeind.Indicator()
            GLib.timeout_add(config['interval_indicator']*1000, update_ind)

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
