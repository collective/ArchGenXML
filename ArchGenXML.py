#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Name:        ArchGenXML.py
# Purpose:
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# RCS-ID:      $Id: ArchGenXML.py,v 1.4 2003/06/11 02:34:10 zworkb Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

# originally inspired Dave Kuhlman's generateDS Copyright (c) 2003 Dave Kuhlman





#from __future__ import generators   # only needed for Python 2.2

import sys, os.path, time
import getopt
from xml.sax import saxexts, saxlib, saxutils
from xml.sax import handler

from zipfile import ZipFile

import XSDParser
import XMIParser

#
# Global variables etc.
#
DelayedElements = []
AlreadyGenerated = []
Force = 0
YamlGen = 0


from utils import makeFile
from utils import makeDir
from utils import mapName


#
# Representation of element definition.
#

class ArchetypesGenerator:

    force=1
    unknownTypesAsString=1
    generateActions=0
    prefix=''

    reservedAtts=['id','title']

    def __init__(self,xschemaFileName,outfileName,**kwargs):
        self.outfileName=outfileName
        self.xschemaFileName=xschemaFileName
        self.__dict__.update(kwargs)

    def generateFti(self,element,subtypes):
        ''' '''

        actTempl='''
    actions=(
           {'action': 'portal_form/base_edit',
          'category': 'object',
          'id': 'edit',
          'name': 'edit',
          'permissions': ('Manage portal content',)},

           {'action': 'base_view',
          'category': 'object',
          'id': 'view',
          'name': 'view',
          'permissions': ('View',)},

        '''
        if subtypes:
            actTempl=actTempl+'''
           {'action': 'folder_listing',
          'category': 'object',
          'id': 'folder_listing',
          'name': 'folder_listing',
          'permissions': ('View',)},

    '''
        actTempl+='''
              )
        '''
        ftiTempl='''

    factory_type_information={
        'allowed_content_types':%(subtypes)s,
        #'content_icon':'%(type_name)s.gif',
        'immediate_view':'base_view'
        }

        '''
        if self.generateActions:
            ftiTempl += actTempl

        res=ftiTempl % {'subtypes':repr(tuple(subtypes)),'type_name':element.getCleanName()}
        return res

    typeMap={
        'string':'''StringField('%(name)s',
                    searchable=1,
                    ),''' ,
        'text':  '''StringField('%(name)s',
                    searchable=1,
                    widget=TextAreaWidget()
                    ),''' ,
        'integer':'''StringField('%(name)s',
                    searchable=1,
                    ),''',
        'float':'''FloatField('%(name)s',
                    searchable=1,
                    ),''',
        'boolean':'''BooleanField('%(name)s',
                    searchable=1,
                    ),''',
        'lines':'''LinesField('%(name)s',
                    searchable=1,
                    ),''',
        'date':'''DateTimeField('%(name)s',
                    searchable=1,
                    ),''',
        'image':'''ImageField('%(name)s',
                    sizes={'small':(100,100),'medium':(200,200),'large':(600,600)},
                    storage=AttributeStorage()
                    ),''',
        'file':'''FileField('%(name)s',
                    storage=AttributeStorage(),
                    widget=FileWidget()
                    ),''',
        'lines':'''LinesField('%(name)s',
                    searchable=1,
                    ),''',
        'reference':'''ReferenceField('%(name)s',allowed_types=%(allowed_types)s,
                    searchable=1,
                    ),''',

    }

    coerceMap={
        'xs:string':'string',
        'xs:int':'integer',
        'xs:integer':'integer',
        'xs:byte':'integer',
        'xs:double':'float',
        'xs:float':'float',
        'xs:boolean':'boolean',
        'ofs.image':'image',
        'ofs.file':'file',
        'xs:date':'date',
        'datetime':'date',
        'list':'lines',
        'liste':'lines',
        'image':'image',
        'int':'integer',
    }

    def coerceType(self, typename):
        #print 'coerceType:',typename,
        if typename in self.typeMap.keys():
            return typename

        if self.unknownTypesAsString:
            ctype=self.coerceMap.get(typename.lower(),'string')
        else:
            ctype=self.coerceMap[typename.lower()]

        #print ctype
        return ctype

    def getFieldString(self, element):
        ''' gets the schema field code '''
        typename=str(element.type)

        if element.getMaxOccurs()>1:
            ctype='lines'
        else:
            ctype=self.coerceType(typename)

        templ=self.typeMap[ctype]
        return templ % {'name':element.getCleanName(),'type':element.type}

    def getFieldStringFromAttribute(self, attr):
        ''' gets the schema field code '''
        #print 'getFieldStringFromAttribute:',attr.getName(),attr.type
        if not hasattr(attr,'type') or attr.type=='NoneType':
            ctype='string'
        else:
            ctype=self.coerceType(str(attr.type))

        templ=self.typeMap[ctype]
        return templ % {'name':attr.getName(),'type':attr.getType()}

    def getFieldStringFromAssociation(self, rel):
        ''' gets the schema field code '''
        #print 'getFieldStringFromAttribute:',attr.getName(),attr.type

        templ=self.typeMap['reference']
        obj=rel.toEnd.obj
        name=rel.fromEnd.getName()
        if name == 'None':
            name=obj.getName()+'_ref'
            
        return templ % {'name':name,'type':obj.getType(),'allowed_types':repr((obj.getName(),))}

    # Generate get/set/add member functions.
    def generateArcheSchema(self, outfile, element):
        print >> outfile,'    schema=BaseSchema + Schema(('
        refs=[]

        for attrDef in element.getAttributeDefs():
            name = attrDef.getName()
            if name in self.reservedAtts:
                continue
            mappedName = mapName(name)

            print >> outfile, '    '*2 ,self.getFieldStringFromAttribute(attrDef)
        for child in element.getChildren():
            name = child.getCleanName()
            if name in self.reservedAtts:
                continue
            unmappedName = child.getUnmappedCleanName()
            if child.getRef():
                refs.append(str(child.getRef()))

            if child.isIntrinsicType():
                print >> outfile, '    '*2 ,self.getFieldString(child)

        # and now the associations
        for rel in element.getToAssociations():
            if 1 or rel.toEnd.mult==1: #XXX: for mult==-1 a multiselection widget must come
                name = rel.fromEnd.getName()
                    
                if name in self.reservedAtts:
                    continue
    
                print >> outfile, '    '*2 ,self.getFieldStringFromAssociation(rel)
                

        print >> outfile,'    ))'

    def generateMethods(self,outfile,element):
        print >> outfile
        print >> outfile,'    #Methods'
        for m in element.getMethodDefs():
            paramstr=''
            params=m.getParamNames()
            if params:
                paramstr=','+','.join(params)
                print paramstr
            print >> outfile
            print >> outfile,'    def %s(self%s):' % (m.getName(),paramstr)
            print >> outfile,'    '*2,'pass'
            print >> outfile

    def generateClasses(self, outfile, element, delayed):
        wrt = outfile.write

        refs = element.getRefs() + element.getSubtypeNames()

        if not element.isComplex():
            return
        if element.getType() in AlreadyGenerated:
            return

        AlreadyGenerated.append(element.getType())
        name = element.getCleanName()

        wrt('\n')

        if refs:
            s1 = 'class %s%s(BaseFolder):\n' % (self.prefix, name)
        else:
            s1 = 'class %s%s(BaseContent):\n' % (self.prefix, name)

        wrt(s1)
        self.generateArcheSchema(outfile,element)
        self.generateMethods(outfile,element)

        #generateGettersAndSetters(outfile, element)
        print >> outfile,self.generateFti(element,refs)

        wrt('registerType(%s)' % name)
        wrt('# end class %s\n' % name)
        wrt('\n\n')


    def generateHeader(self, outfile):
        s1 = self.TEMPLATE_HEADER % time.ctime()
        outfile.write(s1)


    def generateStdFiles(self, target,projectName,generatedModules):
        #generates __init__.py, Extensions/Install.py and the skins directory
        #the result is a QuickInstaller installable product
        templdir=os.path.join(sys.path[0],'templates')
        initTemplate=open(os.path.join(templdir,'__init__.py')).read()

        imports='\n'.join(['    import '+m for m in generatedModules])

        initTemplate=initTemplate % {'project_name':projectName,'add_content_permission':'Add %s content' % projectName,'imports':imports }
        of=makeFile(os.path.join(target,'__init__.py'))
        of.write(initTemplate)
        of.close()

        installTemplate=open(os.path.join(templdir,'Install.py')).read()
        extDir=os.path.join(target,'Extensions')
        makeDir(extDir)
        of=makeFile(os.path.join(extDir,'Install.py'))
        of.write(installTemplate % {'project_dir':os.path.split(target)[1]})
        of.close()


    def generate(self, root, projectName=None ):
        dirMode=0
        outfile=None

        if not projectName:
            projectName=self.outfileName

        if not os.path.splitext(self.outfileName)[1]:
            dirMode=1

        if self.outfileName:
            if dirMode:
                makeDir(self.outfileName)
                makeDir(os.path.join(self.outfileName,'skins'))
                makeDir(os.path.join(self.outfileName,'skins',self.outfileName))
    ##            makeDir(os.path.join(outfileName,'skins',outfileName,outfileName+'_forms'))
    ##            makeDir(os.path.join(outfileName,'skins',outfileName,outfileName+'_views'))
    ##            makeDir(os.path.join(outfileName,'skins',outfileName,outfileName+'_scripts'))
            else:
                outfile = makeFile(self.outfileName)

            if outfile:
                self.generateHeader(outfile)
                for element in root.getChildren():
                    self.generateClasses(outfile, element, 0)
                while 1:
                    if len(DelayedElements) <= 0:
                        break
                    element = DelayedElements.pop()
                    self.generateClasses(outfile, element, 1)
                #generateMain(outfile, prefix, root)
                outfile.close()

            if dirMode:
                generatedModules=[]

                for element in root.getChildren():
                    module=element.getName()
                    generatedModules.append(module)
                    outfile=makeFile(os.path.join(self.outfileName,module+'.py'))
                    self.generateHeader(outfile)
                    self.generateClasses(outfile, element, 0)
                    outfile.close()

                while 1:
                    if len(DelayedElements) <= 0:
                        break
                    element = DelayedElements.pop()
                    module=element.getName()
                    generatedModules.append(module)
                    outfile=makeFile(os.path.join(self.outfileName,module+'.py'))
                    generateHeader(outfile)
                    generateClasses(outfile, element, 1)
                    outfile.close()
                #generateMain(outfile, prefix, root)
                self.generateStdFiles(self.outfileName,projectName,generatedModules)

    def parseAndGenerate(self):

        suff=os.path.splitext(self.xschemaFileName)[1].lower()

        if suff.lower() in ('.xmi','.xml'):
            print 'opening xmi'
            root=XMIParser.parse(self.xschemaFileName)
        elif suff.lower() in ('.zargo',):
            print 'opening zargo'
            zf=ZipFile(self.xschemaFileName)
            xmis=[n for n in zf.namelist() if os.path.splitext(n)[1].lower()=='.xmi']
            assert(len(xmis)==1)
            buf=zf.read(xmis[0])
            root=XMIParser.parse(xschema=buf)
        elif suff.lower() == '.xsd':
            root=XSDParser.parse(self.xschemaFileName)

        #if no output filename given, ry to guess it from the model
        if not self.outfileName:
            self.outfileName=root.getName()

        if not self.outfileName:
            raise TypeError,'output filename not specified'

        print 'outfile:',self.outfileName
        self.generate(root)

    TEMPLATE_HEADER = """\
# generated by ArchGenXML %s
from Products.Archetypes.public import *

    """

