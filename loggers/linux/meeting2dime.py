#!/usr/bin/env python

import os.path
import sys
import argparse
import requests

from zg2dimeglobals import config
import zg2dimeconf as conf
import zg2dimecommon as common

# -----------------------------------------------------------------------

def read_slidetxt(pngfn):
    slidetxtfn = pngfn
    slidetxtfn = slidetxtfn.replace(".png", ".txt")
    slidetxtfn = args.slidepath + '/' + slidetxtfn
    print slidetxtfn
    with open (slidetxtfn, "r") as t:
        return t.read()

# -----------------------------------------------------------------------

def calc_slidetime(frame, start_time):
    stparts = start_time.split(':')
    stinsecs = int(stparts[0])*3600 + int(stparts[1])*60 + int(stparts[2])
    slinsecs = stinsecs + frame/args.fps
    slhrs, slmins = divmod(slinsecs, 3600)
    slmins, slsecs = divmod(slmins, 60)
    return "%02d:%02d:%02d" % (slhrs, slmins, slsecs)

# -----------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Sends meeting slides to DiMe.')

parser.add_argument('videos', metavar='N', nargs='+',
                     help='meeting videos to be processed')
parser.add_argument('--slides', action='store', required=True, dest='slidepath',
                    help='path to individual slides')
parser.add_argument('--tz', action='store', required=True, 
                    help='numeric time zone, e.g. "+0200"')
parser.add_argument('--fps', action='store', type=int, required=True, 
                    help='frame rate of video')

args = parser.parse_args()

conf.configure()

seenslides = set()

i = 0
for videofile in args.videos:
    print "Processing %s" % videofile
    timestampfile = videofile + ".txt"
    if not os.path.isfile(timestampfile):
        print "Timestamp file %s not found, continuing" % timestampfile
        continue

    with open (timestampfile, "r") as timestamp:
        for line in timestamp:
            tsparts = line.strip().split()
            break

    print "  timestamp: %sT%s%s" % (tsparts[0], tsparts[1], args.tz)

    matchesfile = videofile + ".matches.txt"
    if not os.path.isfile(matchesfile):
        print "Matches file %s not found, continuing" % matchesfile
        continue


    with open (matchesfile, "r") as matches:
        for line in matches:
            mparts = line.strip().split()            
            if len(mparts)==2 and not mparts[1] in seenslides:
                print "  slide found: [%s]" % line.strip()
                i = i+1
                seenslides.add(mparts[1])
                slidetime = calc_slidetime(int(mparts[0]), tsparts[1])
                datetime = "%sT%s%s" % (tsparts[0], slidetime, args.tz)
                slidetxt = read_slidetxt(mparts[1])
                
                mimetype = 'unknown'
                uri      = 'file://' + videofile + '?f=' + mparts[0]

                payload = {'origin':         config['hostname'],
                           'actor':          'meeting2dime.py',
                           'interpretation': config['event_interpretation_meeting'],
                           'manifestation':  config['event_manifestation_meeting'],
                           'timestamp':      datetime}

                subject = {'uri':            uri,
                           'interpretation': config['subject_interpretation_meeting'],
                           'manifestation':  config['subject_manifestation_meeting'],
                           'mimetype':       mimetype,
                           'storage':        'net'}

                subject['id'] = common.json_to_sha1(subject)
                payload['subject'] = {}
                payload['subject']['id'] = subject['id']
                payload['id'] = common.json_to_sha1(payload)
                subject['text'] = slidetxt
                payload['subject'] = subject.copy()

                json_payload = common.json_dumps(payload)
                print(json_payload)                

                headers = {'content-type': 'application/json'}

                r = requests.post(config['server_url'], data=json_payload,
                                  headers=headers,
                                  auth=(config['username'],
                                        config['password']))

                print(r.text)
                print "########################################################"

print "Processed %d entries" % i

# -----------------------------------------------------------------------
