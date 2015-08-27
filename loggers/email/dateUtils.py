from datetime import datetime
from datetime import timedelta, tzinfo
import numpy as np
import pandas as pd
class FixedOffset(tzinfo):
    """Fixed offset in minutes: `time = utc_time + utc_offset`."""
    def __init__(self, offset):
        self.__offset = timedelta(minutes=offset)
        hours, minutes = divmod(offset, 60)
        #NOTE: the last part is to remind about deprecated POSIX GMT+h timezones
        #  that have the opposite sign in the name;
        #  the corresponding numeric value is not used e.g., no minutes
        self.__name = '<%+03d%02d>%+d' % (hours, minutes, -hours)
    def utcoffset(self, dt=None):
        return self.__offset
    def tzname(self, dt=None):
        return self.__name
    def dst(self, dt=None):
        return timedelta(0)
    def __repr__(self):
        return 'FixedOffset(%d)' % (self.utcoffset().total_seconds() / 60)

def getDateTime_numpy(date_str):
    if ('(' in date_str):
        date_str, _, offset_str = date_str.rpartition(' ')
    if(len(date_str) <30):
        naive_date_str, _, offset_str = date_str.rpartition(' ')
        naive_dt = datetime.strptime(naive_date_str, '%d %b %Y %H:%M:%S')
        offset = int(offset_str[-4:-2])*60 + int(offset_str[-2:])
        if offset_str[0] == "-":
            offset = -offset
        dt = naive_dt.replace(tzinfo=FixedOffset(offset))
        return (np.datetime64(dt))
    naive_date_str, _, offset_str = date_str.rpartition(' ')
    naive_dt = datetime.strptime(naive_date_str, '%a, %d %b %Y %H:%M:%S')
    offset = int(offset_str[-4:-2])*60 + int(offset_str[-2:])
    if offset_str[0] == "-":
       offset = -offset
    dt = naive_dt.replace(tzinfo=FixedOffset(offset))
    return (np.datetime64(dt))

def getMedian(lis):
    if(len(lis) >0):
        m = pd.Series(lis)
        return m.median()
    else:
        return 0

def getMean(lis):
    if(len(lis) >0):
        m = pd.Series(lis)
        return m.mean()
    else:
        return 0

def getThreadLevelTemporal(ids, user_em_id, sub):
    ret = {
    'initiator': '', 
    'No_messages_user': 0, 
    'No_messages_peer': 0, 
    'user_response_times': [], 
    'peer_response_times': [],
    }
    no_user = 0
    no_peer = 0
    user_response_times = []
    peer_response_times = []
    last_mail_sent_by = ''
    last_time_user = None
    last_time_peer = None
    ret['initiator'] = ids.ix[0]._From
    for j in range(0, len(ids.index)):
        if(ids.ix[j]._From == user_em_id):
            no_user = no_user+1
            if(last_mail_sent_by == 'peer'):
                if(last_time_peer is not None):
                    resp = pd.to_datetime(ids.ix[j].Date) - last_time_peer
                    #print pd.to_datetime(ids.ix[j].Date),  last_time_peer, resp
                    user_response_times.append(resp)
                    #last_time_user = pd.to_datetime(ids.ix[j].Date)
            #if(last_time_user is None):
                    #print ids.ix[j].Date
                    #last_time_user = pd.to_datetime(ids.ix[j].Date)
            last_time_user = pd.to_datetime(ids.ix[j].Date)
            last_mail_sent_by = 'user'
        else:
            no_peer = no_peer+1
            if(last_mail_sent_by == 'user'):
                if(last_time_user is not None):
                    resp = pd.to_datetime(ids.ix[j].Date) - last_time_user
                    #print pd.to_datetime(ids.ix[j].Date),  last_time_user, resp
                    peer_response_times.append(resp)
                    #last_time_peer = pd.to_datetime(ids.ix[j].Date)
            #if(last_time_peer is None):
                    #print ids.ix[j].Date
                    #last_time_peer = pd.to_datetime(ids.ix[j].Date)
            last_time_peer = pd.to_datetime(ids.ix[j].Date)
            last_mail_sent_by = 'peer'
 
    ret['No_messages_user'] = no_user
    ret['No_messages_peer'] = no_peer
    ret['user_response_times'] = user_response_times
    ret['peer_response_times'] = peer_response_times
    return ret

#dat = 'Tue, 23 Jun 2015 13:33:44 +0300'
#dt = getDateTime(dat)
#dt64 = np.datetime64(dt)
