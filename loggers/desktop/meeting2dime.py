#!/usr/bin/env python

import os
import sys
import time
import argparse
import requests

from zg2dimeglobals import config
import zg2dimeconf as conf
import zg2dimecommon as common

# -----------------------------------------------------------------------

def read_txt(fn):
    if args.slides:
        txtfn = fn.replace(".png", ".txt")
    else:
        txtfn = fn
    if os.path.isfile(txtfn):
        print "Opening " + txtfn
        with open (txtfn, "r") as t:
            return t.read()
    else:
        print "WARNING: File not found: " + txtfn
        return ''

# -----------------------------------------------------------------------

def calc_slidetime(frame, start_time):
    stparts = start_time.split(':')
    stinsecs = int(stparts[0])*3600 + int(stparts[1])*60 + int(stparts[2])
    slinsecs = stinsecs + frame/args.fps
    slhrs, slmins = divmod(slinsecs, 3600)
    slmins, slsecs = divmod(slmins, 60)
    return "%02d:%02d:%02d" % (slhrs, slmins, slsecs)

# -----------------------------------------------------------------------

def create_payload(epoch, uri, fn):

    datetime = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(epoch))

    tz = time.strftime("%Z", time.localtime(epoch))
    if tz == "EET":
        tz = "+0200"
    elif tz == "EEST":
        tz = "+0300"

    payload = {'origin': config['hostname'],
               'actor':  'meeting2dime.py',
               'type':   common.ontology('event_type_meeting'),
               'start':  datetime+tz}
    
    document = {'uri':            uri,
                'type':           common.ontology('document_type_meeting'),
                'isStoredAs':     common.ontology('document_isa_meeting'),
                'mimeType':       'unknown'}
    
    document['id'] = common.to_json_sha1(document)
    payload['targettedResource'] = {}
    payload['targettedResource']['id'] = document['id']
    payload['id'] = common.to_json_sha1(payload)
    document['text'] = read_txt(fn)
    payload['targettedResource'] = document.copy()
    
    return common.json_dumps(payload)

# -----------------------------------------------------------------------

def post_payload(json_payload):
    headers = {'content-type': 'application/json'}

    r = requests.post(config['server_url']+"/data/zgevent",
                      data=json_payload,
                      headers=headers,
                      auth=(config['username'],
                            config['password']))

    print(r.text)
    print "########################################################"

# -----------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Sends meeting slides to DiMe.')

parser.add_argument('videofile', metavar='N',
                     help='meeting video to be processed')
parser.add_argument('--slides', action='store_true', 
                    help='path to individual slides')
parser.add_argument('--noslides', action='store', metavar='textdesc',
                    help='no individual slides, use video-level description')
parser.add_argument('--url', action='store',
                    help='use this URL instead of file:// link to videofile')
parser.add_argument('--dryrun', action='store_true',
                    help='do not actually send anything')
parser.add_argument('--firstonly', action='store_true',
                    help='store only the first time each slide is shown')

args = parser.parse_args()

if args.slides and args.noslides:
    print 'ERROR: Both "--slides" and "--noslides" cannot be set together'
    sys.exit()

if not args.slides and not args.noslides:
    print 'ERROR: Either "--slides" and "--noslides" has to be set'
    sys.exit()

if args.url:
    url = args.url
else:
    url = 'file://' + args.videofile

cwd = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

conf.configure()

os.chdir(cwd)

pingstring = "Pinging DiMe server at location: " + config['server_url'] + " : "
if common.ping_server():
    print pingstring + "OK"
else:
    print pingstring + "FAILED"
    if not args.dryrun:
        print 'Ping failed and "--dryrun" not set, exiting'
        sys.exit()

videofilepath = os.path.abspath(args.videofile)
videofilepath = os.path.split(videofilepath)[0]

seenslides = set()

i = 0

timefile = args.videofile + ".txt"
if not os.path.isfile(timefile):
    print "ERROR: Timefile %s not found" % timefile
    sys.exit()

start_epoch = 0
with open (timefile, "r") as tfile:
    for line in tfile:
        tsparts = line.strip().split()
        epoch = int(tsparts[0])
        if start_epoch==0:
            start_epoch = epoch

        if args.noslides:
            i = i+1
            json_payload = create_payload(epoch, url,
                                          args.noslides)
            print(json_payload)

            if not args.dryrun:
                post_payload(json_payload)

            break

        if (len(tsparts)==2 and
            not (args.firstonly and tsparts[1] in seenslides)):

            print "  slide found: [%s]" % line.strip()
            i = i+1
            seenslides.add(tsparts[1])

            timed_url = '%s#t=%d' % (url, (epoch-start_epoch))

            json_payload = create_payload(epoch, timed_url, tsparts[1])
            print(json_payload)

            if not args.dryrun:
                post_payload(json_payload)

print "Processed %d entries" % i

# -----------------------------------------------------------------------
