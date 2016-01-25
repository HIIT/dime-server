Digital Me (DiMe)
=================

This package contains the executable version of DiMe. If you wish to
access the source code go to <https://github.com/HIIT/dime-server>.

Run DiMe
--------

The only requirement for running DiMe is Java JRE version 1.7 or
above. If you don't have that, you can download it from:

http://www.oracle.com/technetwork/java/javase/downloads/index.html

You can run DiMe directly from this directory, just open a terminal
window and change to this directory, and run:

    ./run-dime.sh

or for Windows systems you can double-click the run-dime.bat file.

It will take a few seconds to start up, once you see the message
"Started Application in X seconds" you can access your DiMe dashboard
by opening a web browser and going to the address:
<http://localhost:8080/>

This is the DiMe server that runs completely on your own computer!

The first step is to create an account for yourself by clicking on
"Register a new account." After this you can log in. Unfortunately
your DiMe will be empty, so the next step is to start logging, by
installing one of the DiMe loggers. You can find a list here:
<http://hiit.github.io/dime-server/>


Starting DiMe automatically
---------------------------

If you want DiMe to start automatically the next time you restart your
computer, you can run the installer script in this directory:

    ./install-autorun.sh

This will install DiMe into the folder ~/.dime and set up autostarting
for supported operating systems. Currently we support Mac OS X, and
Linux systems running an XDG compliant desktop or systemd.

After installing autorun you may remove the current directory if you
wish (since DiMe is now installed in ~/.dime).

Licensing
---------

The DiMe core server is Copyright (c) 2015 University of Helsinki

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.


