ArchGenXML documentation, such as README, INSTALL and manual
are located in the ./docs directory.

Note 1)

To install it use the --no-compile option for now. We need to figure out how
to exclude dtml-files ending with .py from byte-compiling at install time. 

  $ python setup.py install --no-compile


Note 2)

To build a Debian Package run:

  $ fakeroot debian/rules binary

-- Jens Klein
