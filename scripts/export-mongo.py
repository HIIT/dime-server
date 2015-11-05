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
bad_user = set()
null_type = set()
no_elem_found = set()

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

def process_common(obj, uid):
    global null_type

    app_id = obj['_id']
    obj['appId'] = app_id
    del(obj['_id'])

    if '_class' in obj:
        obj['@type'] = obj['_class'].split('.')[-1]
        del(obj['_class'])
    else:
        null_type.add(app_id)
        return None
    
    if 'user' in obj:
        if str(obj['user']['_id']) != str(uid):
            bad_user.add(app_id)
            return None
        del(obj['user'])

    return obj

#------------------------------------------------------------------------------

def process_element(elem, uid):
    global elem_fields

    elem = process_common(elem, uid)
    
    if elem is None:
        return None

    for k in elem.keys():
        t = type(elem[k])
        elem_fields[k] = str(type(elem[k]))
    return elem

#------------------------------------------------------------------------------

def export_events(db, uid, filename):
    global event_fields, no_elem_found, linked_app_ids

    events = db.event
    elems = db.informationElement

    n = 0

    with io.open(filename, 'w', encoding='utf-8') as fp:
        fp.write(u'[')
        for event in events.find({'user._id': uid}):
            event = process_common(event, uid)

            if event is None:
                continue

            # if we have a targettedResource, let's instead fetch it
            # from the events db if available - that's supposed to be
            # the more complete version
            if 'targettedResource' in event:
                elem_id = event['targettedResource']['_id']
                elem = elems.find_one({'_id': elem_id, 'user._id': uid})

                # if elem_id == '6f6f1c2f6c8960662de300b048e75c18398eadf1':
                #     print("HERE")
                #     print(elem)

                # if we can't find it use the embedded one
                # if elem is None:
                #     elem = event['targettedResource']
                if elem is None:
                    no_elem_found.add(elem_id)
                    continue

                processed_elem = process_element(elem, uid)
                if processed_elem is None:
                    continue

                event['targettedResource'] = processed_elem
                linked_app_ids.add(elem['appId'])

            for k in event.keys():
                t = type(event[k])
                event_fields[k] = str(type(event[k]))

            if n > 0:
                fp.write(u',\n')
            fp.write(json.dumps(event, default=json_serial,
                                indent=2,
                                ensure_ascii=False))
            n += 1
        
        fp.write(u']\n')

    print('Exported {} events.'.format(n))

    if debug:
        print('\nEvent fields:')
        for f in event_fields:
            print(f, event_fields[f])

    # print('\nElement fields:')
    # for f in elem_fields:
    #     print(f, elem_fields[f])

#------------------------------------------------------------------------------

def export_element(elem, uid, fp, n):
    elem = process_element(elem, uid)
    if elem is not None:
        if n > 0:
            fp.write(u',\n')
        fp.write(json.dumps(elem, default=json_serial, indent=2,
                            ensure_ascii=False))

#------------------------------------------------------------------------------
    
def export_elems(db, uid, filename):
    global linked_app_ids

    elems = db.informationElement
    events = db.event

    n = 0

    with io.open(filename, 'w', encoding='utf-8') as fp:
        fp.write(u'[')
        for elem in elems.find({'user._id': uid}):
            export_element(elem, uid, fp, n)

            appId = elem['appId']
            if appId in linked_app_ids:
                linked_app_ids.remove(appId)
            n += 1

        orphan_count = len(linked_app_ids)
        if orphan_count > 0:
            print('Found {} orphan elements. Exporting these as well...'.format(orphan_count))

            for appId in linked_app_ids:
                elem = events.find_one({'targettedResource._id': appId})
                export_element(elem, uid, fp, n)
                n += 1

        fp.write(u']\n')

    print('Exported {} elements.'.format(n))

    if debug:
        print('\nElement fields:')
        for f in elem_fields:
            print(f, elem_fields[f])

#------------------------------------------------------------------------------

def main():
    global bad_user, null_type, no_elem_found

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
            print("{} ({})".format(user['username'], str(user['_id'])))

        print()
    else:
        user = users.find_one({'username': args.user})
        uid = user['_id']
        export_events(db, uid, 'dime-events.json')
        export_elems(db, uid, 'dime-elements.json')

        if bad_user:
            print('Skipped {} objects with incorrect user.'.format(len(bad_user)))
        if null_type:
            print('Skipped {} objects with null type.'.format(len(null_type)))

        if no_elem_found:
            print('Skipped {} events with broken objects.'.format(len(no_elem_found)))


if __name__ == '__main__':
    main()
