
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

def process_config_string(p, s, o, k, v=True):
    return process_config_item(p, s, o, k, 'string', v)

# -----------------------------------------------------------------------

def process_config_int(p, s, o, k, v=True):
    return process_config_item(p, s, o, k, 'int', v)

# -----------------------------------------------------------------------

def process_config_boolean(p, s, o, k, v=True):
    return process_config_item(p, s, o, k, 'boolean', v)

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

    # [Zeitgeist]:

    process_config_boolean(parser, 'Zeitgeist', 'use', 'use_zeitgeist')
    process_config_int(parser, 'Zeitgeist', 'nevents', 'nevents')

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

    # [Chrome]:

    process_config_boolean(parser, 'Chrome', 'use', 'use_chrome')
    process_config_string(parser, 'Chrome', 'actor', 'actor_chrome')
    process_config_int(parser, 'Chrome', 'interval', 'interval_chrome')
    process_config_string(parser, 'Chrome', 'history_file', 'history_file_chrome')
    process_config_string(parser, 'Chrome', 'tmpfile', 'tmpfile_chrome')
    process_config_int(parser, 'Chrome', 'nevents', 'nevents_chrome')
    process_config_int(parser, 'Chrome', 'maxtextlength', 'maxtextlength_chrome')

    if (process_config_string(parser, 'Chrome', 'blacklist', 'tmp')):
        bl = config['tmp'].split(';')
        for bl_item in bl:
            bl_item = bl_item.strip()
            if not config.has_key('blacklist_chrome'):
                config['blacklist_chrome'] = set()
            config['blacklist_chrome'].add(bl_item)
        config.pop('tmp')

    # [Chromium]:

    process_config_boolean(parser, 'Chromium', 'use', 'use_chromium')
    process_config_string(parser, 'Chromium', 'actor', 'actor_chromium')
    process_config_int(parser, 'Chromium', 'interval', 'interval_chromium')
    process_config_string(parser, 'Chromium', 'history_file', 'history_file_chromium')
    process_config_string(parser, 'Chromium', 'tmpfile', 'tmpfile_chromium')
    process_config_int(parser, 'Chromium', 'nevents', 'nevents_chromium')
    process_config_int(parser, 'Chrome', 'maxtextlength', 'maxtextlength_chromium')
                
    return True

# -----------------------------------------------------------------------

def configure():

    config['hostname'] = socket.gethostbyaddr(socket.gethostname())[0]

    process_config("zg2dime.ini")
    process_config("user.ini")

    return True

# -----------------------------------------------------------------------
