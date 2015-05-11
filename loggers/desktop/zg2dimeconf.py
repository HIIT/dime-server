
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

def process_config_path(p, s, o, key, verbose=True):
    res = process_config_item(p, s, o, key, 'string', False)
    if config.has_key(key):    
        config[key] = os.path.expanduser(config[key])
        if verbose:
            print "  Setting " + key + "=" + config[key]
    return res

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

def process_config_all_string(parser, section, verbose=True):
    if parser.has_section(section):
        items = parser.items(section)
        for it in items:
            config[it[0]] = it[1]
            if verbose:
                print "  Setting " + it[0] + "=" + it[1]

# -----------------------------------------------------------------------

def process_config_dict(parser, section, opt_to_read, opt_to_write,
                        verbose=True):
    if process_config_string(parser, section, opt_to_read, 'tmp', False):
        #print config['tmp']
        item_list = config['tmp'].split(';')
        first = True
        for item in item_list:
            item = item.strip()
            #print item
            item_kv = item.split('->')            
            if len(item_kv)==2:
                #print item_kv[0] +" " + item_kv[1]
                if not config.has_key(opt_to_write):
                    config[opt_to_write] = {}
                config[opt_to_write][item_kv[0]]=item_kv[1]                
                if verbose and first:
                    print "  Setting " + opt_to_write + "=<type 'dict'>"
                first = False
            else:
                print "ERROR: Unable to parse %s/%s: %s" + (section,
                                                            opt_to_read,
                                                            item)
                break
        config.pop('tmp')

# -----------------------------------------------------------------------

def process_blacklist(parser, section, suffix, verbose=True):
    if (process_config_string(parser, section, 'blacklist', 'tmp', False)):
        bl = config['tmp'].split(';')
        first = True
        for bl_item in bl:
            bl_item = bl_item.strip()
            if not config.has_key('blacklist_'+suffix):
                config['blacklist_'+suffix] = set()
            config['blacklist_'+suffix].add(bl_item)
            if verbose and first:
                print "  Setting blacklist_" + suffix + "=<type 'set'>"
            first = False
        config.pop('tmp')

# -----------------------------------------------------------------------

def process_timing_applist(parser, applist, verbose=True):
    if (process_config_string(parser, 'Timing', applist, 'tmp', False)):
        al = config['tmp'].split(';')
        first = True
        for al_item in al:
            al_item = al_item.strip()
            if not config.has_key(applist+'_timing'):
                config[applist+'_timing'] = set()
            config[applist+'_timing'].add(al_item)
            if verbose and first:
                print "  Setting " + applist + "_timing=<type 'set'>"
            first = False
        config.pop('tmp')
        
# -----------------------------------------------------------------------

def process_browser(parser, section, suffix, v=True):

    process_config_boolean(parser, section, 'use', 'use_'+suffix, v)
    process_config_string(parser, section, 'actor', 'actor_'+suffix, v)
    process_config_int(parser, section, 'interval', 'interval_'+suffix, v)
    process_config_path(parser, section, 'history_file', 'history_file_'+suffix, v)
    process_config_string(parser, section, 'tmpfile', 'tmpfile_'+suffix, v)
    process_config_int(parser, section, 'nevents', 'nevents_'+suffix, v)
    process_blacklist(parser, section, suffix, v)
                
# -----------------------------------------------------------------------

def process_config(config_file, v=True):
    print "Processing config file: " + config_file

    if not os.path.isfile(config_file):
        print "ERROR: Config file not found"
        return False

    config_fp = open(config_file)     
    parser = SafeConfigParser()    
    parser.readfp(config_fp)

    # [Ontology]:

    process_config_all_string(parser, 'Ontology', v)
    
    # [General]:

    process_config_string(parser, 'General', 'hostname', 'hostname', v)
    process_config_string(parser, 'General', 'uuid_command', 'uuid_command', v)
    process_config_string(parser, 'General', 'uuid_command_mac', 'uuid_command_mac', v)
    process_config_string(parser, 'General', 'mimetype_command', 'mimetype_command', v)
    process_config_string(parser, 'General', 'pdftotext_command', 'pdftotext_command', v)
    process_config_string(parser, 'General', 'fulltext_command', 'fulltext_command', v)

    process_config_dict(parser, 'General', 'ext_mimetypes', 'ext_to_mimetype', v)
    process_config_dict(parser, 'General', 'ext_types', 'ext_to_type', v)
    
    # [DiMe]:

    process_config_string(parser, 'DiMe', 'server_url', 'server_url', v)
    process_config_int(parser,    'DiMe', 'server_timeout', 'server_timeout', v)
    process_config_string(parser, 'DiMe', 'username', 'username', v)
    process_config_string(parser, 'DiMe', 'password', 'password', v)

    # [Zeitgeist]:

    process_config_boolean(parser, 'Zeitgeist', 'use', 'use_zeitgeist', v)
    process_config_int(parser,     'Zeitgeist', 'nevents', 'nevents', v)
    process_config_boolean(parser, 'Zeitgeist', 'pdftotext', 'pdftotext_zeitgeist', v)
    process_config_int(parser,     'Zeitgeist', 'maxtextlength', 'maxtextlength_zg', v)

    process_config_dict(parser, 'Zeitgeist', 'other_actors', 'actors', v)

    process_blacklist(parser, 'Zeitgeist', 'zeitgeist', v)

    # [Browsers]:

    process_config_boolean(parser, 'Browsers', 'fulltext', 'fulltext', v)
    process_config_int(parser,     'Browsers', 'maxtextlength', 'maxtextlength_web', v)
    process_config_string(parser,  'Browsers', 'event_type', 'event_type_browser', v)
    process_config_string(parser,  'Browsers', 'document_type', 'document_type_browser', v)
    process_config_string(parser,  'Browsers', 'document_isa', 'document_isa_browser', v)

    # [Chrome/Chromium/Firefox]:

    process_browser(parser, 'Chrome', 'chrome', v)
    process_browser(parser, 'Chromium', 'chromium', v)
    process_browser(parser, 'Firefox', 'firefox', v)

    # [Indicator]:

    process_config_boolean(parser, 'Indicator', 'use', 'use_indicator', v)
    process_config_int(parser, 'Indicator', 'interval', 'interval_indicator', v)
    process_config_path(parser, 'Indicator', 'icon', 'icon_indicator', v)

    # [Meetings]:

    process_config_string(parser, 'Meetings', 'event_type', 'event_type_meeting', v)
    process_config_string(parser, 'Meetings', 'document_type', 'document_type_meeting', v)
    process_config_string(parser, 'Meetings', 'document_isa', 'document_isa_meeting', v)

    # [Timing];
    process_config_path(parser, 'Timing', 'applescript_file', 'applescript_file', v)
    process_config_string(parser, 'Timing', 'applescript_command', 'applescript_command', v)
    process_config_path(parser, 'Timing', 'datafile', 'datafile', v)
    process_config_path(parser, 'Timing', 'timingfile', 'timingfile', v)
    process_config_boolean(parser, 'Timing', 'pdftotext', 'pdftotext_timing', v)
    process_config_int(parser,     'Timing', 'maxtextlength', 'maxtextlength_timing', v)
    
    process_timing_applist(parser, 'usage_apps', v)
    process_timing_applist(parser, 'modify_apps', v)

    process_blacklist(parser, 'Timing', 'timing', v)
        
    return True

# -----------------------------------------------------------------------

def configure(verbose=True):

    config['hostname'] = socket.gethostbyaddr(socket.gethostname())[0]

    process_config("default.ini", verbose)
    process_config("user.ini", verbose)

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
