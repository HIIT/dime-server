#!/bin/bash

# If you need to change the server port, uncomment the following line
# and change the port number.
#
# export SERVER_PORT=8080

DIME_INSTALL_DIR=.

java -jar $DIME_INSTALL_DIR/dime-server.jar
