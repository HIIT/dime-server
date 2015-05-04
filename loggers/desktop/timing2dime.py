#!/opt/local/bin/python2.7

import os.path
import sys
import socket
import subprocess
import time

from zg2dimeglobals import config
import zg2dimeconf as conf
import zg2dimecommon as common

# -----------------------------------------------------------------------

def load_data():
    if not config.has_key('datafile'):
        return None

    if not os.path.isfile(config['datafile']):
        tmp_data = {}
        tmp_data['started'] = int(time.time())
        tmp_data['items'] = []
        tmp_data['executions'] = []
        common.json_dump(tmp_data, config['datafile'])

    if os.path.isfile(config['datafile']):
        return common.json_load(config['datafile'])

    return None

# -----------------------------------------------------------------------

def print_status():
    print
    print ("Initialized on:      "+
           (time.strftime("%Y-%m-%d %H:%M:%S",
                          time.localtime(data['started']))))
    print "Executions:"

    ntotal = 0
    nfailed = 0
    nlasthourtotal = 0
    nlasthourfailed = 0
    ntodaytotal = 0
    ntodayfailed = 0
    latest_timestamp = 0
    latest_msg = ''
    latest_ok_timestamp = 0
    latest_ok_msg = ''
    latest_failed_timestamp = 0
    latest_failed_msg = ''

    now = int(time.time())

    # this is ridiculous:
    a = time.localtime(now)
    b=time.strftime('%Y-%m-%d', a)
    c=time.strptime(b, '%Y-%m-%d')
    today_start = int(time.mktime(c))

    for ex in data['executions']:
        ntotal = ntotal + 1 
        if ex['status']:
            if ex['timestamp'] > latest_ok_timestamp:
                latest_ok_timestamp = ex['timestamp']            
                latest_ok_msg = ex['msg']
        else:
            if ex['timestamp'] > latest_failed_timestamp:
                latest_failed_timestamp = ex['timestamp']            
                latest_failed_msg = ex['msg']
            nfailed = nfailed + 1
        if ex['timestamp'] > latest_timestamp:
            latest_timestamp = ex['timestamp']
            latest_msg = ex['msg']
        if ex['timestamp'] > now - 60*60:
            nlasthourtotal = nlasthourtotal + 1
            if not ex['status']:
                nlasthourfailed = nlasthourfailed + 1
        if ex['timestamp'] > today_start:
            ntodaytotal = ntodaytotal + 1
            if not ex['status']:
                ntodayfailed = ntodayfailed + 1

    print ("  latest:            "+
           '%s ("%s")') % (time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(latest_timestamp)),
                           latest_msg)
    print ("  latest successful: "+
           '%s ("%s")') % (time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.localtime(latest_ok_timestamp)),
                           latest_ok_msg)
    print ("  latest failed:     "+
           '%s ("%s")') % (time.strftime("%Y-%m-%d %H:%M:%S",
                                 time.localtime(latest_failed_timestamp)),
                           latest_failed_msg)
    print ("  total:             "+
           "%d (last hour: %d; today: %d)") % (ntotal, 
                                               nlasthourtotal,
                                               ntodaytotal)
    print ("  failed:            "+
           "%d (last hour: %d; today: %d)") % (nfailed,
                                               nlasthourfailed,
                                               ntodayfailed)

    print "Events sent:"
    ntotal = 0

    for it in data['items']:
        ntotal = ntotal +1 
    print "  total:     %d" % ntotal

    ping_str = "FAILED"
    if check_ping():
        ping_str = "OK"

    notify_msg = ("Total: last hour: %d, today: %d\n" +
                  "Failed: last hour: %d, today: %d - " +
                  "Ping: %s") % (nlasthourtotal, ntodaytotal,
                                 nlasthourfailed, ntodayfailed,
                                 ping_str)

    shell_command = "osascript -e 'display notification \"%s\" with title \"Timing2dime\"'" % notify_msg
    try:
        subprocess.check_call(shell_command, shell=True)
    except subprocess.CalledProcessError:
        print "ERROR: Running AppleScript [%s] failed" % shell_command

