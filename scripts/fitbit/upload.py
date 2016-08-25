#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import fitbit
import socket
import time
import json
import requests
import ConfigParser
import hashlib
from pprint import pprint
from datetime import datetime, timedelta
from pytz import timezone

#------------------------------------------------------------------------------

fitbit_config = 'fitbit.cfg'
activity_type = 'steps'

#detail_level = '1min'
detail_level = '15min'

server_url = 'http://localhost:8080/api'
server_username = 'mvsjober'
server_password = 'tBaiTwIIAjB+YGg24F59zH9p'

#------------------------------------------------------------------------------

if __name__ == '__main__':
    r = requests.post(server_url + '/ping')

    if r.status_code != requests.codes.ok:
        print('No connection to DiMe server!')
        sys.exit(1)

    config = ConfigParser.ConfigParser()
    config.read(fitbit_config)

    client_id = config.get('oauth2', 'client_id')
    client_secret = config.get('oauth2', 'client_secret')

    access_token = config.get('oauth2', 'access_token')
    refresh_token = config.get('oauth2', 'refresh_token')

    client = fitbit.Fitbit(client_id, client_secret,
                           access_token=access_token, 
                           refresh_token=refresh_token)

    # See http://python-fitbit.readthedocs.io/en/latest/

    # a = client.activities()
    user_profile = client.user_profile_get()
    #pprint(client.get_devices())

    # pprint(a['summary']['steps'])

    device = client.get_devices()[0]['deviceVersion']
    print('Device = %s' % device)

    ts = client.intraday_time_series('activities/' + activity_type, 
                                     detail_level=detail_level)

    metadata = ts['activities-'+activity_type]
    values = ts['activities-'+activity_type+'-intraday']

    assert(len(metadata) == 1)
    
    events = []

    origin = socket.gethostbyaddr(socket.gethostname())[0]

    tz = timezone(user_profile['user']['timezone'])
    
    for i in range(len(metadata)):
        day = metadata[i]['dateTime']

        interval = values['datasetInterval']
        assert(values['datasetType'] == 'minute')

        td = timedelta(minutes=interval)

        for data in values['dataset']:
            #print(data['time'], data['value'])

            value = data['value']
            if value == 0:
                continue

            start = tz.localize(datetime.strptime(day + ' ' + data['time'], '%Y-%m-%d %H:%M:%S'))
            end = start + td

            payload = {
                '@type':    'HealthTrackerEvent',
                'actor':    'Fitbit',
                'device':   device,
                'activityType': activity_type,
                'origin':   origin,
                'type':     'http://www.hiit.fi/ontologies/dime/#HealthTrackerEvent',
                'start':    start.strftime("%Y-%m-%dT%H:%M:%S.000%z"),
                'end':      end.strftime("%Y-%m-%dT%H:%M:%S.000%z"),
                'value':    value
            }

            sha1 = hashlib.sha1()
            sha1.update('Fitbit|{}|{}|{}|{}'.format(device, payload['start'], 
                                                     payload['end'], origin))
            payload['appId'] = sha1.hexdigest()

            events.append(payload)

    #pprint(events)
    r = requests.post(server_url + '/data/events',
                      data=json.dumps(events),
                      headers={'content-type': 'application/json'},
                      auth=(server_username, server_password),
                      timeout=10)

    print('DiMe returns:', json.dumps(r.json(), indent=2))

    if r.status_code == requests.codes.ok:
        print('Successfully uploaded', len(r.json()), 'events to DiMe.')
