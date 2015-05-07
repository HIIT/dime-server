

INSTALLING THE LINUX DESKTOP LOGGER
===================================

This document describes the installation of the Linux desktop logger
for Ubuntu 14.04.  The logger is based on the GNOME
[Zeitgeist](http://zeitgeist-project.com/) engine for logging user
activities and will not work without it.  Zeitgeist is installed by
default at least in all recent Ubuntu distributions.  For supported
browsers (Google Chrome, Chromium, Firefox), the logger utilizes the
browser-specific history files.


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
default values, but it should not be modified directly.  Use
`user.ini` instead: all *non-list* configuration options in `user.ini`
take precedence over the defaults of `default.ini`. 

The configuration files are split into sections like `[Mysection]`.
Each configuration option is a key,value pair formatted as `key:
value`.  All extra whitespace is removed.

All lists in the configuration files use semicolons (`;`) to separate
list items.  For dictionary maps, the format is `A->B`.  Lists can
extend to multiple lines. An example:

	[Mysection]
	mylist: foo; bar;
	        baz
	mydict: keyone->valueone; keytwo->valuetwo

### [DEFAULT]

* `dimepath`: Path to DiMe root, e.g. `~/dime-server`.  This value can
  then be used in other configuration options as `%(dimepath)s`.
  **Required**

### [General]

* `hostname`: Determined automatically but can be overrided explicitly
  here.

### [DiMe]

* `server_url`: URL address of the used DiMe server. **Required**
* `username`: DiMe server username. **Required**
* `password`: DiMe server password. **Required**

### [Zeitgeist]

The Zeitgeist logging component monitors DBus for Zeitgeist events and
sends them immediately to DiMe.

* `use`: Whether to use the Zeitgeist component.
* `nevents`: Number of historical events to send at startup or when a
  lost connection to the DiMe server is recovered. This is can be
  increased if the server is unreachable for longer periods of time.
* `other_actors`: Explicit mappings from Zeitgeist application labels
  (typically of format `*.desktop`) to real application names.  This
  might be needed for some more uncommon applications.
* `blacklist`: List of substrings in URLs to discard.  Can be used to
  blacklist files or directories from submission to DiMe.

### [Chrome/Chromium/Firefox]

These browser logging components are independent and can be used
simultaneously.  They probe the browser-specific history file at
regular intervals and send new items to DiMe.

All have the following configuration options:

* `use`: Whether to use this particular logger.
* `history_file`: Path and filename of the history file. **Required**
* `interval`: Update interval in seconds.
* `nevents`: Number of most-recent items in the browser history to
  consider. This is can be increased if the server is unreachable for
  longer periods of time.
* `blacklist`: List of substrings in URLs to discard.  Can be used to
  blacklist websites from submission to DiMe.

### [Indicator]

An Ubuntu AppIndicator showing the state of the logger.  Probably will
not work without the Unity desktop.

* `use`: Whether to use the indicator.
* `interval`: Update interval in seconds.
* `icon`: Icon for the indicator.
