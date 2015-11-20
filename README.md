# Digital Work Me (DiMe) server

The DiMe server can run in your local machine or in a server. Its task
is to collect your personal data from different loggers into a central
place that you control.

You can install DiMe directly on your machine (instructions below), or
if you are adventurous test the experimental
[Docker virtualisation](https://github.com/HIIT/dime-server/wiki/Docker).
support. For people intending to develop, it is probably easier to
install it directly.

## Installation

### Requirements

- [Java 7 JDK][1] or newer (i.e. Java version 1.7 or newer)

### Compiling

Clone the git repository, e.g.:

    git clone https://github.com/HIIT/dime-server.git

To compile run:

    make

(If you don't have GNU Make, for example on Windows you will have to
use gradle directly instead of the Makefile wrapper: `./gradlew
assemble`.)

On the first compilation, gradle will download any Java dependencies
automatically. Hence it may take a bit longer the first time.

### Running

To run the server in port 8080 issue the command:

    make run

(Or `./gradlew run` if you don't have GNU Make.)

If you wish to change the TCP port of the server take a look at how to
[configure the DiMe server][2] to use another port.

The DiMe server will put all its files, such as the database and
Lucene search index under `~/.dime` in your home directory.

Now you can access the DiMe dashboard by going to the address
<http://localhost:8080>.

When you run DiMe the first time it will automatically create an
`admin` user and show its randomly generated password in the command
line.

## Documentation

The [project wiki page] has more detailed instructions and
documentation of the API and development.

If you have any questions, don't hesitate to contact the lead
developer [Mats Sjöberg](mailto:mats.sjoberg@helsinki.fi).

[1]: http://www.oracle.com/technetwork/java/javase/downloads/index.html
[2]: https://github.com/HIIT/dime-server/wiki/Configuration
[3]: https://github.com/HIIT/dime-server/wiki
