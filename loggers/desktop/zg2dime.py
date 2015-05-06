#!/usr/bin/env python

import os.path
import sys
import subprocess
import requests
import urllib
import time

from gi.repository import GLib

from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import *

from zg2dimeglobals import config
import zg2dimeconf as conf
import zg2dimecommon as common
import chrome2dime
import zg2dimeind

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

def map_zg(zg):
    if zg.endswith("AccessEvent"):
        return config['nuao_usageevent']
    if zg.endswith("CreateEvent"):
        return config['nuao_modificationevent']
    if zg.endswith("ModifyEvent"):
        return config['nuao_modificationevent']

    return config['nuao_event']

# -----------------------------------------------------------------------

def send_event(event):
    """Send an event to DiMe."""
    filename = urllib.unquote(event.subjects[0].uri)
    print ("Starting to process " + filename + " on " + time.strftime("%c") +
               " with " + str(len(documents)) + " known documents")

    if common.blacklisted(filename, 'blacklist_zeitgeist'):
        return

    if filename.startswith('file://'):
        filename = filename[7:]

    payload = {'origin': config['hostname'],
               'actor':  map_actor(event.actor), 
               'type':   map_zg(event.interpretation),
               'start':  event.timestamp}

    document = {'uri':              event.subjects[0].uri,
                'type':             event.subjects[0].interpretation,
                'isStoredAs':       event.subjects[0].manifestation,
                'mimeType':         event.subjects[0].mimetype,
                'plainTextContent': event.subjects[0].text}

    document['id'] = common.to_json_sha1(document)
    payload['targettedResource'] = {}
    payload['targettedResource']['id'] = document['id']
    payload['id'] = common.to_json_sha1(payload)

    full_data = False
    if not document['id'] in documents:
        print "Not found in known documents, sending full data"
        documents.add(document['id'])
        full_data = True

    if payload['type'] == config['nuao_modificationevent']:
        print "This is a modify event, sending full data"
        full_data = True

    if full_data:
        if os.path.isfile(filename):
            document['storage'] = 'local'

            if document['mimeType'] == "" or document['mimeType'] == "unknown":
                document['mimeType'] = common.get_mimetype(filename)

            if (config.has_key('pdftotext_zeitgeist') and config['pdftotext_zeitgeist']
                and event.subjects[0].mimetype == 'application/pdf'):
                document['plainTextContent'] = common.pdf_to_text(filename)
            elif 'text/' in document['mimeType']:
                if document['type'] == config['nfo_document']:
                    document['type'] = config['nfo_textdocument']
                with open (filename, "r") as myfile:
                    document['plainTextContent'] = myfile.read()
        else:
            document['storage'] = 'deleted'

        if (config['maxtextlength_zg']>0 and
            len(document['plainTextContent'])>config['maxtextlength_zg']):
            document['plainTextContent'] = document['plainTextContent'][0:config['maxtextlength_zg']]

        payload['targettedResource'] = document.copy()

    json_payload = common.payload_to_json(payload)
    print "PAYLOAD:\n" + json_payload

    r = common.post_json(json_payload)
    print "RESPONSE:"
    if r is not None:
        r.text
    else:
        print "<None>"
    print "---------------------------------------------------------"

    if r.status_code != common.requests.codes.ok:
        print "Post to DiMe failed: error=[%s], message=[%s]" % (r.json()['error'],
                                                                 r.json()['message'])

    stats['zeitgeist']['events_sent'] = stats['zeitgeist']['events_sent'] + 1
    stats['zeitgeist']['data_sent'] = (stats['zeitgeist']['data_sent'] +
                                       len(json_payload))
    stats['zeitgeist']['latest'] = int(time.time())


# -----------------------------------------------------------------------

def on_insert(time_range, events):
    """Process an insert to Zeitgeist: send either 1 or n events to DiMe."""
    if not hasattr(on_insert, "last_ping_ok"):
        on_insert.last_ping_ok = True

    ping_ok = common.ping_server()
    if ping_ok:
        if on_insert.last_ping_ok:
            send_event(events[0])
        else:
            zeitgeist.find_events_for_template(template, on_events_received,
                                               num_events=config['nevents'])
    else:
        print "No connection to DiMe server on " + time.strftime("%c")

    on_insert.last_ping_ok = ping_ok

# -----------------------------------------------------------------------

def on_events_received(events):
    """Send n latest events to DiMe."""
    if common.ping_server():
        for event in events:
            send_event(event)
        print "Processed %d entries" % len(events)
    else:
        print "No connection to DiMe server on " + time.strftime("%c")

# -----------------------------------------------------------------------

def on_delete(time_range, event_ids):
    """For completeness, not used."""
    print event_ids

# -----------------------------------------------------------------------

def update_ind():
    """Update the data for the Unity menubar indicator."""
    if config['use_chrome']:
        stats['chrome']['events_sent'] = chromelogger.events_sent
        stats['chrome']['data_sent'] = chromelogger.data_sent
        stats['chrome']['latest'] = chromelogger.latest
    if config['use_chromium']:
        stats['chromium']['events_sent'] = chromiumlogger.events_sent
        stats['chromium']['data_sent'] = chromiumlogger.data_sent
        stats['chromium']['latest'] = chromiumlogger.latest
    if config['use_firefox']:
        stats['firefox']['events_sent'] = firefoxlogger.events_sent
        stats['firefox']['data_sent'] = firefoxlogger.data_sent
        stats['firefox']['latest'] = firefoxlogger.latest

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

    pingstring = "Pinging DiMe server at location: " + config['server_url'] + " : "
    if common.ping_server():
        print pingstring + "OK"
    else:
        print pingstring + "FAILED"

    documents = set()

    actors = config['actors'].copy()

    stats = {'zeitgeist': {'events_sent': 0, 'data_sent': 0, 'latest': 0},
             'chrome': {'events_sent': 0, 'data_sent': 0, 'latest': 0},
             'chromium': {'events_sent': 0, 'data_sent': 0, 'latest': 0},
             'firefox': {'events_sent': 0, 'data_sent': 0, 'latest': 0}}

    if config['use_zeitgeist']:

        zeitgeist = ZeitgeistClient()

        template = Event.new_for_values(subject_interpretation=Interpretation.DOCUMENT)

        zeitgeist.find_events_for_template(template, on_events_received, num_events=config['nevents'])
        zeitgeist.install_monitor(TimeRange.always(), [template], on_insert, on_delete)

        try:
            uuid = subprocess.check_output(config['uuid_command'], shell=True)
            uuid = uuid.rstrip()
        except subprocess.CalledProcessError:
            uuid = 'unknown'

    try:
        if config['use_indicator']:
            ind = zg2dimeind.Indicator()
            GLib.timeout_add(config['interval_indicator']*1000, update_ind)

        if config['use_chrome']:
            chromelogger = chrome2dime.Browserlogger('chrome')
            GLib.timeout_add(config['interval_chrome']*1000, chromelogger.run)

        if config['use_chromium']:
            chromiumlogger = chrome2dime.Browserlogger('chromium')
            GLib.timeout_add(config['interval_chromium']*1000, chromiumlogger.run)

        if config['use_firefox']:
            firefoxlogger = chrome2dime.Browserlogger('firefox')
            GLib.timeout_add(config['interval_firefox']*1000, firefoxlogger.run)

        GLib.MainLoop().run()

    except KeyboardInterrupt:
        print("Exiting")

# -----------------------------------------------------------------------
