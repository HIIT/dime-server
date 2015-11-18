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

import random
random.seed(42)

import xml.etree.ElementTree as ET

from dlog_globals import config
import dlog_conf as conf
import dlog_common as common

porter = nltk.PorterStemmer()
wnl = nltk.WordNetLemmatizer()

text2cat = {
    "Computer Science - Artificial Intelligence": "cs.AI",
    "Computer Science - Computational Complexity": "cs.CC",
    "Computer Science - Computational Engineering, Finance, and Science": "cs.CE",
    "Computer Science - Computational Geometry": "cs.CG",
    "Computer Science - Computation and Language": "cs.CL",
    "Computer Science - Computers and Society": "cs.CY",
    "Computer Science - Computer Science and Game Theory": "cs.GT",
    "Computer Science - Computer Vision and Pattern Recognition": "cs.CV",
    "Computer Science - Cryptography and Security": "cs.CR",
    "Computer Science - Databases": "cs.DB",
    "Computer Science - Data Structures and Algorithms": "cs.DS",
    "Computer Science - Digital Libraries": "cs.DL",
    "Computer Science - Discrete Mathematics": "cs.DM",
    "Computer Science - Distributed, Parallel, and Cluster Computing": "cs.DC",
    "Computer Science - Emerging Technologies": "cs.ET",
    "Computer Science - Formal Languages and Automata Theory": "cs.FL",
    "Computer Science - General Literature": "cs.GL",
    "Computer Science - Graphics": "cs.GR",
    "Computer Science - Hardware Architecture": "cs.AR",
    "Computer Science - Human-Computer Interaction": "cs.HC",
    "Computer Science - Information Retrieval": "cs.IR",
    "Computer Science - Information Theory": "cs.IT",
    "Computer Science - Learning": "cs.LG",
    "Computer Science - Logic in Computer Science": "cs.LO",
    "Computer Science - Mathematical Software": "cs.MS",
    "Computer Science - Multiagent Systems": "cs.MA",
    "Computer Science - Multimedia": "cs.MM",
    "Computer Science - Networking and Internet Architecture": "cs.NI",
    "Computer Science - Neural and Evolutionary Computing": "cs.NE",
    "Computer Science - Numerical Analysis": "cs.NA",
    "Computer Science - Operating Systems": "cs.OS",
    "Computer Science - Other Computer Science": "cs.OH",
    "Computer Science - Performance": "cs.PF",
    "Computer Science - Programming Languages": "cs.PL",
    "Computer Science - Robotics": "cs.RO",
    "Computer Science - Social and Information Networks": "cs.SI",
    "Computer Science - Software Engineering": "cs.SE",
    "Computer Science - Sound": "cs.SD",
    "Computer Science - Symbolic Computation": "cs.SC",
    "Computer Science - Systems and Control": "cs.SY"
}

#------------------------------------------------------------------------------

def filter_string(string, do_stem=True, do_lemma=False):

    if ((not nltk.__version__.startswith('2')) and 
        (not nltk.__version__.startswith('3.0'))):
        print("ERROR: Use of incompatible nltk suspected")
        sys.exit()

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
    if do_lemma:
        tokens = [wnl.lemmatize(t) for t in tokens]
    return " ".join(item for item in tokens if len(item)>1)

#------------------------------------------------------------------------------

def create_payload(doc, i, do_stem, do_lemma):

    print "---###---###---###---###---###---###---###---###---###---###---"
    print i
    print

    uri, title, abstract = '', '', ''
    keywords = []
    finaltags = []
    for field in doc:
        text = field.text
        if not field.attrib.has_key('name'):
            continue
        nameattr = field.attrib['name']
        if nameattr == 'url':
            uri = text
        elif nameattr == 'title':
            title = text
        elif nameattr == 'abstract':
            abstract = text
        elif nameattr == 'keyword':
            keywords.append(text)
        elif nameattr == 'subject' and text2cat.has_key(text):
            finaltags = ['category='+text2cat[text], 'categorytext='+text]

    payload = {
        '@type':    'DesktopEvent',
        'actor':    'arxiv-cs2dime.py',
        'origin':   config['hostname'],
        'type':     'http://www.semanticdesktop.org/ontologies/2010/01/25/nuao#UsageEvent',
        'duration': 0}

    targettedResource = {
        '@type':      'ScientificDocument',
        'uri': uri,
        'type': 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo/#PlainTextDocument',
        'isStoredAs': 'http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#EmbeddedFileDataObject',
        'keywords': keywords,
        'title': filter_string(title, do_stem, do_lemma), 
        'tags' : finaltags
    }

    targettedResource['id'] = common.to_json_sha1(targettedResource)
    payload['targettedResource'] = {}
    payload['targettedResource']['id'] = targettedResource['id']
    payload['id'] = common.to_json_sha1(payload)

    targettedResource['plainTextContent'] = filter_string(abstract, do_stem, do_lemma)

    payload['targettedResource'] = targettedResource.copy()

    return common.json_dumps(payload, indent=2)

#------------------------------------------------------------------------------

if __name__ == "__main__":

    print "Starting the arxiv-cs2dime.py logger on " + time.strftime("%c")

    parser = argparse.ArgumentParser(description='Sends Arxiv.org CS data to DiMe.')

    parser.add_argument('xmlfile', metavar='FILE',
                        help='list of abstracts to be processed')
    parser.add_argument('--dryrun', action='store_true',
                        help='do not actually send anything')
    parser.add_argument('--limit', metavar='N', action='store', type=int,
                        default=0, help='process only N first abstracts')
    parser.add_argument('--nostem', action='store_true',
                        help='disable Porter stemming of tokens')
    parser.add_argument('--probskip', action='store', type=float,
                        default=-1.0, help='probability of skipping an abstract')
    parser.add_argument('--lemmatize', action='store_true',
                        help='enable Wordnet lemmatization of tokens')

    args = parser.parse_args()

    cwd = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    conf.configure(inifile="arxiv-cs.ini")
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

    print "Parsing XML, this may take a while"
    tree = ET.parse(args.xmlfile)
    root = tree.getroot()
    print "Parsing XML done"

    i=0
    skipped = []
    for j, doc in enumerate(root):
        if random.random()<args.probskip:
            print "Skipping", j, doc
            skipped.append(j)
            continue

        print "Processing", j, doc

        json_payload = create_payload(doc, i, not args.nostem, args.lemmatize)
        if json_payload is None:
            continue
        print "PAYLOAD:\n" + json_payload

        if not args.dryrun:
            common.post_payload(json_payload, "event")
            
        if args.limit>0 and i >= args.limit:
            break
        i=i+1

    print "Processed %d entries" % i
    print "Skipped:", skipped
    with open("skipped.txt", 'w') as file:
        for item in skipped:
            file.write("%d\n" % item)

#------------------------------------------------------------------------------
