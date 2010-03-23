# -*- coding: utf-8 -*-
#
# File: XMLSectionParser.py
#
# generate files out of templated considering protected sections in existing
# files
#
# Created:     2007/09/06

__author__ = """\
Robert Niederreiter <rnix@squarewave.at>,
Jens Klein <jens@bluedynamics.com>"""
__licence__ = 'GPL'

BEGINPATTERN = '##code-section %s'
ENDPATTERN = '##/code-section %s'

import os
import logging
from StringIO import StringIO
from pkg_resources import resource_string, resource_stream
from zope.documenttemplate import HTML
from PyParser import PyModule

log = logging.getLogger('CodeSectionHandler')


def handleSectionedFile(templatepath, outputpath,
                        sectionnames=[], templateparams=None, overwrite=True):
    """Do some magic here since we are decayed :)
    
    @param templatepath - the relative path (as list of strings) to the 
                          template file, including it as last item
    @param outputpath - the path to the target file
    @param sectionnames - list of section names to consider
    @param templateparams - the placeholderparams for the dtml template
    """
    try:
        existentfile = open(outputpath)
        existentbuffer = existentfile.readlines()
        existentfile.close()
        
        #if overwrite isnt desired, stop when target file exists
        if not overwrite:
            return
    except IOError:
        existentbuffer = None

    # if file is a python file, pyparse it first, so that the template can 
    # reflect existing python constructs
    
    if os.path.splitext(outputpath)[-1] in ('.py','.cpy'):
        parsedModule = PyModule(existentbuffer and ''.join(existentbuffer) + 
                                '\n' or '', mode='string')
        if templateparams:
            templateparams['parsedModule'] = parsedModule

    templatepath = ['templates'] + templatepath
    if templateparams:
        template = resource_string(__name__, os.path.join(*templatepath))
        origparams = templateparams.copy()
        templateparams.update(__builtins__)
        template = HTML(template, templateparams)
        try:
            template = template().encode('utf-8')
        except:
            msg = "Problem rendering %s\n" % os.path.join(*templatepath)
            msg+= "params = %s" % origparams
            log.error(msg)
            raise
        templatebuffer = StringIO(template).readlines()
    else:
        templatestream = resource_stream(__name__, os.path.join(*templatepath))
        templatebuffer = templatestream.readlines()

    
    if existentbuffer and sectionnames:
        templatehandler = CodeSectionHandler(templatebuffer)
        existenthandler = CodeSectionHandler(existentbuffer)
        for sectionname in sectionnames:
            section = existenthandler.getProtectedSection(sectionname)
            templatehandler.setProtectedSection(sectionname, section)
        templatebuffer = templatehandler.codelines
    
    outfile = open(outputpath, 'w')
    outfile.writelines(templatebuffer)
    outfile.close()


class CodeSectionHandler(object):
    """Class CodeSectionHandler is responsible to get and set protected
    sections inside some kind of code.
    
    A protected section is defined like:
    
    ##code-section sectionname
    ##/code-section sectionname
    
    where '##code-section' defines a protected section and the following
    string, in the example 'sectionname' is the identifier or name of the
    section, since we want to be able to define several protected sections.
    
    Be aware of of the protected section syntax since start and end of those
    sections are checked against the pattern "##code-section %s' % name" and
    "##/code-section %s' % name", so spaces has to be set exactly.
    """
    
    def __init__(self, codelines):
        """Create CodeSectionHandler object.
        
        @param codelines - the code to parse and or modify as list of codelines.
        """
        self.codelines = codelines
        
    def getProtectedSection(self, name):
        """Return contents of the protected section with name.
        
        @param name - the name of the section
        """
        ret = []
        sectioncontent = False
        for line in self.codelines:
            if line.find(ENDPATTERN % name) != -1:
                return ret
            if sectioncontent:
                ret.append(line)
            if line.find(BEGINPATTERN % name) != -1:
                sectioncontent = True
        return ['']        
        raise Exception('%s - Section not found or no section end pattern set.'\
                        % name)
    
    def setProtectedSection(self, name, code):
        """Set the contents of the protected section with name.
        
        @param name - the name of the section
        @param code - a list of codelines
        """
        index = 0
        startindex = None
        for line in self.codelines:
            if line.find(ENDPATTERN % name) != -1:
                if startindex is None:
                    raise Exception('Section start not found')
                cl = self.codelines
                self.codelines = cl[0:startindex + 1] + code + cl[index:]
                return
            if line.find(BEGINPATTERN % name) != -1:
                startindex = index
            index += 1
        raise Exception('%s - Section not found or no section end pattern set.'\
                         % name)

