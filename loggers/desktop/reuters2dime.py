#!/usr/bin/env python

import os
import sys
#import mailbox
import requests
import argparse
import time
import rfc822
import pprint
import nltk

from dlog_globals import config
import dlog_conf as conf
import dlog_common as common

porter = nltk.PorterStemmer()
#wnl = nltk.WordNetLemmatizer()

#------------------------------------------------------------------------------

def filter_string(string, do_stem=True):

    #tokens = nltk.word_tokenize(string)

    pattern = r'''(?x)  # set flag to allow verbose regexps
    ([A-Z]\.)+          # abbreviations, e.g. U.S.A.
    | \w+(-\w+)*        # words with optional internal hyphens
    | \$?\d+(\.\d+)?%?  # currency and percentages, e.g. $12.40, 82%
    | \.\.\.            # ellipsis
    | [][.,;"'?():-_`]  # these are separate tokens
    '''
    tokens = nltk.regexp_tokenize(string, pattern)

    tokens = [t.lower() for t in tokens]
    if do_stem:
        tokens = [porter.stem(t) for t in tokens]
    #tokens = [wnl.lemmatize(t) for t in tokens]
    return " ".join(item for item in tokens if len(item)>1)

#------------------------------------------------------------------------------

def create_payload(line, fn, i, do_stem):

    print "---###---###---###---###---###---###---###---###---###---###---"
    print
    print '%d: %s ...' % (i, line[:50])
    print

    parts = line.split("\t")

    if parts[0] in skipped_categories:
        print line[:30], "... (", parts[0],  ") matches category to be skipped"
        return None

    finaltags = ['category='+parts[0]]
    
    payload = {
        '@type':  'MessageEvent',
        'actor':    'reuters2dime.py',
        'origin':   config['hostname'],
        'type':     'http://www.hiit.fi/ontologies/dime/#NewsEvent',
        'duration': 0}
    
    targettedResource = {
        '@type':      'Message',
        'uri': 'file://'+fn+'#'+str(i),
        'type': 'http://www.semanticdesktop.org/ontologies/2007/03/22/nmo/#Message',
        'isStoredAs': 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo/#EmbeddedFileDataObject',
        #'subject': filter_string(message['Subject'], do_stem),
        #'fromString': message['From'],
        'tags' : finaltags
        #'attachments': [],
        #'rawMessage': '' # the full raw message here...
    }

    targettedResource['id'] = common.to_json_sha1(targettedResource)
    payload['targettedResource'] = {}
    payload['targettedResource']['id'] = targettedResource['id']
    payload['id'] = common.to_json_sha1(payload)

    targettedResource['plainTextContent'] = filter_string(parts[1], do_stem)

    payload['targettedResource'] = targettedResource.copy()

    return common.json_dumps(payload, indent=2)

#------------------------------------------------------------------------------

if __name__ == "__main__":

    print "Starting the reuters2dime.py logger on " + time.strftime("%c")

    parser = argparse.ArgumentParser(description='Sends 20 Newsgroups data to DiMe.')

    parser.add_argument('msgfile', metavar='FILE',
                        help='list of newsgroup articles to be processed')
    parser.add_argument('--dryrun', action='store_true',
                        help='do not actually send anything')
    parser.add_argument('--limit', metavar='N', action='store', type=int,
                        default=0, help='process only N first messages')
    parser.add_argument('--nostem', action='store_true',
                        help='disable Porter stemming of tokens')
    parser.add_argument('--skip', action='store', metavar='X[,Y]',
                        help='skip categories X [and Y]')

    args = parser.parse_args()

    skipped_categories = []
    if args.skip:
        skipped_categories = args.skip.split(",")
        print "Categories to be skipped are", skipped_categories

    cwd = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    conf.configure(inifile="reuters.ini")
    os.chdir(cwd)

    print "Username read from ini-file:", config['username']

    pingstring = "Pinging DiMe server at location: " + config['server_url'] + " : "
    if common.ping_server():
        print pingstring + "OK"
    else:
        print pingstring + "FAILED"
        if not args.dryrun:
            print 'Ping failed and "--dryrun" not set, exiting'
            sys.exit()

    i=1
    with open(args.msgfile) as f:
        for line in f:
            line = line.rstrip()
            #print "Processing [{}]".format(line)

            json_payload = create_payload(line, args.msgfile, i, not args.nostem)

            if json_payload is not None:
                print "PAYLOAD:\n" + json_payload
                if not args.dryrun:
                    common.post_payload(json_payload, "event")

            if args.limit>0 and i >= args.limit:
                break
            i=i+1

    print "Processed %d entries" % i
    
#------------------------------------------------------------------------------
