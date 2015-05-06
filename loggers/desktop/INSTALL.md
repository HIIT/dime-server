

INSTALLING THE LINUX DESKTOP LOGGER
===================================

This document describes the installation of the Linux desktop logger
for Ubuntu 14.04.  The logger is based on the GNOME
[Zeitgeist](http://zeitgeist-project.com/) engine for logging user
activities and will not work without it.  Zeitgeist is installed by
default at least in all recent Ubuntu distributions.  For supported
browsers (Google Chrome, Chromium, Firefox), the logger utilizes the
history files.


Required Python modules
-----------------------

The following Python modules are required:

* requests: `apt-get install python-requests`


Configuration
-------------

The logger is configured using the `user.ini` configuration file.  An
example is provided as `user.ini.example`:

    $ cp user.ini.example user.ini
	$ [your_favorite_editor] user.ini

There is also a second configuration file named `default.ini` for
default values, but it should not be modified.  All configuration
options in `user.ini` take precedence over the defaults.

### [General]

* hostname: determined automatically but can be set explicitly here 

### [DiMe]

* server_url: URL address of the used DiMe server, required
* username: DiMe username, required
* password: DiMe password, required

### [Zeitgeist]

* use: whether to use the Zeitgeist document logging functionality

### [Chrome/Chromium/Firefox]

These browser loggers are independent and can be used simultaneously.
All have the following configuration options:

* use: whether to use this particular logger 

### [Indicator]

