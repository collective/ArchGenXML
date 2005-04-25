#-----------------------------------------------------------------------------
# Name:        BaseGenerator.py
# Purpose:     provide some common methods for the generator
#
# Author:      Jens Klein
#
# Created:     2005-01-10
# RCS-ID:      $Id: BaseGenerator.py 3411 2005-01-05 01:55:45Z yenzenz $
# Copyright:   (c) 2005 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

_marker = []

import os
from StringIO import StringIO

from documenttemplate.documenttemplate import HTML

import utils
from utils import makeFile, readFile, makeDir,mapName, wrap, indent, getExpression, \
    isTGVTrue, isTGVFalse, readTemplate, getFileHeaderInfo

import XSDParser, XMIParser, PyParser
from utils import readTemplate, cleanName
from codesnippets import *
from UMLProfile import UMLProfile

class BaseGenerator:
    """ abstract base class for the different concrete generators """
    
    uml_profile=UMLProfile()
    uml_profile.addStereoType('python_class',['XMIClass'],dispatching=1,
        generator='generatePythonClass',template='python_class.py')

    default_class_type='python_class'

    def isTGVTrue(self,v):
        return isTGVTrue(v)

    def isTGVFalse(self,v):
        return isTGVFalse(v)

    def getUMLProfile(self):
        return self.uml_profile

    def getDefaultClassType(self):
        return self.getUMLProfile().getStereoType(self.default_class_type)

    def getOption(self,option,element,default=_marker,aggregate=False):
        ''' query a certain option for an element including 'acquisition' :
            search the element, then the packages upwards, then global options'''

        if element:
            o=element

            #climb up the hierarchy
            aggregator=''
            while o:
                if o.hasTaggedValue(option):
                    if aggregate:
                        # create a multiline string
                        aggregator+=o.getTaggedValue(option)+'\n'
                    else:
                        return o.getTaggedValue(option)
                o=o.getParent()
            if aggregator:
                return aggregator

        #look in the options
        if hasattr(self,option):
            return getattr(self,option)

        if default != _marker:
            return default
        else:
            raise ValueError,"option '%s' is mandatory for element '%s'" % (option,element and element.getName())



    def cleanName(self, name):
        return name.replace(' ','_').replace('.','_').replace('/','_')


    def parsePythonModule(self, packagePath, fileName):
        """Parse a python module and return the module object. This can then
        be passed to getProtectedSection() to generate protected sections
        """

        targetPath = os.path.join(self.targetRoot, packagePath, fileName)
        parsed = None

        if self.method_preservation:
            try:
                parsed = PyParser.PyModule(targetPath)
            except IOError:
                pass
            except :
                print
                print '***'
                print '***Error while reparsing the file', targetPath
                print '***'
                print
                raise

        return parsed

    def getProtectedSection(self, parsed, section, ind=0):
        """Given a parsed python module and a section name, return a string
        with the protected code-section to be included in the generated module.
        """

        outstring = indent(PyParser.PROTECTED_BEGIN, ind) + ' ' + \
                            section +' #fill in your manual code here\n'
        if parsed:
            sectioncode=parsed.getProtectedSection(section)
            if sectioncode:
                outstring += sectioncode + '\n'

        outstring += indent(PyParser.PROTECTED_END,ind) + ' ' + section + '\n'
        return outstring

    def generateProtectedSection(self,outfile,element,section,indent=0):
        parsed = self.parsed_class_sources.get(element.getPackage().getFilePath()+'/'+element.getName(),None)
        print >> outfile, self.getProtectedSection(parsed,section,indent)

    def generateDependentImports(self,element):
        outfile=StringIO()
        package=element.getPackage()

        #imports for stub-association classes
        importLines=[]

        parents  = element.getGenParents()
        parents += element.getRealizationParents()
        for p in parents:
            if p.hasStereoType(self.stub_stereotypes) and \
                p.getTaggedValue('import_from',None):
                print >> outfile,'from %s import %s' % \
                    (p.getTaggedValue('import_from'), p.getName())
            else:
                print >> outfile,'from %s import %s' % (
                    p.getQualifiedModuleName(
                        package,
                        forcePluginRoot=self.force_plugin_root,
                        includeRoot=0,
                    ),
                    p.getName())

        assocs = element.getFromAssociations()
        element.hasAssocClass=0
        for p in assocs:
            if getattr(p,'isAssociationClass',0):
                # get import_from and add it to importLines
                #import pdb; pdb.set_trace()
                module = p.getTaggedValue('import_from', None)
                if module:
                    importLine = 'from %s import %s' % (module, p.getName())
                    importLines.append(importLine)
                element.hasAssocClass=1
                break
        
        if self.backreferences_support:
            bassocs = element.getToAssociations()
            for p in bassocs:
                if getattr(p,'isAssociationClass',0):
                    element.hasAssocClass=1
                    break

        if element.hasAssocClass:
            for line in importLines:
                print >> outfile, line

        return outfile.getvalue()


    def generateImplements(self,element,parentnames):
        outfile=StringIO()
        # "__implements__" line -> handle realization parents
        reparents=element.getRealizationParents()
        reparentnames=[p.getName() for p in reparents]
        if reparents:

            # [optilude] Add extra () around getattr() call, in case the
            # base __implements__ is a single interface, not a tuple. Arbitrary
            # nesting of tuples in interface declaration is permitted.
            # Also, handle now-possible case where parentnames is empty

            if parentnames:
                parentInterfacesConcatenation = \
                    ' + '.join(["(getattr(%s,'__implements__',()),)" % i for i in parentnames])
            else:
                parentInterfacesConcatenation = '()'

            realizationsConcatenation = ','.join(reparentnames)

            print >> outfile, CLASS_IMPLEMENTS % \
                    {'baseclass_interfaces' : parentInterfacesConcatenation,
                     'realizations' : realizationsConcatenation, }
        else:

            # [optilude] Same as above

            if parentnames:
                parentInterfacesConcatenation = \
                    ' + '.join(["(getattr(%s,'__implements__',()),)" % i for i in parentnames])
            else:
                parentInterfacesConcatenation = '()'

            print >> outfile, CLASS_IMPLEMENTS_BASE % \
                    {'baseclass_interfaces' : parentInterfacesConcatenation,}

        return outfile.getvalue()

    def getMethodsToGenerate(self, element):
        manual_methods = []
        generatedMethods = []
        allmethnames = [m.getName() for m in element.getMethodDefs(recursive=1)]

        for m in element.getMethodDefs():
            allmethnames.append(m.getName())
            generatedMethods.append(m)

        for interface in element.getRealizationParents():
            meths=[m for m in interface.getMethodDefs(recursive=1) if m.getName() not in allmethnames]
            # i dont want to extra generate methods that are already defined in the class
            if meths:
                for m in meths:
                    generatedMethods.append(m)
                    allmethnames.append(m.getName())

        #contains _all_ generated method names
        method_names=[m.getName() for m in generatedMethods]

        #if __init__ has to be generated for tools i want _not_ __init__ to be preserved
        #if it is added to method_names it wont be recognized as a manual method (hacky but works)
        if element.hasStereoType(self.portal_tools) and '__init__' not in method_names:
            method_names.append('__init__')

        if self.method_preservation:
            cl=self.parsed_class_sources.get(element.getPackage().getFilePath()+'/'+element.name,None)
            if cl:
                manual_methods=[mt for mt in cl.methods.values() if mt.name not in method_names]

        return generatedMethods, manual_methods

    def generateClass(self,element):
        dispatchers=self.getUMLProfile().findStereoTypes(entities=['XMIClass'],dispatching=1)
        dispatcher=None
        for tgv in dispatchers:
            if element.hasStereoType(tgv.getName()):
                dispatcher=tgv

        if not dispatcher:
            dispatcher=self.getDefaultClassType()

        generator=dispatcher.generator
        return getattr(self,generator)(element,template=getattr(dispatcher,'template',None))

    def generatePythonClass(self,element,template,**kw):

        templ=readTemplate(template)
        d={ 'klass':element,
            'generator':self,
            'parsed_class':element.parsed_class,
            'builtins'   : __builtins__,
            'utils'       :utils,

            }
        d.update(__builtins__)
        d.update(kw)
        res=HTML(templ,d)()
        return res
