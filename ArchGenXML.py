#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Name:        ArchGenXML.py
# Purpose:
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# RCS-ID:      $Id: ArchGenXML.py,v 1.49 2003/11/05 10:37:41 yenzenz Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

# originally inspired Dave Kuhlman's generateDS Copyright (c) 2003 Dave Kuhlman

#from __future__ import generators   # only needed for Python 2.2

import sys, os.path, time
import getopt

from shutil import copy

from zipfile import ZipFile

from StringIO import StringIO
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
from utils import indent

#
# Representation of element definition.
#

class ArchetypesGenerator:

    force=1
    unknownTypesAsString=0
    generateActions=0
    prefix=''
    packages=[] #packages to scan for classes
    noclass=0   # if set no module is reverse engineered,
                #just an empty project + skin is created
    ape_support=0 #generate ape config and serializers/gateways for APE
    reservedAtts=['id',]
    portal_tools=['portal_tool']
    stub_stereotypes=['odStub','stub']
    def __init__(self,xschemaFileName,outfileName,projectName=None, **kwargs):
        self.outfileName=outfileName

        if not projectName:
            path=os.path.split(self.outfileName)
            if path[1]:
                self.projectName=path[1]
            else:
                #in case of trailing slash
                self.projectName=os.path.split(path[0])[1]
                
        print 'projectName:',self.projectName

        self.xschemaFileName=xschemaFileName
        self.__dict__.update(kwargs)

    ACT_TEMPL='''
           {'action': '%(action)s',
          'category': 'object',
          'id': '%(action_id)s',
          'name': '%(action_label)s',
          'permissions': ('%(permission)s',)},
          '''

    def generateMethodActions(self,element):
        outfile=StringIO()
        print >> outfile
        for m in element.getMethodDefs():
            if m.getTaggedValue('action') :
                dict={}
                dict['action']=m.getTaggedValue('action')
                dict['action_id']=m.getName()
                dict['action_label']=m.getTaggedValue('action_label',m.getName())
                dict['permission']=m.getTaggedValue('permission','View')

                print >>outfile,self.ACT_TEMPL % dict

            elif m.getTaggedValue('view') :
                dict={}
                dict['action']=m.getTaggedValue('view')
                dict['action_id']=m.getName()
                dict['action_label']=m.getTaggedValue('action_label',m.getName())
                dict['permission']=m.getTaggedValue('permission','View')
                f=makeFile(os.path.join(self.outfileName,'skins',self.projectName,m.getTaggedValue('view')+'.pt'),0)
                if f:
                    templdir=os.path.join(sys.path[0],'templates')
                    viewTemplate=open(os.path.join(templdir,'action_view.pt')).read()
                    f.write(viewTemplate)



                print >>outfile,self.ACT_TEMPL % dict

        return outfile.getvalue()

    def generateFti(self,element,subtypes):
        ''' '''

        actTempl='''
    actions=(
           {'action': 'string:${object_url}/portal_form/base_edit',
          'category': 'object',
          'id': 'edit',
          'name': 'edit',
          'permissions': ('Manage portal content',)},

           {'action': 'string:${object_url}/base_view',
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
        method_actions=self.generateMethodActions(element)
        actTempl +=method_actions

        actTempl+='''
              )
        '''
        ftiTempl='''

    # uncommant lines below when you need
    factory_type_information={
        'allowed_content_types':%(subtypes)s %(parentsubtypes)s,
        %(has_content_icon)s'content_icon':'%(content_icon)s',
        'immediate_view':'%(immediate_view)s',
        'global_allow':%(global_allow)d,
        'filter_content_types':1,
        }

        '''
        if self.generateActions:
            ftiTempl += actTempl

        #collect the allowed_subtypes from the parents
        parentsubtypes=''
        if element.getGenParents():
            parentsubtypes = '+ ' + ' + '.join(tuple([p.getCleanName()+".factory_type_information['allowed_content_types']" for p in element.getGenParents()]))
        immediate_view=element.getTaggedValue('immediate_view') or 'base_view'

        global_allow=not element.isDependent()
        if element.getStereoType() in self.portal_tools or element.isAbstract():
            global_allow=0

        has_content_icon=''
        content_icon=element.getTaggedValue('content_icon')
        if not content_icon:
            has_content_icon='#'
            content_icon = element.getCleanName()+'.gif'

        res=ftiTempl % {'subtypes':repr(tuple(subtypes)),
            'has_content_icon':has_content_icon,'content_icon':content_icon,
            'parentsubtypes':parentsubtypes,'global_allow':global_allow,'immediate_view':immediate_view}

        return res

    typeMap={
        'string':'''StringField('%(name)s',
                    %(other)s
                    ),''' ,
        'text':  '''TextField('%(name)s',
                    widget=TextAreaWidget(),
                    %(other)s
                    ),''' ,
        'richtext':  '''TextField('%(name)s',
                    widget=RichWidget(),
                    default_output_type='text/html',
                    allowable_content_types=('text/plain',
                        'text/structured',
                        'application/msword',
                        'text/html',),
                    %(other)s
                    ),''' ,

        'integer':'''IntegerField('%(name)s',
                    %(other)s
                    ),''',
        'float':'''FloatField('%(name)s',
                    %(other)s
                    ),''',
        'boolean':'''BooleanField('%(name)s',
                    %(other)s
                    ),''',
        'lines':'''LinesField('%(name)s',
                    %(other)s
                    ),''',
        'date':'''DateTimeField('%(name)s',
                    %(other)s
                    ),''',
        'image':'''ImageField('%(name)s',
                    sizes={'small':(100,100),'medium':(200,200),'large':(600,600)},
                    storage=AttributeStorage(),
                    %(other)s
                    ),''',
        'file':'''FileField('%(name)s',
                    storage=AttributeStorage(),
                    widget=FileWidget(),
                    %(other)s
                    ),''',
        'lines':'''LinesField('%(name)s',
                    %(other)s
                    ),''',
        'reference':'''ReferenceField('%(name)s',allowed_types=%(allowed_types)s,
                    multiValued=%(multiValued)d,
                    relationship='%(relationship)s',
                    %(other)s
                    ),''',
        'computed':'''ComputedField('%(name)s',
                    %(other)s
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
        'bool':'boolean',
        '':'string',     #
        None:'string',
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

    def getFieldAttributes(self,element):
        ''' converts the tagged values of a field into extended attributes for the archetypes field '''
        noparams=['documentation','element.uuid','transient','volatile']
        convtostring=['expression']
        lines=[]
        tgv=element.getTaggedValues()
        #print element.getName(),tgv
        for k in tgv.keys():
            if k not in noparams:
                v=tgv[k]
                if k in convtostring:
                    v=repr(v)
                lines.append('%s=%s'%(k,v))

        if lines:
            res='\n'+',\n'.join(lines)
        else:
            res=''

        return res

    def getFieldString(self, element):
        ''' gets the schema field code '''
        typename=str(element.type)

        if element.getMaxOccurs()>1:
            ctype='lines'
        else:
            ctype=self.coerceType(typename)

        templ=self.typeMap[ctype]

        return templ % {'name':element.getCleanName(),'type':element.type,'other':''}

    def getFieldStringFromAttribute(self, attr):
        ''' gets the schema field code '''
        #print 'getFieldStringFromAttribute:',attr.getName(),attr.type
        if not hasattr(attr,'type') or attr.type=='NoneType':
            ctype='string'
        else:
            ctype=self.coerceType(str(attr.type))

        templ=self.typeMap[ctype]
        defexp=''
        if attr.hasDefault():
            defexp='default='+attr.getDefault()+','

        other_attributes=self.getFieldAttributes(attr)
        res = templ % {'name':attr.getName(),'type':attr.getType(),'other':defexp+indent(other_attributes,5)}
        doc=attr.getDocumentation()
        if doc:
            res=indent(doc,2,'#')+'\n'+' '*8+res
        else:
            res=' '*8+res

        return res

    def getFieldStringFromAssociation(self, rel):
        ''' gets the schema field code '''
        #print 'getFieldStringFromAttribute:',attr.getName(),attr.type
        multiValued=0

        templ=self.typeMap['reference']
        obj=rel.toEnd.obj
        name=rel.toEnd.getName()
        relname=rel.getName()

        if obj.isAbstract():
            allowed_types= tuple(obj.getGenChildrenNames())
        else:
            allowed_types=(obj.getName(), ) + tuple(obj.getGenChildrenNames())

        if int(rel.toEnd.mult[1]) == -1:
            multiValued=1

        if name == 'None':
            name=obj.getName()+'_ref'

        return templ % {'name':name,'type':obj.getType(),
                'allowed_types':repr(allowed_types),
                'multiValued' : multiValued,
                'relationship':relname,'other':''}

    # Generate get/set/add member functions.
    def generateArcheSchema(self, outfile, element):
        parent_schemata=[p.getCleanName()+'.schema' for p in element.getGenParents()]

        if parent_schemata:
            parent_schemata_expr=' + '+' + '.join(parent_schemata)
        else:
            parent_schemata_expr=''

        print >> outfile,'    schema=BaseSchema %s + Schema((' % parent_schemata_expr
        refs=[]

        for attrDef in element.getAttributeDefs():
            name = attrDef.getName()
            if name in self.reservedAtts:
                continue
            mappedName = mapName(name)

            print >> outfile, self.getFieldStringFromAttribute(attrDef)
        for child in element.getChildren():
            name = child.getCleanName()
            if name in self.reservedAtts:
                continue
            unmappedName = child.getUnmappedCleanName()
            if child.getRef():
                refs.append(str(child.getRef()))

            if child.isIntrinsicType():
                print >> outfile, '    '*2 ,self.getFieldString(child)

        #print 'rels:',element.getName(),element.getFromAssociations()
        # and now the associations
        for rel in element.getFromAssociations():
            #print 'rel:',rel
            if 1 or rel.toEnd.mult==1: #XXX: for mult==-1 a multiselection widget must come
                name = rel.fromEnd.getName()

                if name in self.reservedAtts:
                    continue

                print >> outfile, '    '*2 ,self.getFieldStringFromAssociation(rel)


        print >> outfile,'    ),'
        marshaller=element.getTaggedValue('marshaller')
        if marshaller:
            print >> outfile, '    marshall='+marshaller

        print >> outfile,'    )'

    TEMPL_CONSTR_TOOL="""
    #toolconstructors have no id argument, the id is fixed
    def __init__(self):
        %s.__init__(self,'%s')
        """

    def generateMethods(self,outfile,element):
        print >> outfile

        print >> outfile,'    #Methods'
        for m in element.getMethodDefs():
            self.generateMethod(outfile,m)

    def generateMethod(self,outfile,m):
            #ignore actions and views here because they are
            #generated separately
        if m.getTaggedValue('action') or m.getTaggedValue('view'):
            return

        paramstr=''
        params=m.getParamExpressions()
        if params:
            paramstr=','+','.join(params)
            #print paramstr
        print >> outfile
        permission=m.getTaggedValue('permission')
        if permission:
            print >> outfile,indent("security.declareProtected(%s,'%s')" % (permission,m.getName()),1)
        print >> outfile,'    def %s(self%s):' % (m.getName(),paramstr)
        code=m.taggedValues.get('code','')
        doc=m.taggedValues.get('documentation','')
        if doc:
            print >> outfile, indent("'''\n%s\n'''" % doc ,2)

        if code:
            print >> outfile, indent('\n'+code,2)
        else:
            print >> outfile, indent('\n'+'pass',2)

        print >> outfile

    TEMPL_APE_HEADER='''
from Products.Archetypes.ApeSupport import constructGateway,constructSerializer


def ApeGateway():
    return constructGateway(%(class_name)s)

def ApeSerializer():
    return constructSerializer(%(class_name)s)

'''

    TEMPL_TOOL_HEADER='''
from Products.CMFCore.utils import UniqueObject

    '''
    def generateClasses(self, outfile, element, delayed):
        wrt = outfile.write
        wrt('\n')
        parentnames = [p.getCleanName() for p in element.getGenParents()]
        for p in parentnames:
            print >> outfile,'from %s import %s' % (p,p)

        additionalImports=element.getTaggedValue('imports')
        if additionalImports:
            wrt(additionalImports)
            wrt('\n')

        refs = element.getRefs() + element.getSubtypeNames(recursive=1)

        if not element.isComplex():
            return
        if element.getType() in AlreadyGenerated:
            return

        AlreadyGenerated.append(element.getType())
        name = element.getCleanName()

        wrt('\n')

        additionalParents=element.getTaggedValue('additional_parents')
        if additionalParents:
            parentnames=list(parentnames)+additionalParents.split(',')

        baseclass='BaseContent'
        if refs :
            folder_base_class=element.getTaggedValue('folder_base_class')
            if folder_base_class:
                baseclass=folder_base_class
            else:
                baseclass='BaseFolder'


        parentnames.insert(0,baseclass)
        if element.getStereoType() in self.portal_tools:
            print >>outfile,self.TEMPL_TOOL_HEADER
            parentnames.insert(0,'UniqueObject')


        parents=','.join(parentnames)
        if self.ape_support:
            print >>outfile,self.TEMPL_APE_HEADER % {'class_name':name}

        s1 = 'class %s%s(%s):\n' % (self.prefix, name, parents)

        wrt(s1)
        doc=element.getDocumentation()
        if doc:
            print >>outfile,indent("'''\n%s\n'''" % doc, 1)

        print >>outfile,indent('security = ClassSecurityInfo()',1)

        header=element.getTaggedValue('class_header')
        if header:
            print >>outfile,indent(header, 1)

        archetype_name=element.getTaggedValue('archetype_name')
        if not archetype_name: archetype_name=name

        print >> outfile,'''    portal_type = meta_type = '%s' ''' % name
        print >> outfile,'''    archetype_name = '%s'   #this name appears in the 'add' box ''' %  archetype_name
        self.generateArcheSchema(outfile,element)

        if element.getStereoType() in self.portal_tools:
            print >> outfile,self.TEMPL_CONSTR_TOOL % (baseclass,'portal_'+element.getName().lower())
            print >> outfile

        self.generateMethods(outfile,element)

        #generateGettersAndSetters(outfile, element)
        print >> outfile,self.generateFti(element,refs)

        wrt('registerType(%s)' % name)
        wrt('# end class %s\n' % name)
        wrt('\n\n')


    def generateHeader(self, outfile):
        s1 = self.TEMPLATE_HEADER % time.ctime()
        outfile.write(s1)


    TEMPL_TOOLINIT='''
    tools=[%s]
    utils.ToolInit( PROJECTNAME+' Tools',
                tools = tools,
                product_name = PROJECTNAME,
                icon='tool.gif'
                ).initialize( context )'''

    TEMPL_CONFIGLET_INSTALL='''
    portal_control_panel.registerConfiglet( '%(tool_name)s' #id of your Product
        , '%(configlet_title)s' # Title of your Product
        , 'string:${portal_url}/%(configlet_url)s/'
        , '%(configlet_condition)s' # a condition
        , 'Manage portal' # access permission
        , '%(configlet_section)s' # section to which the configlet should be added: (Plone,Products,Members)
        , 1 # visibility
        , '%(tool_name)sID'
        , '%(configlet_icon)s' # icon in control_panel
        , '%(configlet_description)s'
        , None
        )
    # set title of tool:
    tool=getToolByName(self, '%(tool_instance)s')
    tool.title='%(configlet_title)s'

    # dont allow tool listed as content in navtree
    try:
        idx=self.portal_properties.navtree_properties.metaTypesNotToList.index('%(tool_name)s')
    except ValueError:
        self.portal_properties.navtree_properties.metaTypesNotToList.append('%(tool_name)s')
    except:
        raise'''

    TEMPL_CONFIGLET_UNINSTALL='''
    portal_control_panel.unregisterConfiglet('%(tool_name)s')

    # remove prodcut from navtree properties
    try:
        self.portal_properties.navtree_properties.metaTypesNotToList.remove('%(tool_name)s')
    except ValueError:
        pass
    except:
        raise'''



    def generateStdFiles(self, target,projectName,generatedModules):
        #generates __init__.py, Extensions/Install.py and the skins directory
        #the result is a QuickInstaller installable product

        #remove trailing slash
        if target[-1] in ('/','\\'):
            target=target[:-1]

        templdir=os.path.join(sys.path[0],'templates')
        initTemplate=open(os.path.join(templdir,'__init__.py')).read()

        imports='\n'.join(['    import '+m for m in generatedModules])

        toolinit=self.TEMPL_TOOLINIT % ','.join([m+'.'+c.getName() for c,m in self.generatedClasses if c.getStereoType() in self.portal_tools])

        initTemplate=initTemplate % {'project_name':projectName,'add_content_permission':'Add %s content' % projectName,'imports':imports, 'toolinit':toolinit }
        of=makeFile(os.path.join(target,'__init__.py'))
        of.write(initTemplate)
        of.close()

        installTemplate=open(os.path.join(templdir,'Install.py')).read()
        extDir=os.path.join(target,'Extensions')
        makeDir(extDir)
        of=makeFile(os.path.join(extDir,'Install.py'))

        #handling of tools
        autoinstall_tools=[c[0].getName() for c in self.generatedClasses if c[0].getStereoType() in self.portal_tools and c[0].getTaggedValue('autoinstall') == '1' ]

        if autoinstall_tools:
            copy(os.path.join(templdir,'tool.gif'), os.path.join(target,'tool.gif') )

        #handling of tools with configlets
        register_configlets='#auto build\n'
        unregister_configlets='#auto build\n'
        for c in [cn[0] for cn in self.generatedClasses
                            if cn[0].getStereoType() in self.portal_tools and
                               cn[0].getTaggedValue('autoinstall') == '1' and
                               cn[0].getTaggedValue('configlet') != '0'
                 ]:
            configlet_title=c.getTaggedValue('configlet_title')
            if not configlet_title:
                configlet_title=c.getName()

            configlet_section=c.getTaggedValue('configlet_section')
            if not configlet_section or not configlet_section in ['Plone','Products','Members']:
                configlet_section='Products'

            configlet_condition=c.getTaggedValue('configlet_condition')
            if not configlet_condition:
                configlet_condition=''

            configlet_icon=c.getTaggedValue('configlet_icon')
            if not configlet_icon:
                configlet_icon='plone_icon'

            configlet_view='/'+c.getTaggedValue('configlet_view')

            configlet_descr=c.getTaggedValue('configlet_description')
            if not configlet_descr:
                configlet_descr='ArchGenXML generated Configlet "'+configlet_title+'" in Tool "'+c.getName()+'".'

            register_configlets+=self.TEMPL_CONFIGLET_INSTALL % {
                'tool_name':c.getName(),
                'tool_instance':'portal_'+c.getName().lower(),
                'configlet_title':configlet_title,
                'configlet_url':'portal_'+c.getName().lower()+configlet_view,
                'configlet_condition':configlet_condition,
                'configlet_section':configlet_section,
                'configlet_icon':configlet_icon,
                'configlet_description':configlet_descr,
                } + '\n'

            unregister_configlets+=self.TEMPL_CONFIGLET_UNINSTALL % {
                'tool_name':c.getName()
                } + '\n'

        of.write(installTemplate % {'project_dir':os.path.split(target)[1],
                                    'autoinstall_tools':repr(autoinstall_tools),
                                    'register_configlets':register_configlets,
                                    'unregister_configlets':unregister_configlets
                                   })
        of.close()

    TEMPL_APECONFIG_BEGIN='''<?xml version="1.0"?>

<!-- Basic Zope 2 configuration for Ape. -->

<configuration>'''
    def generateApeConf(self, target,projectName):
        #generates apeconf.xml

        #remove trailing slash
        if target[-1] in ('/','\\'):
            target=target[:-1]

        templdir=os.path.join(sys.path[0],'templates')
        apeconfig_object=open(os.path.join(templdir,'apeconf_object.xml')).read()
        apeconfig_folder=open(os.path.join(templdir,'apeconf_folder.xml')).read()

        of=makeFile(os.path.join(target,'apeconf.xml'))
        print >> of,self.TEMPL_APECONFIG_BEGIN
        for el in self.root.getChildren():
            print >>of
            if el.getRefs() + el.getSubtypeNames(recursive=1):
                print >>of,apeconfig_folder % {'project_name':projectName,'class_name':el.getCleanName()}
            else:
                print >>of,apeconfig_object % {'project_name':projectName,'class_name':el.getCleanName()}

        print >>of,'</configuration>'
        of.close()

    def generate(self, root, projectName=None ):
        dirMode=0
        outfile=None

        if not os.path.splitext(self.outfileName)[1]:
            dirMode=1

        if self.outfileName:
            if dirMode:
                makeDir(self.outfileName)
                makeDir(os.path.join(self.outfileName,'skins'))
                makeDir(os.path.join(self.outfileName,'skins',self.projectName))
                makeDir(os.path.join(self.outfileName,'skins',self.projectName+'_public'))
    ##            makeDir(os.path.join(self.outfileName,'skins',self.projectName,self.projectName+'_forms'))
    ##            makeDir(os.path.join(self.outfileName,'skins',self.projectName,self.projectName+'_views'))
    ##            makeDir(os.path.join(self.outfileName,'skins',self.projectName,self.projectName+'_scripts'))
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
                generatedModules=self.generatedModules=[]
                self.generatedClasses=[]

                for element in root.getChildren():
                    #skip tool classes
                    if element.getStereoType() in self.stub_stereotypes:
                        continue

                    module=element.getName()
                    generatedModules.append(module)
                    outfile=makeFile(os.path.join(self.outfileName,module+'.py'))
                    self.generateHeader(outfile)
                    self.generateClasses(outfile, element, 0)
                    self.generatedClasses.append([element,module])
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
                if self.ape_support:
                    self.generateApeConf(self.outfileName,projectName)

    def parseAndGenerate(self):
        
        suff=os.path.splitext(self.xschemaFileName)[1].lower()

        if not self.noclass:
            if suff.lower() in ('.xmi','.xml'):
                print 'opening xmi'
                self.root=root=XMIParser.parse(self.xschemaFileName,packages=self.packages)
            elif suff.lower() in ('.zargo',):
                print 'opening zargo'
                zf=ZipFile(self.xschemaFileName)
                xmis=[n for n in zf.namelist() if os.path.splitext(n)[1].lower()=='.xmi']
                assert(len(xmis)==1)
                buf=zf.read(xmis[0])
                self.root=root=XMIParser.parse(xschema=buf,packages=self.packages)
            elif suff.lower() == '.xsd':
                self.root=root=XSDParser.parse(self.xschemaFileName)

            #if no output filename given, ry to guess it from the model
            if not self.outfileName:
                self.outfileName=root.getName()

            if not self.outfileName:
                raise TypeError,'output filename not specified'

            print 'outfile:',self.outfileName
        else:
            self.root=root=XMIParser.XMIElement() #create empty element

        self.generate(root)

    TEMPLATE_HEADER = """\
# generated by ArchGenXML %s
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *

    """

def main():
    version()
    args = sys.argv[1:]
    opts, args = getopt.getopt(args, 'f:a:t:o:s:p:P:n',['ape','actions','ape-support','noclass'])
    prefix = ''
    outfileName = None
    yesno={'yes':1,'y': 1, 'no':0, 'n':0}

    options={}

    for option in opts:
        if option[0] == '-p':
            options['prefix'] = option[1]
        elif option[0] == '-o':
            outfileName = option[1]
        elif option[0] == '-P':
            options['packages'] = option[1].split(',')
            print 'packs:',options['packages']
        elif option[0] == '-f':
            options['force'] = yesno[option[1]]
        elif option[0] == '-t':
            options['unknownTypesAsString'] = yesno[option[1]]
        elif option[0] == '-a':
            options['generateActions'] = yesno[option[1]]
        elif option[0] == '--actions':
            options['generateActions'] = 1
        elif option[0] == '--noactions':
            options['generateActions'] = 0
        if option[0] == '-n':
            options['noclass'] = 1
        if option[0] == '--noclass':
            options['noclass'] = 1
        if option[0] in ('--ape','--ape-support'):
            options['ape_support'] = 1

    if len(args) < 1 and not options.get('noclass',0):
        usage()

    if len(args):
        xschemaFileName = args[0]
    else:
        xschemaFileName = ''


    if not outfileName:
        if len(args) >= 2:
            outfileName=args[1]
            
    gen=ArchetypesGenerator(xschemaFileName,outfileName, **options)
    gen.parseAndGenerate()

ARCHGENXML_VERSION_LINE = """\
ArchGenXML %(version)s 
(c) 2003 BlueDynamics, under GNU Public License 2.0 or later
"""

USAGE_TEXT = """
Usage: python ArchGenXML.py [ options ] <in_xsd_file>
Options:
    -o <outfilename>         Output file path for data representation classes.
                             Last part of used for internal directory namings.
    -p <prefix>              Prefix string to be pre-pended to the class names
    -t <yes|no>              unknown attribut types will be treated as text
    -f <yes|no>              Force creation of output files.  Do not ask.
    -a <yes|no>              generates actions
    -P <packagename>         package to parse
    --ape-support            generate apeconf.xml and generators for ape (needs Archetypes 1.1+)
"""

def usage():
    print USAGE_TEXT
    sys.exit(-1)
    
def version():
    ver=open(os.path.join(sys.path[0],'version.txt')).read().strip()
    print ARCHGENXML_VERSION_LINE % {'version': ver}

if __name__ == '__main__':
    main()
    #import pdb
    #pdb.run('main()')
