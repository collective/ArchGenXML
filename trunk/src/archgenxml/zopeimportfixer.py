# -*- coding: utf-8 -*-
#---------------------------------------------------------------
# Author:      Reinout van Rees
#
# Copyright:   (c) Zest software
# Licence:     GPL
#---------------------------------------------------------------
 
import logging
import os.path
import sys

log = logging.getLogger('utils')

def prepareZopeImport():
    log.debug("Initializing zope3 machinery...")
    ZOPEPATHFILE = '.agx_zope_path'
    userDir = os.path.expanduser('~')
    pathFile = os.path.join(userDir, ZOPEPATHFILE)
    if os.path.exists(pathFile):
        f = open (pathFile)
        additionalPath = f.readline().strip()
        f.close()
        sys.path.insert(0, additionalPath)
        log.debug("Read %s, added %s in front of the PYTHONPATH.",
                  pathFile, additionalPath)
    try:
        log.debug("sys.path: %r", sys.path)
        log.debug("Before import zope stuff, here "
                  "are all loaded modules: %r",
                  sys.modules.keys())
        from zope import component
        from zope.configuration import xmlconfig
    except ImportError, e:
        log.debug(e)
        log.error("Could not import zope3 components.\n"
                  "They are not available on the PYTHONPATH.\n"
                  "Alternatively, you can place the path location "
                  "in ~/%s.\n"
                  "Put something like /opt/zope2.10.3/lib/python "
                  "in there.", ZOPEPATHFILE)
        if os.path.exists(pathFile):
            log.error("Hm. Apparently '%s' already exists. "
                      "Sure it points at a good zope's /lib/python "
                      "directory? A good zope is 2.10 or 3.3+.",
                      pathFile)
            log.debug("Here are all loaded modules: %r",
                      sys.modules)
            try:
                import zope
                log.error("Actually, we *can* import zope.\n"
                          "So something may be messing up your PYTHONPATH.\n"
                          "The zope that we found was in %s", zope.__path__)
            except ImportError:
                pass
        sys.exit(1)

# Now run the thing
prepareZopeImport()
