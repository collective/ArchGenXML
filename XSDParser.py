#-----------------------------------------------------------------------------
# Name:        XSDParser.py
# Purpose:     use XML Schema Definitions as base for code generation
#
# Author:      Philipp Auersperg
# Remark:      (jensens) The developement of this part has stopped almost.
#              conversion from XSD to XMI can be done with Eclipse and
#              a plugin named (i'll add the name later (brain-dead today)
#
# Created:     2003/19/07
# RCS-ID:      $Id$
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

# DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!!
# DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!!
# DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!!
# DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!!
# DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!!
# DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!!
# DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!! DEPRECATED!!!
# See remark at the top.

import sys, os.path, time, string
import getopt
from xml import sax
from xml.sax import handler

from utils import mapName

class XschemaElement:
    def __init__(self, name, attrs):
        self.name = str(name)
        self.cleanName = ''
        self.attrs = attrs
        self.children = []
        self.maxOccurs = 1
        self.complex = 0
        self.type = 'NoneType'
        self.attributeDefs = []
        self.taggedValues={}
        self.internalOnly=0
        
    def addChild(self, element):
        self.children.append(element)
    def isInternal(self):
        return self.internalOnly
    def getChildren(self): return self.children
    def getName(self): return self.name
    def getCleanName(self): return self.cleanName
    def getUnmappedCleanName(self): return self.unmappedCleanName
    def setName(self, name): self.name = name
    def getAttrs(self): return self.attrs
    def getMaxOccurs(self): return self.maxOccurs
    def getType(self): return self.type
    def isComplex(self): return self.complex
    def getGenParents(self):return []
    def getGenChildren(self):return []
    def addAttributeDefs(self, attrs):
        att=XschemaAttribute(attrs)
        self.attributeDefs.append(att)
    def getAttributeDefs(self): return self.attributeDefs
    def getRef(self):
        return getattr(self,'ref',None)

    def getRefs(self):
        ''' return all referenced schema names '''

        return [str(c.getRef()) for c in self.getChildren() if c.getRef()]

    def getTaggedValue(self,name,default=''):
        return self.taggedValues.get(name,default)

    def hasTaggedValue(self,name):
        return self.taggedValues.has_key(name)

    def getDocumentation(self):
        return self.getTaggedValue('documentation')

    def getSubtypeNames(self,recursive=0):
        ''' returns the non-intrinsic subtypes '''
        return [str(c.getType()) for c in self.getChildren() if not c.isIntrinsicType() ]

    def getToAssociations(self):
        return []

    def getFromAssociations(self):
        return []

    def show(self, outfile, level):
        showLevel(outfile, level)
        outfile.write('Name: %s  Type: %s\n' % (self.name, self.type))
        showLevel(outfile, level)
        outfile.write('  - Complex: %d  MaxOccurs: %d\n' % \
            (self.complex, self.maxOccurs))
        showLevel(outfile, level)
        outfile.write('  - Attrs: %s\n' % self.attrs)
        showLevel(outfile, level)
        outfile.write('  - AttributeDefs: %s\n' % self.attributeDefs)
        for key in self.attributeDefs.keys():
            showLevel(outfile, level + 1)
            outfile.write('key: %s  value: %s\n' % \
                (key, self.attributeDefs[key]))
        for child in self.children:
            child.show(outfile, level + 1)

    def annotate(self):
        # If there is a namespace, replace it with an underscore.
        trans=string.maketrans(':-.', '___')
        if self.name:
            self.unmappedCleanName = str(self.name).translate(trans)
        else:
            self.unmappedCleanName = ''

        self.cleanName = mapName(self.unmappedCleanName)
        if 'maxOccurs' in self.attrs.keys():
            max = self.attrs['maxOccurs']
            if max == 'unbounded':
                max = 99999
            else:
                try:
                    max = int(self.attrs['maxOccurs'])
                except ValueError:
                    sys.stderr.write('*** %s/%s  maxOccurs must be integer or "unbounded".' % \
                        (element.getName(), child.getName())
                        )
                    sys.exit(-1)
        else:
            max = 1
        self.maxOccurs = max
        if 'type' in self.attrs.keys():
            type1 = self.attrs['type']
            if type1 == 'xs:string' or \
                type1 == 'xs:integer' or \
                type1 == 'xs:float':
                self.complex = 0
            else:
                self.complex = 1
            self.type = self.attrs['type']
        else:
            self.complex = 1
            self.type = 'NoneType'
        # If it does not have a type, then make the type the same as the name.
        if self.type == 'NoneType' and self.name:
            self.type = self.name
        # Do it recursively for all descendents.

        # refs
        if 'ref' in self.attrs.keys():
            self.ref=self.attrs['ref']


        for child in self.children:
            child.annotate()

    #zworks extensions
    def isIntrinsicType(self):
        return str(self.getType()).startswith('xs:')

    def getMethodDefs(self):
        return []

    def isAbstract(self):
        return 0

    def isDependent(self):
        return 0

    def getStereoType(self):
        return None
    
    def isI18N(self):
        return 0

