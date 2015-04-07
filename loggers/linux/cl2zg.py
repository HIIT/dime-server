#!/usr/bin/env python

# Examples of entries to .bashrc:
#
# less () {
#     /PATH-TO-DIME/dime-server/loggers/linux/cl2zg.py less "$@"
#     command less "$@"
# }
#
# cat () {
#     /PATH-TO-DIME/loggers/linux/cl2zg.py cat "$@"
#     command cat "$@" 
# }


import sys
import os
import subprocess

from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import *

if len(sys.argv)<3:
    sys.exit()

shell_command = 'which "%s"' % sys.argv[1]
try:
    _actor = subprocess.check_output(shell_command, 
                                     shell=True)
    _actor = _actor.rstrip()                    
except subprocess.CalledProcessError:
    _actor = sys.argv[1]

for su in sys.argv[2:]:

    _subject_uri = os.path.abspath(su)

    if not os.path.isfile(_subject_uri):
        continue
    
    zeitgeist = ZeitgeistClient()

    event = Event.new_for_values(actor=_actor,
                                 interpretation=Interpretation.ACCESS_EVENT,
                                 manifestation=Manifestation.USER_ACTIVITY,
                                 subject_uri="file://"+_subject_uri,
                                 subject_interpretation=Interpretation.DOCUMENT,
                                 subject_manifestation=Manifestation.FILE_DATA_OBJECT, 
                                 subject_origin="",
                                 subject_current_origin="", 
                                 subject_mimetype="unknown", 
                                 subject_storage="", 
                                 subject_text="")

    zeitgeist.insert_event(event)

#
