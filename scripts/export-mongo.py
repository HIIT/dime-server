#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import argparse
import sys
import datetime
import bson
import json
from pymongo import MongoClient
import io

elem_fields = {}
event_fields = {}

linked_app_ids = set()

debug = False

#------------------------------------------------------------------------------

def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    elif isinstance(obj, bson.objectid.ObjectId):
        return str(obj)
    raise TypeError ("Type not serializable:" + obj)

#------------------------------------------------------------------------------

def process_common(obj, uid, allowMissing=False):
    obj['appId'] = obj['_id']
    del(obj['_id'])

    if not allowMissing or '_class' in obj:
        obj['@type'] = obj['_class'].split('.')[-1]
        del(obj['_class'])
    
    if not allowMissing or 'user' in obj:
        assert(obj['user']['_id'] == uid)
        del(obj['user'])

    return obj

#------------------------------------------------------------------------------

def process_element(elem, uid, allowMissing=False):
    global elem_fields

    elem = process_common(elem, uid, allowMissing)

    for k in elem.keys():
        t = type(elem[k])
        elem_fields[k] = str(type(elem[k]))
    return elem

#------------------------------------------------------------------------------

def process_event(event, uid):
    global event_fields

    event = process_common(event, uid)

    if 'targettedResource' in event:
        elem = event['targettedResource']
        event['targettedResource'] = process_element(elem, uid, True)
        linked_app_ids.add(elem['appId'])

    for k in event.keys():
        t = type(event[k])
        event_fields[k] = str(type(event[k]))

    return event    

#------------------------------------------------------------------------------

def export_events(db, uid, filename):
    events = db.event

    n = 0

    with io.open(filename, 'w', encoding='utf-8') as fp:
        fp.write(u'[')
        for event in events.find({'user._id': uid}):
            if n > 0:
                fp.write(u',\n')
            event = process_event(event, uid)
            fp.write(json.dumps(event, default=json_serial,
                                indent=2,
                                ensure_ascii=False))
            n += 1
        fp.write(u']')

    print('Exported {} events.'.format(n))

    if debug:
        print('\nEvent fields:')
        for f in event_fields:
            print(f, event_fields[f])

    # print('\nElement fields:')
    # for f in elem_fields:
    #     print(f, elem_fields[f])

#------------------------------------------------------------------------------

def export_element(elem, uid, fp):
    elem = process_element(elem, uid)
    fp.write(json.dumps(elem, default=json_serial, indent=2,
                        ensure_ascii=False))

#------------------------------------------------------------------------------
    
def export_elems(db, uid, filename):
    elems = db.informationElement
    events = db.event

    n = 0

    with io.open(filename, 'w', encoding='utf-8') as fp:
        fp.write(u'[')
        for elem in elems.find({'user._id': uid}):
            if n > 0:
                fp.write(u',\n')
            export_element(elem, uid, fp)
            appId = elem['appId']
            if appId in linked_app_ids:
                linked_app_ids.remove(appId)
            n += 1

        orphan_count = len(linked_app_ids)
        if orphan_count > 0:
            print('\nFound {} orphan elements. Exporting these as well...'.format(orphan_count))

            for appId in linked_app_ids:
                if n > 0:
                    fp.write(u',\n')
                elem = events.find_one({'targettedResource._id': appId})
                export_element(elem, uid, fp)
                n += 1

        fp.write(u']')

    print('\nExported {} elements.'.format(n))

    if debug:
        print('\nElement fields:')
        for f in elem_fields:
            print(f, elem_fields[f])

#------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', '-u', type=str)
    args = parser.parse_args()

    client = MongoClient()
    db = client.dime

    users = db.user

    if not args.user: 
        print("Please specify the user for which to export the DiMe data by using the -u argument when running this command, e.g.\n")
        print("  " + sys.argv[0] + " -u someuser\n")
        print("The local mongodb database contains the following users:\n")

        for user in users.find():
            print("  " + user['username'])

        print()
    else:
        user = users.find_one({'username': args.user})
        uid = user['_id']
        export_events(db, uid, 'dime-events.json')
        export_elems(db, uid, 'dime-elements.json')


if __name__ == '__main__':
    main()
