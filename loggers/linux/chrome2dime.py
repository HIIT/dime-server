#!/usr/bin/env python

import os.path
import sys
import shutil
import socket
import subprocess
import requests
import json
import hashlib
import sqlite3
import time

from zg2dimeglobals import config
import zg2dimeconf as conf

# -----------------------------------------------------------------------

class Browserlogger:

    def __init__(self, name):
        self.name = name
        self.debug = False
        self.old_history_file_sha1 = ''
        self.events = set()
        self.subjects = set()
        self.events_sent = 0
        self.data_sent = 0
        self.latest = 0

# -----------------------------------------------------------------------

    def json_to_sha1(self, payload):
        json_payload = json.dumps(payload)
        sha1 = hashlib.sha1()
        sha1.update(json_payload)
        return sha1.hexdigest()

# -----------------------------------------------------------------------

    def file_to_sha1(self, fn):
        return hashlib.sha1(open(fn, 'rb').read()).hexdigest()

# -----------------------------------------------------------------------

    def sqlite3command(self):
        if self.name == 'firefox':
            return '''SELECT strftime('%Y-%m-%dT%H:%M:%SZ',(moz_historyvisits.visit_date/1000000), 'unixepoch'),moz_places.url,moz_places.title FROM moz_places, moz_historyvisits WHERE moz_places.id = moz_historyvisits.place_id ORDER BY moz_historyvisits.visit_date desc'''
        else:
            return '''SELECT strftime('%Y-%m-%dT%H:%M:%SZ',(last_visit_time/1000000)-11644473600, 'unixepoch'),url,title FROM urls ORDER BY last_visit_time desc'''

# -----------------------------------------------------------------------
    
    def blacklisted(self, uri):
        if not config.has_key('blacklist_'+self.name):
            return False
        for bl_substr in config['blacklist_'+self.name]:
            if bl_substr in uri:
                print "URI %s matches a blacklist item [%s], skipping" % (uri, bl_substr) 
                return True
        return False

# -----------------------------------------------------------------------

    def payload_to_json(self, payload, alt_text):
        try:
            return json.dumps(payload)
        except UnicodeDecodeError:
            pass

        payload['subject']['text'] = alt_text
        try:
            return json.dumps(payload)
        except UnicodeDecodeError:
            pass

        payload['subject']['text'] = ''
        try:
            return json.dumps(payload)
        except UnicodeDecodeError:
            return ''

# -----------------------------------------------------------------------

    def run(self):

        print ("Starting the " + self.name + " logger on " + time.strftime("%c") + 
               " with " + str(len(self.events)) + " known events and"
               " with " + str(len(self.subjects)) + " known subjects")

        if not config.has_key('history_file_'+self.name):
            print "ERROR: History file not specified"
            return False

        if not os.path.isfile(config['history_file_'+self.name]):
            print "ERROR: History file not found at: " + config['history_file_'+self.name]
            return False

        history_file_sha1 = self.file_to_sha1(config['history_file_'+self.name])
        if history_file_sha1 == self.old_history_file_sha1:
            print "History not changed, exiting."
            return True
        self.old_history_file_sha1 = history_file_sha1

        shutil.copy(config['history_file_'+self.name], config['tmpfile_'+self.name])
        if not os.path.isfile(config['tmpfile_'+self.name]):
            print "ERROR: Failed copying history to: " + config['tmpfile_'+self.name]
            return False

        conn = sqlite3.connect(config['tmpfile_'+self.name])
        c = conn.cursor()

        i = 0
        for row in c.execute(self.sqlite3command()):

            if i>=config['nevents_'+self.name]:
                break

            storage  = 'net'
            mimetype = 'unknown'

            datetime = row[0]
            uri      = row[1]

            print "Processing %d:%s" % (i, uri)
            i = i+1

            if self.blacklisted(uri):
                continue

            payload = {'origin':         config['hostname'],
                       'actor':          config['actor_'+self.name],
                       'interpretation': config['event_interpretation'],
                       'manifestation':  config['event_manifestation'],
                       'timestamp':      datetime}

            subject = {'uri':            uri,
                       'interpretation': config['subject_interpretation'],
                       'manifestation':  config['subject_manifestation'],
                       'mimetype':       mimetype,
                       'storage':        storage}

            subject['id'] = self.json_to_sha1(subject)
            payload['subject'] = {}
            payload['subject']['id'] = subject['id']
            payload['id'] = self.json_to_sha1(payload)

            if payload['id'] in self.events:
                print "Match found in known events, skipping"
                continue
            else:
                self.events.add(payload['id'])

            if not subject['id'] in self.subjects:
                print "Not found in known subjects, sending full data"
                self.subjects.add(subject['id'])

                if config['fulltext']:
                    lynx_command = config['fulltext_command'] % uri
                    try:
                        subject['text'] = subprocess.check_output(lynx_command, shell=True)
                    except subprocess.CalledProcessError:
                        subject['text'] = row[2]
                    if config['maxtextlength_web']>0 and len(subject['text'])>config['maxtextlength_web']:
                        subject['text'] = subject['text'][0:config['maxtextlength_web']]
                else:
                    subject['text'] = row[2]

                payload['subject'] = subject.copy()


            json_payload = self.payload_to_json(payload, row[2])
            if (json_payload == ''):
                print "Something went wrong in JSON conversion, skipping"
                continue
            print(json_payload)

            headers = {'content-type': 'application/json'}

            r = requests.post(config['server_url'], data=json_payload, headers=headers)
            print(r.text)
            print "########################################################"

            self.events_sent = self.events_sent + 1 
            self.data_sent = self.data_sent + len(json_payload)
            self.latest = int(time.time())

        print "Processed %d entries" % i

        return True

# -----------------------------------------------------------------------

if __name__ == '__main__':

    print "Starting the chrome2dime.py logger on " + time.strftime("%c")

    conf.configure()
    
    if len(sys.argv)>1:
        config['use_'+sys.argv[-1]] = True
        c2d = Browserlogger(sys.argv[-1])
        c2d.run()
    else:
        print "Usage: " + sys.argv[0] + " chrome|chromium|firefox"

# -----------------------------------------------------------------------