class XschemaAttribute(XschemaElement):
    def __init__(self,  attrs):
        self.name = ''
        self.cleanName = ''
        self.attrs = attrs
        self.children = []
        self.maxOccurs = 1
        self.complex = 0
        self.type = 'NoneType'
        self.attributeDefs = []
        self.taggedValues={}

        for k,v in attrs.items():
            setattr(self,str(k),v)

    def __setitem__(self,k,v):
        setattr(self,k,v)

    #def __getitem__(self,*args):
    #    """ """
    #    return self.__dict__.__getitem__(*args)

    #def has_key(self,k):
    #    return self.__dict__.has_key(k)

    def hasDefault(self):
        return 0

    def getDefault(self):
        return None

    def getTaggedValue(self,name,default=''):
        return self.taggedValues.get(name,default)

    def hasTaggedValue(self,name):
        return self.taggedNames.has_key(name)

    def getTaggedValues(self):
        return self.taggedValues
#
# SAX handler
#
class XschemaHandler(handler.ContentHandler):
    def __init__(self):
        self.stack = []
        self.root = None
        self.inElement = 0
        self.inComplexType = 0
        self.inSequence = 0
        self.inChoice = 1

    def getRoot(self):
        return self.root

    def showError(self, msg):
        print msg
        sys.exit(-1)

    def startElement(self, name, attrs):
        #print '(startElement) name: %s len(stack): %d' % \
        #      (name, len(self.stack))
        if name == 'xs:element':
            self.inElement = 1
            if 'name' in attrs.keys() and 'type' in attrs.keys():
                if attrs['type'] == 'xs:string' or \
                       attrs['type'] == 'xs:integer' or \
                       attrs['type'] == 'xs:float':
                    element = XschemaElement(attrs['name'], attrs)
                    #self.stack[-1].addChild(element)
                else:
                    element = XschemaElement(attrs['name'], attrs)
            elif 'name' in attrs.keys():
                element = XschemaElement(attrs['name'], attrs)
            elif 'type' in attrs.keys():
                element = XschemaElement('', attrs)
            else:
                element = XschemaElement('', attrs)
            self.stack.append(element)
        elif name == 'xs:complexType':
            self.inComplexType = 1
        elif name == 'xs:sequence':
            self.inSequence = 1
        elif name == 'xs:choice':
            self.inChoice = 1
        elif name == 'xs:attribute':
            self.inAttribute = 1
            if 'name' in attrs.keys():
                self.stack[-1].addAttributeDefs(attrs)
        elif name == 'xs:schema':
            self.inSchema = 1
            element = XschemaElement('root', {})
            self.stack.append(element)

    def endElement(self, name):
        if name == 'xs:element':
            self.inElement = 0
            element = self.stack.pop()
            self.stack[-1].addChild(element)
        elif name == 'xs:complexType':
            self.inComplexType = 0
        elif name == 'xs:sequence':
            self.inSequence = 0
        elif name == 'xs:choice':
            self.inChoice = 0
        elif name == 'xs:attribute':
            self.inAttribute = 0
        elif name == 'xs:schema':
            self.inSchema = 0
            if len(self.stack) != 1:
                print '*** error stack'
                sys.exit(-1)
            self.root = self.stack[0]

    def characters(self, chrs):
        if self.inElement:
            pass
        elif self.inComplexType:
            pass
        elif self.inSequence:
            pass
        elif self.inChoice:
            pass

def parse(xschemaFileName):
    """ """

    parser = sax.make_parser(["xml.sax.drivers2.drv_pyexpat",])
    dh = XschemaHandler()
    parser.setContentHandler(dh)
    parser.parse(xschemaFileName)
    root = dh.getRoot()
    root.annotate()
    return root