# -----------------------------------------------------------------------

def check_ping():
    pingstring = ("Pinging DiMe server at location: " +
                  config['server_url'] + " : ")
    if common.ping_server():
        print pingstring + "OK"
        return True

    print pingstring + "FAILED"
    return False

# -----------------------------------------------------------------------

def run_applescript():
    shell_command = config['applescript_command'] % config['applescript_file']
    try:
        subprocess.check_call(shell_command, shell=True)
        return True
    except subprocess.CalledProcessError:
        print "ERROR: Running AppleScript [%s] failed, exiting" % shell_command

    return False

# -----------------------------------------------------------------------

def get_uuid():
    try:
        uuid = subprocess.check_output(config['uuid_command_mac'], shell=True)
        return uuid.rstrip()
    except subprocess.CalledProcessError:
        return 'unknown'

# -----------------------------------------------------------------------

def exit(status, msg=None):
    data['executions'].append({'timestamp': int(time.time()),
                               'status': status,
                               'msg': msg})
    common.json_dump(data, config['datafile'])
    sys.exit()

# -----------------------------------------------------------------------

if __name__ == '__main__':

    print "------------------------------------------------------------------------------"
    print "Starting the timing2dime.py logger on " + time.strftime("%c")
    print "------------------------------------------------------------------------------"

    conf.configure(False)

    debug = False
    statusmode = False
    forced_id = None
    if len(sys.argv)>1:
        if sys.argv[-1] == 'debug':
            config['server_url'] = 'http://httpbin.org/post'
            config['nevents'] = 1
            debug = True
        elif sys.argv[-1] == 'status':
            statusmode = True
        else:
            forced_id = sys.argv[-1]

    data = load_data()
    if data is None:
        print "ERROR: Failed to initialize [%s], exiting" % config['datafile']
        sys.exit()

    if statusmode:
        print_status()
        sys.exit()

    if not check_ping():
        print "Ping failed, exiting"
        exit(False, "ping failed")

    if not run_applescript():
        exit(False, "running AppleScript failed")

    uuid = get_uuid()

    if not os.path.isfile(config['timingfile']):
        print "ERROR: File not found [%s], exiting" % config['timingfile']
        exit(False, config['timingfile']+' not found')
    with open(config['timingfile']) as timingfile:
        timing_data_txt = timingfile.read()
    timing_id = common.str_to_sha1(timing_data_txt)
    timing_data_json = common.json_loads(timing_data_txt)

    if data.has_key('timingfile_id') and timing_id == data['timingfile_id']:
        print "Timing data file not changed (id=[%s]), exiting" % timing_id
        exit(True, "timing data not changed")
    data['timingfile_id'] = timing_id

    i = 0; j = 0
    for timing_item in timing_data_json:

        j=j+1
        item_id = common.to_json_sha1(timing_item)

        if forced_id is not None and item_id != forced_id:
            continue

        if forced_id is None:
            known_item = False
            for di in data['items']:
                if di['id'] == item_id:
                    known_item = True
                    break
            if known_item:
                print "Timing data item [%s] already sent to DiMe, skipping" % item_id
                continue

        item_appl = timing_item[u'application']

        recognized_app = False
        if (item_appl in config['modify_apps_timing']):
            recognized_app = True
            event_interpretation = config['zg_i_modifyevent']
        elif (item_appl in config['access_apps_timing']):
            recognized_app = True
            event_interpretation = config['zg_i_accessevent']

        if not recognized_app:
            print "Application [%s] is not recognized, skipping" % item_appl
            continue

        subject_interpretation = config['sd_i_document']
        subject_manifestation  = config['sd_m_localfiledataobject']

        item_path = timing_item[u'path']
        if common.blacklisted(item_path, 'blacklist_timing'):
            continue
        if (len(item_path)<=0 or item_path.startswith('*') or
            item_path.startswith('.') or item_path.startswith('[')):
            print "Item_path [%s] is not looking correct, skipping" % item_path
            continue
        path_end = item_path.find(' [')
        if path_end<0:
            path_end = item_path.find(' (')
        if path_end>0:
            item_path = item_path[0:path_end]

        storage = 'deleted'
        mimetype = 'unknown'
        uri_prefix = 'file://'
        text = ''

        if os.path.isfile(item_path):
            storage = 'local'
            mimetype = common.get_mimetype(item_path)

            if mimetype == 'application/pdf':
                subject_interpretation = config['sd_i_paginatedtextdocument']
                if config.has_key('pdftotext_timing') and config['pdftotext_timing']:
                    text = common.pdf_to_text(item_path)
            if mimetype == 'application/zip':
                extension = os.path.splitext(item_path)[1]
                if (config.has_key('ext_to_mimetype') and
                    extension in config['ext_to_mimetype']):
                    mimetype = config['ext_to_mimetype'][extension]
                if (config.has_key('ext_to_interpretation') and
                    extension in config['ext_to_interpretation']):
                    subject_interpretation = eval("config['" +
                                                  config['ext_to_interpretation'][extension] +
                                                  "']")
            elif 'text/' in mimetype:
                if mimetype == 'text/x-python':
                    subject_interpretation = config['sd_i_sourcecode']
                else:
                    subject_interpretation = config['sd_i_plaintextdocument']
                with open (item_path, "r") as myfile:
                    text = myfile.read()

        elif item_appl == u'Evernote':
            storage = 'internal'
            uri_prefix = 'evernote://'

        elif item_appl == u'Google Chrome':
            subject_manifestation  = config['sd_m_remotefiledataobject']
            storage = 'net'
            uri_prefix = ''
            text = common.uri_to_text(item_path)

        print "Submitting: %s [%s]" % (timing_item, item_id)
        sd = timing_item[u'startDate']
        item_datetime = u'20'+sd[6:8]+u'-'+sd[3:5]+u'-'+sd[0:2]+u'T'+sd[9:11]+u':'+sd[12:14]+u':00+03:00'
        #print "[%s] => [%s]" % (sd, item_datetime)

        payload = {'origin':                 config['hostname'],
                   'actor':                  item_appl,
                   'interpretation':         event_interpretation,
                   'manifestation':          config['zg_m_useractivity'],
                   'timestamp':              item_datetime}
            
        subject = {'uri':            uri_prefix + item_path,
                   'interpretation': subject_interpretation,
                   'manifestation':  subject_manifestation,
                   'mimetype':       mimetype,
                   'storage':        storage}

        subject['id'] = common.to_json_sha1(subject)
        payload['subject'] = {}
        payload['subject']['id'] = subject['id']
        payload['id'] = common.to_json_sha1(payload)
        subject['text'] = text
        payload['subject'] = subject.copy()

        json_payload = common.payload_to_json(payload)
        if (json_payload == ''):
            print "Something went wrong in JSON conversion, skipping"
            continue
        print "PAYLOAD: " + str(type(json_payload))
        print json_payload

        r = common.post_json(json_payload)
        if r is None:
            break

        print "RESPONSE: " + str(type(r.text))
        try: 
            print r.text.encode('utf-8')
        except UnicodeEncodeError:
            print "<UnicodeEncodeError>"
        print "---------------------------------------------------------"

        i = i+1

        if r.status_code != common.requests.codes.ok:
            print "Post to DiMe failed: error=[%s], message=[%s]" % (r.json()['error'],
                                                                     r.json()['message'])
            break

        data_item = {'id': item_id,
                     'item' : timing_item,
                     'response': {'id': r.json()['id'],
                                  'time_created': r.json()['time_created'],
                                  'time_modified': r.json()['time_modified']}}

        data['items'].append(data_item)            
                         
        if debug:
            break

    print "Processed %d entries, submitted %s entries" % (j, i)

    exit(True, "all ok") 

# -----------------------------------------------------------------------
