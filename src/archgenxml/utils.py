# -*- coding: utf-8 -*-
#---------------------------------------------------------------
# Author:      Philipp Auersperg
#
# Copyright:   (c) 2003-2009 BlueDynamics
# Licence:     GPL
#---------------------------------------------------------------
 
from pkg_resources import resource_string
from pkg_resources import get_distribution
import logging
import os.path

from zope import component

from archgenxml.interfaces import IOptions
from archgenxml import PyParser

from xmiparser.utils import toBoolean, normalize, wrap


log = logging.getLogger('utils')

NameTable = {
    'class': 'klass',
    'import': 'emport'
    }
    
def capitalize(s):
    '''alternative to standard capitalize() method that does not set the trailing
    chars to lowercase as string.capitalize() does'''
    if not s:
        return s
    
    return '%s%s' % (s[0].upper(),s[1:])
    
def makeFile(filename, force=1, binary=0):
    log.debug("Calling makeFile to create '%s'.", filename)
    options = component.getUtility(IOptions, name='options')
    fullfilename = os.path.join(options.option('targetRoot'),
                                filename)
    log.debug("Making file '%s' (force=%s).", fullfilename, force)
    outfile = None
    if (not force) and os.path.exists(fullfilename):
        log.debug("File already exists and we're not to force it. Returning nothing.")
        return None
    else:
        log.debug("Opening the file for writing and returning it.")
        if binary:
            outfile = open(fullfilename, 'wb')
        else:
            outfile = open(fullfilename, 'w')
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
    
    parent=os.path.join(*os.path.split(directoryName)[:-1])
    if force and parent and not os.path.exists(parent):
        makeDir(parent,force=force)

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

def indent(s, indent, prepend='', 
           skipFirstRow=False, 
           stripBlank=True, 
           skipBlank=False):
    """Indent string 's'.

    's' is a string with optional '\n's for multiple lines. 's' can be
    empty or None, that won't barf this function.
    'indent' is the level of indentation. 0 gives 0 spaces, 1 gives 4
    spaces, and so on.
    """
    if s is None:
        return ''
    rows = s.split('\n')
    if skipFirstRow:
        lines = [rows[0]]+['    '*indent + prepend + l for l in rows[1:]]
    else:
        lines = ['    '*indent + prepend + l for l in rows]
    if stripBlank:
        lines = [line.rstrip() for line in lines]
    if skipBlank:
        lines = [line.rstrip() for line in lines if line.strip()]
    return '\n'.join(lines)

def getExpression(s):
    """Interprets an expression (permission and other taggedValues).

    * If an exp is a string it will be kept, if not it will be enclosed
    by quotes.

    * If an exp starts with 'python:' it wont be quoted.
    """
    if s is None:
        s = ''
    try:
        s = s.strip()
    except AttributeError:
        # it is a int/float, probably, returning as string
        return str(s)
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
            
# almost the same in a other flavour (attention, this one called by 
# BaseGenerator pendant with same name
            
def processExpression(value, asString=True):
    """Process the string returned by tagged values.

    * python: prefixes a python expression
    * string: prefixes a string
    * fallback to default, which is string, if asString isnt set to False
    """
    if not isinstance(value, (str, unicode)):
        return value
    if value.startswith('python:'):
        return value[7:]
    elif value.startswith('string:'):
        return "'%s'" % value[7:]
    if asString:
        return "'%s'" % value
    else:
        return value            

def isTGVTrue(tgv):
    if isinstance(tgv, (str, unicode)):
        tgv = tgv.lower()
    else:
        return bool(tgv)
    
    return tgv in (1, '1', 'true')

def isTGVFalse(tgv):
    """Checks if a tgv is _explicitly_ False.

    A 'None' value is undefined and _not_ False, so it's something
    different than (not toBoolean(tgv)).
    """
    if isinstance(tgv, (str, unicode)):
        tgv = tgv.lower()
    else:
        if not tgv is None:
            return not bool(tgv)
        else:
            return False
    
    return tgv in (0, '0', 'false')

def cleanName(name):
    return name.replace(' ','_').replace('.','_').replace('/','_')


ARCHGENXML_VERSION_LINE = """\
ArchGenXML %s
(c) 2003-2009 BlueDynamics Alliance, Austria, GPL 2.0 or later\
"""

def version(stripsvn=True):
    dist = get_distribution('archgenxml')
    ver = dist.version
    if stripsvn:
        ver = ver[:ver.find('.dev-')+4] 
    return "Version %s" % ver 

def parsePythonModule(targetRoot, packagePath, fileName):
    """Parse a python module and return the module object.

    This can then be passed to getProtectedSection() to
    generate protected sections.
    """

    targetPath = os.path.join(targetRoot, packagePath, fileName)
    parsed = None
    try:
        parsed = PyParser.PyModule(targetPath)
    except IOError:
        pass
    except:
        print
        print '***'
        print '***Error while reparsing the file', targetPath
        print '***'
        print
        raise
    return parsed

