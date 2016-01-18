#!/bin/bash
#
# Copyright (c) 2015 University of Helsinki
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

if [ -z "$DIME_INSTALL_DIR" ]; then
    DIME_INSTALL_DIR="$HOME/dime"
fi

if [ ! -f "dime-server.jar" -o ! -f "run-dime.sh" ]; then
    echo "ERROR: you should run this script in the same directory where you extracted the DiMe files."
    echo "That directory should contain for example: dime-server.jar run-dime.sh"
    exit 1
fi

echo "Installing DiMe into $DIME_INSTALL_DIR ..."

mkdir -p $DIME_INSTALL_DIR || exit 1
cp dime-server.jar $DIME_INSTALL_DIR

DIME_SH=${DIME_INSTALL_DIR}/run-dime.sh
sed "s;\$DIME_INSTALL_DIR;$DIME_INSTALL_DIR;" run-dime.sh > $DIME_SH
chmod a+x $DIME_SH

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Mac OS X detected, installing launchd script."

    LAUNCHD_TARGET="$HOME/Library/LaunchAgents/dime-server.plist"
    sed "s;\$DIME_INSTALL_DIR;$DIME_INSTALL_DIR;" init/dime-server.plist > $LAUNCHD_TARGET

    launchctl unload ${LAUNCHD_TARGET}
    plutil -lint ${LAUNCHD_TARGET}
    launchctl load ${LAUNCHD_TARGET}

    launchctl list | grep hiit

# elif [[ "$OSTYPE" == "linux-gnu" ]]; then
    
# else

fi
