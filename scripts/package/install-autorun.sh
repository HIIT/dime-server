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
    DIME_INSTALL_DIR="$HOME/.dime/bin"
fi

if [ ! -f "dime-server.jar" -o ! -f "run-dime.sh" ]; then
    echo "ERROR: you should run this script in the same directory where you extracted the DiMe files."
    exit 1
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    INIT_SYSTEM=launchd
elif [[ "$OSTYPE" == "linux-gnu" ]]; then
    if [ ! -z "$XDG_SESSION_ID" ]; then
        INIT_SYSTEM=xdg
    elif hash systemctl 2>/dev/null; then
        INIT_SYSTEM=systemd
    fi
fi

if [ -z "$INIT_SYSTEM" ]; then
    echo "Sorry, your platform isn't supported for autorun yet."
    echo "You'll have to start DiMe manually from this directory by running:"
    echo
    echo "./run-dime.sh"
    exit 1
fi

echo "Installing DiMe into $DIME_INSTALL_DIR ..."
mkdir -p $DIME_INSTALL_DIR || exit 1
echo

# Copy jar
cp dime-server.jar $DIME_INSTALL_DIR

# Copy run script
DIME_SH=${DIME_INSTALL_DIR}/run-dime.sh
sed "s;DIME_INSTALL_DIR=\.;DIME_INSTALL_DIR=$DIME_INSTALL_DIR;" run-dime.sh > $DIME_SH
chmod a+x $DIME_SH

# Install auto-run depending on platform
if [[ "$INIT_SYSTEM" = "launchd" ]]; then
    echo "Mac OS X detected, installing launchd script."
    
    if [[ ! -e "$HOME/Library/LaunchAgents" ]]; then
    	echo "~/Library/LaunchAgents folder not found, it will be created"
    	mkdir "$HOME/Library/LaunchAgents"
    fi

    LAUNCHD_TARGET="$HOME/Library/LaunchAgents/dime-server.plist"
    sed "s;\$DIME_INSTALL_DIR;$DIME_INSTALL_DIR;" install/dime-server.plist > $LAUNCHD_TARGET

    launchctl unload ${LAUNCHD_TARGET} 2> /dev/null
    plutil -lint ${LAUNCHD_TARGET}
    launchctl load ${LAUNCHD_TARGET}

    launchctl list | grep dime-server
    echo
    echo "DiMe should now start automatically when you start your computer."
    echo "If you ever wish to disable this, just run:"
    echo
    echo "rm ${LAUNCHD_TARGET}"

elif [[ "$INIT_SYSTEM" == "xdg" ]]; then
    echo "Detected XDG compliant desktop environment."

    CONFIG_DIR="${HOME}/.config/autostart"
    CONFIG_FILE="${CONFIG_DIR}/dime-server.desktop"
    
    mkdir -p ${CONFIG_DIR}

    sed "s;\$DIME_INSTALL_DIR;$DIME_INSTALL_DIR;" install/dime-server.desktop > $CONFIG_FILE

    echo
    echo "DiMe should now start automatically when you start your computer."
    echo "If you ever wish to disable this, just run:"
    echo
    echo "    rm ${CONFIG_FILE}"
    echo

elif [[ "$INIT_SYSTEM" == "systemd" ]]; then
    echo "Detected systemd services system."
    echo
    
    SYSTEMD_DIR="${HOME}/.config/systemd"
    SYSTEMD_CONF="${SYSTEMD_DIR}/user/dime-server.service"
    
    mkdir -p ${SYSTEMD_DIR}/user
    
    echo "Installing $SYSTEMD_CONF ..."
    sed "s;\$DIME_INSTALL_DIR;$DIME_INSTALL_DIR;" install/dime-server.service > $SYSTEMD_CONF

    systemctl --user enable dime-server.service
    systemctl --user start dime-server

    systemctl --user status dime-server
    
    echo
    echo "DiMe should now start automatically when you start your computer."
    echo "If you ever wish to disable this, just run:"
    echo
    echo "    systemctl --user disable dime-server"
    echo
    echo "To stop the dime-server (without affecting autostart):"
    echo "    systemctl --user stop dime-server"
    echo "and start again:"
    echo "    systemctl --user start dime-server"
    echo
fi
