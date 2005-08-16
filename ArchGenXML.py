#!/usr/bin/env python2.3

#-----------------------------------------------------------------------------
# Name:        ArchGenXML.py
# Purpose:     generating plone products (archetypes code) out of an UML-model
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

# originally inspired Dave Kuhlman's generateDS Copyright (c) 2003 Dave Kuhlman

#from __future__ import generators   # only needed for Python 2.2

import sys
import logging
import utils
from OptionParser import parser

try:
    # for standalone use
    from ArchetypesGenerator import ArchetypesGenerator
except ImportError:
    # if installed in site-packages:
    from ArchGenXML.ArchetypesGenerator import ArchetypesGenerator
        
def main():
    utils.initLog('archgenxml.log')
    utils.addConsoleLogging()
    log = logging.getLogger('main')

    log.debug("Reading command line options first.")
    (settings, args) = parser.parse_args()
    try:
        model = args[0]
        log.debug("Model file is '%s'.",
                  model)
    except:
        log.critical("Hey, we need to be passed a UML file as an argument!")
        parser.print_help()
        sys.exit(2)

    print utils.ARCHGENXML_VERSION_LINE % str(utils.version())

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
    d = {}
    for key in keys:
        d[key] = getattr(settings, key)
        log.debug("Option '%s' has value '%s'.",
                  key, d[key])

    # if outfilename is not given by the -o option try getting the second 
    # regular argument
    if not d['outfilename']:
        log.debug("Outfilename not specified in the options. "
                  "Trying second loose commandline argument.")
        if len(args) > 1:
            d['outfilename']=args[1]
        else:
            log.debug("No second argument found: keeping outfilename empty.")
            # the output dir will be named after the model
    # start generation
    gen=ArchetypesGenerator(model, **d)
    gen.parseAndGenerate()

if __name__ == '__main__':
    main()
    #import pdb
    #pdb.run('main()')
