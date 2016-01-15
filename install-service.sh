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

DIME_INSTALL_DIR="$PWD"

# Install common binary
function install_bin {
    DIME_SH=${DIME_INSTALL_DIR}/run-dime.sh

    echo "Installing $DIME_SH ..."
    sed "s;\$DIME_INSTALL_DIR;$DIME_INSTALL_DIR;" \
        ${DIME_INSTALL_DIR}/scripts/upstart/run-dime.sh > $DIME_SH
    chmod a+x $DIME_SH
}

if hash systemctl 2>/dev/null
then 
    echo "Systemd found."
elif hash initctl 2>/dev/null
then
    echo "Detected upstart services system (older Ubuntus).";
    echo
    UPSTART_DIR="${HOME}/.config/upstart"
    UPSTART_CONF="${UPSTART_DIR}/dime-server.conf"

    mkdir -p $UPSTART_DIR
    echo "Installing $UPSTART_CONF ..."
    sed "s;\$DIME_INSTALL_DIR;$DIME_INSTALL_DIR;" \
        ${DIME_INSTALL_DIR}/scripts/upstart/dime-server.conf > $UPSTART_CONF

    install_bin

    echo
    echo "You can now start dime-server by running:"
    echo "    start dime-server"
    echo "and stop by:"
    echo "    stop dime-server"
    echo
    echo "Next time you restart your computer dime-server should start up automatically."
    echo

else
    echo "Nothing found.";
fi
