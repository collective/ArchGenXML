# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Author:      Philipp Auersperg
#
# Copyright:   (c) 2003-2006 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys
import logging
import os.path
import types

log = logging.getLogger('utils')

NameTable = {
    'class': 'klass',
    'import': 'emport'
    }
    
specialrpl = {
    u'ö': u'oe',
    u'ü': u'ue',
    u'ä': u'ae',
    u'Ö': u'Oe',
    u'Ü': u'Ue',
    u'Ä': u'Ae',
    u'ß': u'ss',
    # add more for other language here
}

def makeFile(outfilename, force=1, binary=0):
    log.debug("Making file '%s' (force=%s).", outfilename, force)
    outfile = None
    if (not force) and os.path.exists(outfilename):
        log.debug("File already exists and we're not to force it. Returning nothing.")
        return None
    else:
        log.debug("Opening the file for writing and returning it.")
        if binary:
            outfile = open(outfilename, 'wb')
        else:
            outfile = open(outfilename, 'w')
    return outfile

def readFile(filename):
    log.debug("Trying to open '%s' for reading.", filename)
    try:
        file = open(filename, 'r')
        res = file.read()
        file.close()
        log.debug("Done, returing result.")
        return res
    except IOError:
        log.debug("Couldn't open the file, returning nothing.")
        return None

def makeDir(directoryName, force=1):
    log.debug("Trying to make directory '%s' (force=%s).", directoryName, force)
    directory = None
    if os.path.exists(directoryName):
        log.debug("Directory already exists. Fine.")
    else:
        os.mkdir(directoryName)
        log.debug("Made the directory.")

def mapName(oldName):
    #global NameTable
    newName = oldName
    if NameTable:
        if oldName in NameTable.keys():
            newName = NameTable[oldName]
    return newName.replace('-', '_')

def readTemplate(filename):
    log.debug("Trying to read template '%s'.", filename)
    templatedir = os.path.join(sys.path[0], 'templates')
    log.debug("Trying to find it in template directory '%s'.", templatedir)
    template = open(os.path.join(templatedir,filename)).read()
    log.debug("Succesfully opened the template, returning it.")
    return template

def indent(s, indent, prepend='', skipFirstRow=False, stripBlank=False):
    """Indent string 's'.

    's' is a string with optional '\n's for multiple lines. 's' can be
    empty or None, that won't barf this function.
    'indent' is the level of indentation. 0 gives 0 spaces, 1 gives 4
    spaces, and so on.
    """
    if s == None:
        return ''
    rows = s.split('\n')
    if skipFirstRow:
        lines = [rows[0]]+['    '*indent + prepend + l for l in rows[1:]]
    else:
        lines = ['    '*indent + prepend + l for l in rows]
    if stripBlank:
        lines = [line.rstrip() for line in lines]
    return '\n'.join(lines)

def getExpression(s):
    """Interprets an expression (permission and other taggedValues).

    * If an exp is a string it will be kept, if not it will be enclosed
    by quotes.

    * If an exp starts with 'python:' it wont be quoted.
    """
    if s is None:
        s = ''
    s = s.strip()
    if s and (s[0]=='"' and s[-1]=='"' or s[0]=="'" and s[-1]=="'"):
        return s
    else:
        if s.startswith('python:'):
            return s[7:]
        else:
            # Quote in """ if the string contains " or a newline, else use "
            if '"' in s or '\n' in s:
                return '"""%s"""' % s
            else:
                return '"%s"' % s

def isTGVTrue(tgv):
    if isinstance(tgv, (str, unicode)):
        tgv = tgv.lower()
    return tgv in (1, '1', 'true')

def isTGVFalse(tgv):
    """Checks if a tgv is _explicitly_ False.

    A 'None' value is undefined and _not_ False, so it's something
    different than (not toBoolean(tgv)).
    """
    if isinstance(tgv, (str, unicode)):
        tgv = tgv.lower()
    return tgv in (0, '0', 'false')

def toBoolean(v):
    if isinstance(v, (str, unicode)):
        v = v.lower().strip()
    if v in (0, '0', 'false', False):
        return False
    if v in (1, '1', 'true', True):
        return True
    if v:
        return True
    return False

def cleanName(name):
    return name.replace(' ','_').replace('.','_').replace('/','_')

# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061
def wrap(text, width):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line[line.rfind('\n')+1:])
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )

ARCHGENXML_VERSION_LINE = """\
ArchGenXML %s
(c) 2003-2006 BlueDynamics, Austria, GNU General Public License 2.0 or later\
"""

def version():
    ver = open(os.path.join(sys.path[0],'version.txt')).read().strip()
    return "Version " + str(ver)

def initLog(filename):
    """Initialise the logger.

    This needs only to be called from ArchGenXML.py and tests/runalltests.py.
    """
    log = logging.getLogger()
    hdlr = logging.FileHandler(filename, 'w')
    formatter = logging.Formatter('%(name)-10s %(levelname)-5s %(message)s')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)

def addConsoleLogging():
    """Add logging to the console.

    This needs only to be called from ArchGenXML.py.
    """
    log = logging.getLogger()
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(levelname)-5s %(message)s')
    hdlr.setLevel(logging.INFO)
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)

def normalize(data, doReplace=False):
    """Converts a unicode to string, stripping blank spaces."""
    if type(data) not in types.StringTypes:
        return data
    if type(data) is types.StringType:
        # make unicode
        data = data.decode('utf-8')
    if type(data) is types.UnicodeType:
        data = data.strip()
        if doReplace:
            for key in specialrpl:
                data = data.replace(key, specialrpl[key])    
    if not data is None:
        return data.encode('utf-8')
    else:
        return None
