#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Name:        ArchGenXML.py
# Purpose:     generating plone products (archetypes code) out of an UML-model
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# Copyright:   (c) 2003-2007 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

# originally inspired Dave Kuhlman's generateDS Copyright (c) 2003 Dave Kuhlman

# First things first, sadly.
import loginitializer
loginitializer.initLog('archgenxml.log')
loginitializer.addConsoleLogging()
# End of the stuff that needs to be handled first.

import archgenxml
import logging
import sys
import utils
import os
from time import time

from zope import component

from OptionParser import parser

log = logging.getLogger('main')

DEBUG = 1

if not DEBUG:
    try:
        # speedup: ~15%
        import psyco
        psyco.full()
        log.debug("Running with Psyco.")
    except ImportError:
        log.debug("Running without Psyco.")
        

def main():
    starttime = time()
    # Import zope here as we want to possibly inject an extra
    # directory into the import path. Just depending on a zope in the
    # normal import path can easily mess up existing zope sites.
    

    log.debug("Reading command line options first.")
    (settings, args) = parser.parse_args()
    # Note: settings is all that the parser can recognize and parse
    # from the command line arguments. 'args' is everything else
    # that's left. The first (and probably only) left-over argument
    # should be the model file
    if len(args) > 0:
        model = args[0]
        log.debug("Model file is '%s'.", model)
    else:
        log.critical("Hey, we need to be passed a UML file as an argument!")
        parser.print_help()
        sys.exit(2)
    log.info(utils.ARCHGENXML_VERSION_LINE, str(utils.version(stripsvn=False)))
    # This is a little bit hacky. Probably should read optparse's doc
    # better. [Reinout]
    log.debug("Figuring out the settings we're passing to the "
              "main program...")
    keys = dir(settings)
    keys = [key for key in keys
            if not key.startswith('_')
            and not key in ['ensure_value', 'read_file', 'read_module']]
    log.debug("Keys available through the option parser: %r.",
              keys)
    options = {}
    for key in keys:
        options[key] = getattr(settings, key)
        log.debug("Option '%s' has value '%s'.",
                  key, options[key])

    # if outfilename is not given by the -o option try getting the second
    # regular argument
    if not options['outfilename']:
        log.debug("Outfilename not specified in the options. "
                  "Trying second loose commandline argument.")
        if len(args) > 1:
            options['outfilename'] = args[1]
        else:
            log.debug("No second argument found: keeping outfilename empty.")
            # the output dir will be named after the model

    # hook into sys.excepthook if the user requested it
    if options['pdb_on_exception']:
        sys.excepthook = info

    # start generation
    try:
        # for standalone use
        from ArchetypesGenerator import ArchetypesGenerator
    except ImportError:
        # if installed in site-packages:
        from archgenxml.ArchetypesGenerator import ArchetypesGenerator
    # Instead of passing these options to the generator (which uses it
    # to update it's self.__dict__, we ought to pass this along to a
    # utility that you can grab from anywhere.
    import utility
    from archgenxml.interfaces import IOptions
    optionsHolder = component.getUtility(IOptions, name='options')
    optionsHolder.storeOptions(options)
    gen = ArchetypesGenerator(model, **options)
    gen.parseAndGenerate()
    log.info('generator run took %1.2f sec.' % (time()-starttime))

def info(type, value, tb):
    # from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65287
    if hasattr(sys, 'ps1') or not (
        sys.stderr.isatty() and sys.stdin.isatty()):
        # Interactive mode, no tty-like device, or syntax error: nothing
        # to do but call the default hook
        sys.__excepthook__(type, value, tb)
    else:
        import traceback, pdb
        # You are NOT in interactive mode; so, print the exception...
        traceback.print_exception(type, value, tb)
        print
        # ... then start the debugger in post-mortem mode
        pdb.pm()

if __name__ == '__main__':
    main()
