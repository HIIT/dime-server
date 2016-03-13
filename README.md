# Digital Work Me (DiMe) server

The DiMe server can run in your local machine or in a server. Its task
is to collect your personal data from different loggers into a central
place that you control.

You can install DiMe directly on your machine (instructions below), or
if you are adventurous test the experimental
[Docker virtualisation](https://github.com/HIIT/dime-server/wiki/Docker)
support. For people intending to develop, it is probably easier to
install it directly.

## Installation

### Requirements

[Java 7 JDK][1] or newer (i.e. Java version 1.7 or newer) is required.

For Mac OS X you need to have
[Xcode](https://developer.apple.com/xcode/) installed first. You can
install it from the Apple Mac App Store.

### Compiling

First, clone the git repository, for example via the command line:

    git clone https://github.com/HIIT/dime-server.git

To compile, just run:

    make

(If you don't have GNU Make installed you can also use [gradle][4]
directly: `./gradlew assemble`.)

In the first compilation, it will download any Java dependencies
automatically. Hence it may take a bit longer the first time.

### Running

To run the server in port 8080 issue the command:

    make run
    
**Note for Mac Users**: if you use Xcode, using `make run` to run DiMe might cause conflicts. In this case, use the alternate command:

	./gradlew bootRun
	
To start DiMe.

(`./gradlew bootRun` can always be used as an alternative to `make run` if you don't have GNU Make.)

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

The [project wiki page][3] has more detailed instructions and
documentation of the API and development.

If you have any questions, don't hesitate to contact the lead
developer [Mats Sjöberg](mailto:mats.sjoberg@helsinki.fi).

## License

The DiMe server source code is licensed under
[the MIT License](https://opensource.org/licenses/MIT).

[1]: http://www.oracle.com/technetwork/java/javase/downloads/index.html
[2]: https://github.com/HIIT/dime-server/wiki/Configuration
[3]: https://github.com/HIIT/dime-server/wiki
[4]: http://gradle.org/
