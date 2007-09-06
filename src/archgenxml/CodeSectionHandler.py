# -*- coding: utf-8 -*-
# File: XMLSectionParser.py
#
# generate files out of templated considering protected sections in existing
# files
#
# Created:     2007/09/06

__author__ = 'Robert Niederreiter <office@squarewave.at>'
__licence__ = 'GPL'

BEGINPATTERN = '##code-section %s'
ENDPATTERN = '##/code-section %s'

import os
from StringIO import StringIO
from documenttemplate.documenttemplate import HTML

def handleSectionedFile(templatepath, outputpath,
                        sectionnames=[], templateparams=None):
    """Do some magic here since we are decayed :)
    
    @param templatepath - the path to the template file
    @param outputpath - the path to the target file
    @param sectionnames - list of section names to consider
    @param templateparams - the placeholderparams for the dtml template
    """
    if templateparams:
        templateparams.update(__builtins__)
        templatefile = open(templatepath, 'r')
        template = templatefile.read()
        templatefile.close()
        template = HTML(template, templateparams)
        template = template()
        templatebuffer = StringIO(template).readlines()
    else:
        templatefile = open(templatepath, 'r')
        templatebuffer = templatefile.readlines()
        templatefile.close()
    
    try:
        existentfile = open(outputpath)
        existentbuffer = existentfile.readlines()
        existentfile.close()
    except IOError:
        existentbuffer = None
    
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
        raise Exception('Section not found or no section end pattern set.')
    
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
        raise Exception('Section not found or no section end pattern set.')

