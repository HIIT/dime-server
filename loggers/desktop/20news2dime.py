#!/usr/bin/env python

import os
import sys
import mailbox
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

def create_payload(message, i, fn, do_stem):

    print "---###---###---###---###---###---###---###---###---###---###---"
    print
    print '%d: %s "%s" from %s' % (i, message['Message-ID'], message['subject'], message['from'])
    print

    parts = fn.split("/")
    finaltags = ['filename='+fn, 'newsgroup='+parts[0]]
    
    payload = {
        '@type':  'MessageEvent',
        'actor':    '20news2dime.py',
        'origin':   config['hostname'],
        'type':     'http://www.hiit.fi/ontologies/dime/#NewsEvent',
        'duration': 0}
    
    targettedResource = {
        '@type':      'Message',
        'uri': fn,
        'type': 'http://www.semanticdesktop.org/ontologies/2007/03/22/nmo/#Message',
        'isStoredAs': 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo/#LocalFileDataObject',
        'subject': filter_string(message['Subject'], do_stem),
        'fromString': message['From'],
        'tags' : finaltags
        #'attachments': [],
        #'rawMessage': '' # the full raw message here...
    }

    targettedResource['id'] = common.to_json_sha1(targettedResource)
    payload['targettedResource'] = {}
    payload['targettedResource']['id'] = targettedResource['id']
    payload['id'] = common.to_json_sha1(payload)

    msgpayload = message.get_payload()
    msgtext = ''
    while isinstance(msgpayload, list): 
        msgpayload = msgpayload[0].get_payload()

    if isinstance(msgpayload, str):
        msgtext = msgpayload

    targettedResource['plainTextContent'] = filter_string(msgtext, do_stem)

    payload['targettedResource'] = targettedResource.copy()

    return common.json_dumps(payload, indent=2)

#------------------------------------------------------------------------------

if __name__ == "__main__":

    print "Starting the enron2dime.py logger on " + time.strftime("%c")

    parser = argparse.ArgumentParser(description='Sends 20 Newsgroups data to DiMe.')

    parser.add_argument('msgfile', metavar='FILE',
                        help='list of newsgroup articles to be processed')
    parser.add_argument('--dryrun', action='store_true',
                        help='do not actually send anything')
    parser.add_argument('--limit', metavar='N', action='store', type=int,
                        default=0, help='process only N first messages')
    parser.add_argument('--nostem', action='store_true',
                        help='disable Porter stemming of tokens')

    args = parser.parse_args()

    cwd = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    conf.configure(inifile="20news.ini")
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
            print "Processing [{}]".format(line)
            mbox = mailbox.mbox(line)
            if len(mbox) != 1:
                print "ERROR: Multiple messages found in", line
                break
            for message in mbox:
                json_payload = create_payload(message, i, line, not args.nostem)
                if json_payload is None:
                    continue
                print "PAYLOAD:\n" + json_payload

                if not args.dryrun:
                    common.post_payload(json_payload, "event")

            if args.limit>0 and i >= args.limit:
                break
            i=i+1

    print "Processed %d entries" % i
    
#------------------------------------------------------------------------------
