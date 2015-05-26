# Digital Work Me (DiMe) server

The DiMe server can run in your local machine or in a server. Its task
is to collect your personal data from different loggers into a central
place that you control.

## Server installation

### Requirements

- [Java 7 JDK][4] or newer (i.e. Java version 1.7 or newer)
- [mongodb][2] (2.4 or newer, although 2.6 or newer is preferred)

If you are running mongodb version 2.4 you have to
[enable the text search feature manually][1] (it's automatically
enabled in newer versions).

In Linux it is recommended to install the requirements through a
package manager if possible, e.g. for Ubuntu or Debian:

    sudo apt-get install mongodb openjdk-7-jdk

on Mac OS X, use either Homebrew or Macports:

    brew install mongod
    sudo port install mongodb

On Mac OS X you also need to remember to start mongod, e.g.

    mkdir ~/mongodata
    mongod --dbpath ~/mongodata/

### Compile

Clone the git repository, e.g.:

    git clone https://github.com/HIIT/dime-server.git

To compile, run:

    make

The `Makefile` is just a wrapper around `gradle` which does all the
work. The first time you run `make` it will download any Java
dependencies automatically. Hence it may take a bit longer the first
time.

### Configure

If you wish to change the port in which dime-server is running you can
edit the file `config/application.properties` and modify the
`server.port`, the default is:

    server.port=8080


### Run

To run the server, issue the command:

    make run

This will also re-compile if the source code has changed since last
compilation. The DiMe server will automatically use a database named
"dime" in the mongodb server.

Now you can access the DiMe dashboard by going to the address
<http://localhost:8080> (if you are using the default port).

When you run DiMe the first time it will automatically create an
`admin` user and show its randomly generated password in the command
line.

## Loggers

This repository currently includes the following loggers:

### Linux desktop logger

- [Installation instructions][3]

### Mac desktop logger

- [Installation instructions][5]

[1]: http://docs.mongodb.org/v2.4/tutorial/enable-text-search/
[2]: http://www.mongodb.org/
[3]: https://github.com/HIIT/dime-server/wiki/Linux-desktop
[4]: http://www.oracle.com/technetwork/java/javase/downloads/index.html
[5]: https://github.com/HIIT/dime-server/wiki/Mac-desktop
[6]: http://brew.sh/
[7]: https://www.macports.org/
