#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Name:        ArchGenXML.py
# Purpose:     generating plone products (archetypes code) out of an UML-model
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# RCS-ID:      $Id: ArchGenXML.py,v 1.152 2004/04/27 12:25:07 yenzenz Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

# originally inspired Dave Kuhlman's generateDS Copyright (c) 2003 Dave Kuhlman

#from __future__ import generators   # only needed for Python 2.2

import sys

try:
    # for standalone use
    from ArchetypesGenerator import ArchetypesGenerator
    from utils import read_project_settings, version
except ImportError:
    # if installed in site-packages:
    from ArchGenXML.ArchetypesGenerator import ArchetypesGenerator
    from ArchGenXML.utils import read_project_settings
        
def main():
    args = sys.argv[1:]
    settings,args=read_project_settings(args)
    if len(args) < 1 and not settings.get('noclass',0):
        usage()
        
    if len(args):
        xschemaFileName = args[0]
    else:
        xschemaFileName = ''

    # if outfilename is not given by the -o option try getting the second 
    # regular argument
    if not settings['outfilename']: 
        if len(args) > 1:
            settings['outfilename']=args[1]

    if not settings['outfilename']:
        usage(2)
    
    # start generation
    gen=ArchetypesGenerator(xschemaFileName, **settings)
    gen.parseAndGenerate()

if __name__ == '__main__':
    main()
    #import pdb
    #pdb.run('main()')
