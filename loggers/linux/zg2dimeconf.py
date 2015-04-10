
import os.path
import socket
from ConfigParser import SafeConfigParser

from zg2dimeglobals import config

# -----------------------------------------------------------------------

def process_config_item(parser, section, option, key, mode, verbose):
    if parser.has_section(section) and parser.has_option(section, option):
        if mode == 'int':
            val = parser.getint(section, option)
            valstr = str(val)
        elif mode == 'boolean':
            val = parser.getboolean(section, option)
            valstr = str(val)
        else:
            valstr = val = parser.get(section, option)
        config[key] = val
        if verbose:
            print "  Setting " + key + "=" + valstr
        return True
    return False

# -----------------------------------------------------------------------

def process_config_path(p, s, o, key, v=True):
    val = process_config_item(p, s, o, key, 'string', v)
    if config.has_key(key):
        config[key] = os.path.expanduser(config[key])
    return val

# -----------------------------------------------------------------------

def process_config_string(p, s, o, k, v=True):
    return process_config_item(p, s, o, k, 'string', v)

# -----------------------------------------------------------------------

def process_config_int(p, s, o, k, v=True):
    return process_config_item(p, s, o, k, 'int', v)

# -----------------------------------------------------------------------

def process_config_boolean(p, s, o, k, v=True):
    return process_config_item(p, s, o, k, 'boolean', v)

# -----------------------------------------------------------------------

def process_blacklist(parser, section, suffix):
    if (process_config_string(parser, section, 'blacklist', 'tmp')):
        bl = config['tmp'].split(';')
        for bl_item in bl:
            bl_item = bl_item.strip()
            if not config.has_key('blacklist_'+suffix):
                config['blacklist_'+suffix] = set()
            config['blacklist_'+suffix].add(bl_item)
        config.pop('tmp')

# -----------------------------------------------------------------------

def process_browser(parser, section, suffix):

    process_config_boolean(parser, section, 'use', 'use_'+suffix)
    process_config_string(parser, section, 'actor', 'actor_'+suffix)
    process_config_int(parser, section, 'interval', 'interval_'+suffix)
    process_config_path(parser, section, 'history_file', 'history_file_'+suffix)
    process_config_string(parser, section, 'tmpfile', 'tmpfile_'+suffix)
    process_config_int(parser, section, 'nevents', 'nevents_'+suffix)
    process_blacklist(parser, section, suffix)
                
# -----------------------------------------------------------------------

def process_config(config_file):
    print "Processing config file: " + config_file

    if not os.path.isfile(config_file):
        print "ERROR: Config file not found"
        return False

    config_fp = open(config_file)     
    parser = SafeConfigParser()    
    parser.readfp(config_fp)

    # [General]:

    process_config_string(parser, 'General', 'hostname', 'hostname')

    # [DiMe]:

    process_config_string(parser, 'DiMe', 'server_url', 'server_url')
    process_config_string(parser, 'DiMe', 'username', 'username')
    process_config_string(parser, 'DiMe', 'password', 'password')

    # [Zeitgeist]:

    process_config_boolean(parser, 'Zeitgeist', 'use', 'use_zeitgeist')
    process_config_int(parser, 'Zeitgeist', 'nevents', 'nevents')
    process_config_boolean(parser, 'Zeitgeist', 'pdftotext', 'pdftotext')
    process_config_string(parser, 'Zeitgeist', 'pdftotext_command', 'pdftotext_command')
    process_config_int(parser, 'Zeitgeist', 'maxtextlength', 'maxtextlength_zg')
    process_config_string(parser, 'Zeitgeist', 'uuid_command', 'uuid_command')
    process_config_string(parser, 'Zeitgeist', 'mimetype_command', 'mimetype_command')

    if (process_config_string(parser, 'Zeitgeist', 'other_actors', 'tmp')):
        #print config['tmp']
        oa_list = config['tmp'].split(';')
        for oa in oa_list:
            oa = oa.strip()
            #print oa
            oa_kv = oa.split('->')            
            if len(oa_kv)==2:
                #print oa_kv[0] +" " + oa_kv[1]
                if not config.has_key('actors'):
                    config['actors'] = {}
                config['actors'][oa_kv[0]]=oa_kv[1]                
            else:
                print "ERROR: Unable to parse Zeitgeist/other_actors: " + oa
        config.pop('tmp')

    process_blacklist(parser, 'Zeitgeist', 'zeitgeist')

    # [Browsers]:

    process_config_boolean(parser, 'Browsers', 'fulltext', 'fulltext')
    process_config_string(parser, 'Browsers', 'fulltext_command', 'fulltext_command')
    process_config_int(parser, 'Browsers', 'maxtextlength', 'maxtextlength_web')
    process_config_string(parser, 'Browsers', 'event_interpretation', 'event_interpretation_browser')
    process_config_string(parser, 'Browsers', 'event_manifestation', 'event_manifestation_browser')
    process_config_string(parser, 'Browsers', 'subject_interpretation', 'subject_interpretation_browser')
    process_config_string(parser, 'Browsers', 'subject_manifestation', 'subject_manifestation_browser')

    # [Chrome/Chromium/Firefox]:

    process_browser(parser, 'Chrome', 'chrome')
    process_browser(parser, 'Chromium', 'chromium')
    process_browser(parser, 'Firefox', 'firefox')

    # [Indicator]:

    process_config_boolean(parser, 'Indicator', 'use', 'use_indicator')
    process_config_int(parser, 'Indicator', 'interval', 'interval_indicator')
    process_config_path(parser, 'Indicator', 'icon', 'icon_indicator')

    # [Meetings]:
    process_config_string(parser, 'Meetings', 'event_interpretation', 'event_interpretation_meeting')
    process_config_string(parser, 'Meetings', 'event_manifestation', 'event_manifestation_meeting')
    process_config_string(parser, 'Meetings', 'subject_interpretation', 'subject_interpretation_meeting')
    process_config_string(parser, 'Meetings', 'subject_manifestation', 'subject_manifestation_meeting')

    return True

# -----------------------------------------------------------------------

def configure():

    config['hostname'] = socket.gethostbyaddr(socket.gethostname())[0]

    process_config("zg2dime.ini")
    process_config("user.ini")

    return True

# -----------------------------------------------------------------------

def parse_desktop_file(desktop_file, oldval):
    parser = SafeConfigParser()
    parser.read(desktop_file)
    if parser.has_section('Desktop Entry') and parser.has_option('Desktop Entry', 'Name'):
        return parser.get('Desktop Entry', 'Name')
    else:
        return oldval

# -----------------------------------------------------------------------
