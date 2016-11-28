#!/usr/bin/env python3

import json
import argparse
import datetime

#------------------------------------------------------------------------------

def dime_date(epoch_time):
    return datetime.datetime.fromtimestamp(float(epoch_time)/1000.0)

#------------------------------------------------------------------------------


def main(args):
    fp = open(args.dime_dump_fname, 'r')
    data=json.load(fp)
    fp.close()

    fp_text = None
    if args.collect_text:
        fp_text = open(args.collect_text, 'w')
    
    print('Loaded {} DiMe events from {}.'.format(len(data), args.dime_dump_fname))
    
    text_hist = {}

    old_day=''
    for event in data:
        dt = dime_date(event['start'])
        day = dt.strftime("%Y-%m-%d")
        time = dt.strftime("%H:%M")

        actor = event['actor']

        if day != old_day:
            if args.show_events:
                print()
                print('***', day, '***')
            old_day = day

        elem = event.get('targettedResource')

        text = None
        desc = None
        if elem:
            desc = elem.get('title')
            if desc:
                desc = '"' + desc + '"'
            else:
                desc = elem['uri']

            text = elem.get('plainTextContent')

        if actor == "Fitbit":
            desc = '{} {}'.format(int(event['value']), event['activityType'])

        if desc is None:
            desc = ''
        else:
            desc = '- ' + desc

        textNote=''
        if text:
            lt = len(text.split())
            textNote = '- {} chars'.format(lt)

            if lt > 10:
                text_hist[actor] = text_hist.get(actor, 0) + lt

            if fp_text:
                print(text, file=fp_text)

        if args.show_events:
            print(time, event['actor'], desc, textNote)

    if fp_text:
        fp_text.close()

    if text_hist:
        print("*** Text \"histogram\" ***")
        for key in sorted(text_hist, key=text_hist.get, reverse=True):
            print(key, text_hist[key])

#------------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dime_dump_fname', type=str)
    parser.add_argument('--collect_text', type=str, required=False)
    # parser.add_argument('--val', type=int, default=1)
    parser.add_argument('--show_events', action='store_true')
    args = parser.parse_args()
    
    main(args)