def main():
    args = sys.argv[1:]
    opts, args = getopt.getopt(args, 'f:a:t:o:s:p:')
    prefix = ''
    outfileName = None
    yesno={'yes':1,'y': 1, 'no':0, 'n':0}

    if len(args) < 1:
        usage()

    options={}

    for option in opts:
        if option[0] == '-p':
            options['prefix'] = option[1]
        elif option[0] == '-o':
            outfileName = option[1]
        elif option[0] == '-f':
            options['force'] = yesno[option[1]]
        elif option[0] == '-t':
            options['unknownTypesAsString'] = yesno[option[1]]
        elif option[0] == '-a':
            options['generateActions'] = yesno[option[1]]


    xschemaFileName = args[0]
    if not outfileName:
        if len(args) >= 2:
            outfileName=args[1]

    gen=ArchetypesGenerator(xschemaFileName,outfileName, **options)
    gen.parseAndGenerate()


USAGE_TEXT = """
Usage: python ArggenXML.py [ options ] <in_xsd_file>
Options:
    -o <outfilename>         Output file name for data representation classes
    -p <prefix>              Prefix string to be pre-pended to the class names
    -t <yes|no>              unknown attribut types will be treated as text
    -f <yes|no>              Force creation of output files.  Do not ask.
    -a <yes|no>              generates actions
"""

def usage():
    print USAGE_TEXT
    sys.exit(-1)

if __name__ == '__main__':
    main()
    #import pdb
    #pdb.run('main()')
