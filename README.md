# Digital Work Me (DiMe) server

The DiMe server can run in your local machine or in a server. Its task
is to collect your personal data from different loggers into a *central
place that you control*.

## Server installation

### Requirements

- Java 7 SDK or newer
- [mongodb][2] (2.4 or newer, although 2.6 or newer is preferred)

If you are running mongodb version 2.4 you have to
[enable the text search feature manually][1] (it's automatically
enabled in newer versions).

### Compile

Clone the git repository, e.g.:

    git clone git@github.com:HIIT/dime-server.git

To compile, run:

    make

This will cause the gradle wrapper script to download any Java
dependencies automatically. Hence it may take a longer the first time.

### Configure

To change the port in which dime-server is running you can edit the
file `config/application.properties` and modify the `server.port`, e.g.

    server.port=8090


### Run

To run the server in port 8080, issue the command:

    make run

This will also re-compile if the source code has changed. The DiMe
server will automatically use a database named "dime" in the mongodb
server. Now you can access the DiMe dashboard by going to the address
<http://localhost:8080>.


## Loggers

This repository currently includes the following loggers:

### Linux desktop logger

- [Installation instructions][3]

[1]: http://docs.mongodb.org/v2.4/tutorial/enable-text-search/
[2]: http://www.mongodb.org/
[3]: https://github.com/HIIT/dime-server/blob/master/loggers/desktop/INSTALL.md
