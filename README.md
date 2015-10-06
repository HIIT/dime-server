# Digital Work Me (DiMe) server

The DiMe server can run in your local machine or in a server. Its task
is to collect your personal data from different loggers into a central
place that you control.

You can install DiMe directly on your machine (instructions below), or
[use Docker virtualisation](https://github.com/HIIT/dime-server/wiki/Docker).
Docker support is still very experimental, but might be easier if you
don't intend to develop much on DiMe.

## Server installation

### Requirements

- [Java 7 JDK][4] or newer (i.e. Java version 1.7 or newer)
- [mongodb][2] (2.4 or newer, although 2.6 or newer is preferred)

If you are running mongodb version 2.4 you have to
[enable the text search feature manually][1] (it's automatically
enabled in newer versions).

#### Linux

In Linux it is recommended to install the requirements through a
package manager if possible, e.g. for Ubuntu or Debian:

    sudo apt-get install mongodb openjdk-7-jdk

On Ubuntu 14.04, it might be a good idea to update mongodb to a 
more recent version with [these instructions][8].

#### OS X

To install mongodb on Mac OS X, use either Homebrew, Macports or
install manually.

##### Homebrew and manual install

See: <http://docs.mongodb.org/manual/tutorial/install-mongodb-on-os-x/>

##### Macports
    
    sudo port install mongodb
    sudo port load mongodb      # to start automatically

#### Windows

Install mongodb with [these instructions][9].

### Compile

Clone the git repository, e.g.:

    git clone https://github.com/HIIT/dime-server.git

To compile run:

    ./gradlew build

(In Linux and Mac you can also use `make`, which is just a wrapper
around gradle.)

On the first compilation, gradle will download any Java dependencies
automatically. Hence it may take a bit longer the first time.

### Configure

If you wish to change the default configuration, you need to create a
file `config/application.properties`. The easiest way is to copy the
`config/application.properties.example` that is included in this git
repository. Some of the most common configuration options are
explained below.

#### TCP port

The default TCP port where the DiMe server runs is 8080, you can
change this with the `server.port` setting.

    server.port=8080

#### Lucene search

If you wish to use Lucene indexing for (much) better text search
results, you currently have to enable it manually by setting the
`dime.useLucene` option to `true`. There is also a
`dime.luceneIndexPath` which is the directory where the index will be
generated:

    dime.useLucene=true
    dime.luceneIndexPath=${user.home}/dime-lucene

### Run

To run the server issue the command:

    ./gradlew run

(Or `make run` if you prefer on Linux/Mac.)

The DiMe server will automatically use a database named "dime" in the
mongodb server.

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

### Cross-platform browser history logger

- [Installation instructions][10]


[1]: http://docs.mongodb.org/v2.4/tutorial/enable-text-search/
[2]: http://www.mongodb.org/
[3]: https://github.com/HIIT/dime-server/wiki/Linux-desktop
[4]: http://www.oracle.com/technetwork/java/javase/downloads/index.html
[5]: https://github.com/HIIT/dime-server/wiki/Mac-desktop
[6]: http://brew.sh/
[7]: https://www.macports.org/
[8]: http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/
[9]: http://docs.mongodb.org/manual/tutorial/install-mongodb-on-windows/
[10]: https://github.com/HIIT/dime-server/wiki/Browser-logger
