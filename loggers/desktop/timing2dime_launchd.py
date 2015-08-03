#!/opt/local/bin/python2.7

import os
import sys
import subprocess

from dlog_globals import config
import dlog_conf as conf
import dlog_common as common

plistfilenames = ('timing2dime.plist.template',
                  'timing2dime-status.plist.template')
config_options = ('dimepath', 'logger_interval', 'status_interval')

# -----------------------------------------------------------------------

def run_command(shell_command, devnull=False):
    try:
        if not devnull:
            subprocess.check_call(shell_command, shell=True)
        else:
            FNULL = open(os.devnull, 'w')
            subprocess.check_call(shell_command, shell=True,
                                  stdout=FNULL, stderr=subprocess.STDOUT)
            FNULL.close()
    except subprocess.CalledProcessError:
        print "ERROR: Running command [%s] failed, exiting" % shell_command    

# -----------------------------------------------------------------------

if __name__ == '__main__':

    conf.configure(False)

    for plistfn in plistfilenames:
        outfn = plistfn.replace('.template', '')
        outfn = os.path.expanduser('~/Library/LaunchAgents/' + outfn)
        outfile = open(outfn, 'w')
        with open (plistfn, "r") as plistfile:
            for line in plistfile:
                for config_option in config_options:
                    if not config.has_key(config_option):
                        print 'ERROR: Config key "%s" not set' % config_option
                        sys.exit()
                    line = line.replace('%('+config_option+')s', str(config[config_option]))
                outfile.write(line)
        outfile.close()

        run_command("launchctl unload " + outfn, True)
        run_command("plutil -lint "   + outfn)
        run_command("launchctl load "   + outfn)

    run_command("launchctl list | grep hiit")

# -----------------------------------------------------------------------
