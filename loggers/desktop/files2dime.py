#!/usr/bin/env python

import sys
import time
import os
import argparse

from dlog_globals import config
import dlog_conf as conf
import dlog_common as common
import browserlogger as blog

# -----------------------------------------------------------------------

def process_file(filepath, filename):
    json_payload = create_payload(filepath, filename)
    if json_payload is None:
        return
    print "PAYLOAD:\n" + json_payload
    
    if not args.dryrun:
        common.post_payload(json_payload, "informationelement")

# -----------------------------------------------------------------------

def create_payload(filepath, filename):

    print "Starting to process", filename, "at", filepath, "on", time.strftime("%c")

    if common.blacklisted(filename, 'blacklist_files'):
        print "File is blacklisted";
        return None

    filepathname = filepath+'/'+filename
    
    if not os.path.isfile(filepathname):
        print "File cannot be found/accessed";
        return None
    
    mimetype, document_type, text = common.analyze_file(filepathname, 'files')
    
    payload = {'@type':            'Document',
                'uri':              'file://'+filepathname,
                'type':             document_type,
                'isStoredAs':       common.o("nfo_localfiledataobject"),
                'mimeType':         mimetype}

    payload['id'] = common.to_json_sha1(payload)
    payload['plainTextContent'] = text

    return common.json_dumps(payload, indent=2)

# -----------------------------------------------------------------------

if __name__ == '__main__':

    print "Starting the files2dime.py logger on " + time.strftime("%c")

    parser = argparse.ArgumentParser(description='Sends local files to DiMe.')

    parser.add_argument('--dryrun', action='store_true',
                        help='do not actually send anything')
    parser.add_argument('--count', action='store_true',
                        help='count found files only, implies --dryrun')
    parser.add_argument('--limit', metavar='N', action='store', type=int,
                        default=0, help='process only N first files')

    args = parser.parse_args()

    conf.configure()

    if args.count:
        args.dryrun = True
    
    pingstring = "Pinging DiMe server at location: " + config['server_url'] + " : "
    if common.ping_server():
        print pingstring + "OK"
    else:
        print pingstring + "FAILED"
        if not args.dryrun:
            print 'Ping failed and "--dryrun" not set, exiting'
            sys.exit()

    i = 0
    stopall = False
    for root_path in config['root_paths_files']:
        if stopall:
            break
        print('Processing root path: %s' % root_path)
        for dirName, subdirList, fileList in os.walk(root_path):
            if stopall:
                break
            print('Found directory: %s' % dirName)
            innermost = ''
            parts = dirName.rsplit('/',1)
            if len(parts)==2:
                innermost = parts[1]
            if innermost.startswith('.') or dirName in config['exclusions_files']:
                print('\tExcluded dir: %s' % dirName)
                del subdirList[:]
                continue
            else:
                for fname in fileList:
                    if fname.startswith('.'):
                        continue
                    elif fname.endswith(tuple(config['extensions_files'])):
                        if args.limit>0 and i >= args.limit:
                            stopall = True
                            break
                        print('\t%s' % fname)
                        if not args.count:
                            process_file(dirName, fname)
                        i=i+1

    print "Processed %d files" % i

# -----------------------------------------------------------------------
