#!/usr/bin/env python

#-----------------------------------------------------------------------------
# Name:        ArchGenXML.py
# Purpose:     generating plone products (archetypes code) out of an UML-model
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# RCS-ID:      $Id: ArchGenXML.py,v 1.99 2004/02/26 10:46:55 zworkb Exp $
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
import PyParser #for extracting the method codes out of the destination src
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
from utils import indent, getExpression

#
# Representation of element definition.
#

class ArchetypesGenerator:

    force=1
    unknownTypesAsString=0
    generateActions=1
    generateDefaultActions=0
    prefix=''
    packages=[] #packages to scan for classes
    noclass=0   # if set no module is reverse engineered,
                #just an empty project + skin is created
    ape_support=0 #generate ape config and serializers/gateways for APE
    method_preservation=1 #should the method bodies be preserved? defaults now to 0 will change to 1
    i18n_support=0
    
    reservedAtts=['id',]
    portal_tools=['portal_tool']
    stub_stereotypes=['odStub','stub']
    left_slots=[]
    right_slots=[]
    creation_permission=None
    detailled_creation_permissions=0
    
    parsed_class_sources={} #dict containing the parsed sources by class names (for preserving method codes)
    parsed_sources=[] #list of containing the parsed sources (for preserving method codes)
    
    nonstring_tgvs=['widget','vocabulary','required'] #taggedValues that are not strings, e.g. widget or vocabulary
    
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
           {'action':      %(action)s,
            'category':    %(action_category)s,
            'id':          '%(action_id)s',
            'name':        '%(action_label)s',
            'permissions': (%(permission)s,)},
          '''

    def generateMethodActions(self,element):
        outfile=StringIO()
        print >> outfile
        for m in element.getMethodDefs():
            if m.getStereoType() in ['action','view','form']:
                action_name=m.getTaggedValue(m.getStereoType(), m.getName()).strip()
                print 'generating ' + m.getStereoType()+':',action_name
                dict={}

                
                if not action_name.startswith('string:') and not action_name.startswith('python:'):
                    action_target='string:$object_url/'+action_name
                else:
                    action_target=action_name
                    
                dict['action']=getExpression(action_target)
                dict['action_category']=getExpression(m.getTaggedValue('category','object'))
                dict['action_id']=m.getTaggedValue('id',m.getName())
                dict['action_label']=m.getTaggedValue('action_label') or m.getTaggedValue('label',m.getName()) # action_label is deprecated and for backward compability only!
                dict['permission']=getExpression(m.getTaggedValue('permission','View'))

                print >>outfile, self.ACT_TEMPL % dict

            if m.getStereoType() == 'view':
                f=makeFile(os.path.join(self.outfileName,'skins',self.projectName,action_name+'.pt'),0)
                if f:
                    templdir=os.path.join(sys.path[0],'templates')
                    viewTemplate=open(os.path.join(templdir,'action_view.pt')).read()
                    f.write(viewTemplate)

            elif m.getStereoType() == 'form':
                f=makeFile(os.path.join(self.outfileName,'skins',self.projectName,action_name+'.cpt'),0)
                if f:
                    templdir=os.path.join(sys.path[0],'templates')
                    viewTemplate=open(os.path.join(templdir,'action_view.pt')).read()
                    f.write(viewTemplate)

        return outfile.getvalue()

    MODIFY_FTI = """\
def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in [%(hideactions)s]:
            a['visible'] = 0
    return fti
""" 

    def generateModifyFti(self,element):
        hide_actions=element.getTaggedValue('hide_actions', '').strip()
        if not hide_actions:
            return ''
        hide_actions=', '.join(["'"+a.strip()+"'" for a in hide_actions.split('\n')])
        
        print 'hide actions: ', hide_actions
        
        return self.MODIFY_FTI % {'hideactions':hide_actions, }
        

    def generateFti(self,element,subtypes):
        ''' '''

        actTempl='''
    actions= %s (
        '''
        base_actions=element.getTaggedValue('base_actions', '').strip()
        if base_actions:
            base_actions += ' + '
            actTempl = actTempl % base_actions
        else:
            actTempl = actTempl % ''
        
        if self.generateDefaultActions or element.getTaggedValue('default_actions'):
            actTempl += '''
           {'action': 'string:${object_url}/portal_form/base_edit',
          'category': 'object',
          'id': 'edit',
          'name': 'Edit',
          'permissions': ('Manage portal content',)},

           {'action': 'string:${object_url}/base_view',
          'category': 'object',
          'id': 'view',
          'name': 'View',
          'permissions': ('View',)},

        '''
            if subtypes:
                actTempl=actTempl+'''
           {'action': 'folder_listing',
          'category': 'object',
          'id': 'folder_listing',
          'name': 'Folder Listing',
          'permissions': ('View',)},

        '''
    
        method_actions=self.generateMethodActions(element)
        actTempl +=method_actions
        actTempl+='''
          )
        '''
            
        ftiTempl='''

    # uncomment lines below when you need
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
        #print 'dependent:',element.isDependent(),element.getName()
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
%(other)s
        ),''' ,
        'richtext':  '''TextField('%(name)s',
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
            storage=AttributeStorage(),
%(other)s
        ),''',
        'file':'''FileField('%(name)s',
                    storage=AttributeStorage(),
%(other)s
        ),''',
        'lines':'''LinesField('%(name)s',
%(other)s
        ),''',
        'reference':'''ReferenceField('%(name)s',
            allowed_types=%(allowed_types)s,
            multiValued=  %(multiValued)d,
            relationship= '%(relationship)s',
%(other)s
        ),''',
        'computed':'''ComputedField('%(name)s',
%(other)s
        ),''',
        'photo':'''PhotoField('%(name)s',
%(other)s
        ),''',
    }

    widgetMap={
        'text': 'TextAreaWidget' ,
        'richtext': 'RichWidget' ,
        'file': 'FileWidget',
        'date' : 'CalendarWidget'
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
        'dict':'string',
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
            ctype=self.coerceMap.get(typename.lower(),None)
            if not ctype:
                raise ValueError,'Warning: unknown datatype : %s (use the option --unknown-types-as-string to force unknown types to be converted to string' % typename

        #print ctype
        return ctype

    def getFieldAttributes(self,element):
        ''' converts the tagged values of a field into extended attributes for the archetypes field '''
        noparams=['documentation','element.uuid','transient','volatile','widget']
        convtostring=['expression']
        lines=[]
        tgv=element.getTaggedValues()
        #print element.getName(),tgv
        for k in tgv.keys():
            if k not in noparams and not k.startswith('widget:'):
                v=tgv[k]
                
                if k not in self.nonstring_tgvs:
                    v=getExpression(v)
                    
                #if k in convtostring:
                #    v=repr(v)
                
                n=0
                formatted=''
                for line in v.split('\n'):
                    if formatted:
                        formatted+=(len(k)+1)*' '
                    formatted+=line+'\n'
                lines.append('%s=%s'%(k,formatted.strip()))

        if lines:
            res='\n'+',\n'.join(lines)
        else:
            res=''

        return res

    def getWidget(self, type, element):
        ''' returns either default widget, widget according to
        attribute or no widget '''
        tgv=element.getTaggedValues()
        widgetcode='widget=%s'%type.capitalize()+'Widget('
        custom = 0 #is there a custom setting for widget?
        widgetoptions=[t for t in tgv.items() if t[0].startswith('widget:')]
        
        if tgv.has_key('widget'):
            # Custom widget defined in attributes
            custom=1
            formatted=''
            for line in tgv['widget'].split('\n'):
                if formatted:
                    line=indent(line.strip(),1)
                formatted+=line+'\n'
            widgetcode = '''widget=%s''' % formatted
            
        elif self.widgetMap.has_key(type):
            # Standard widget for this type found in widgetMap
            custom=1
            widgetcode = '''widget=%s''' % self.widgetMap[type]
                    
        if ')' not in widgetcode:
            widgetlines=[]
            for tup in widgetoptions:
                key=tup[0][7:]
                val=tup[1]
                if key not in self.nonstring_tgvs:
                    val=getExpression(val)
                widgetlines.append('%s=%s'%(key,val))
          
            if '(' not in widgetcode:
                widgetcode += '('
            widgetcode += indent(',\n'.join(widgetlines),1,skipFirstRow=1)
            widgetcode +=')'
        
        if custom or len(widgetoptions):
            return widgetcode+','
        else:
            return ''

        
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
        if not hasattr(attr,'type') or attr.type=='NoneType':
            ctype='string'
        else:
            ctype=self.coerceType(str(attr.type))

        templ=self.typeMap[ctype]
        defexp=''
        if attr.hasDefault():
            defexp+=indent('default='+attr.getDefault()+',\n',3)
        
        if ctype=='image' and not attr.getTaggedValue('sizes',None):
            defexp+=indent("sizes  = {'small':(100,100),'medium':(200,200),'large':(600,600)},\n",3)

        other_attributes = (self.getWidget(ctype, attr) +
                            self.getFieldAttributes(attr))

        if self.i18n_support and attr.isI18N():
            templ='I18N'+templ
            
        res = templ % {'name': attr.getName(),
                       'type': attr.getType(),
                       'other':defexp+indent(other_attributes,3)
              }
        doc=attr.getDocumentation()
        if doc:
            res=indent(doc,2,'#')+'\n'+' '*8+res
        else:
            res=' '*8+res

        return res

    def getFieldStringFromAssociation(self, rel):
        ''' gets the schema field code '''
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
        if name == None:
            name=obj.getName()+'_ref'

        other_attributes = (self.getWidget('Reference', rel.toEnd) +
                            self.getFieldAttributes(rel.toEnd))

        return templ % {'name': name,
                        'type':         obj.getType(),
                        'allowed_types':repr(allowed_types),
                        'multiValued':  multiValued,
                        'relationship': relname,
                        'other':        indent(other_attributes,3)
               }

    # Generate get/set/add member functions.
    def generateArcheSchema(self, outfile, element):
        parent_schemata=[p.getCleanName()+'.schema' for p in element.getGenParents()]

        base_schema = element.getTaggedValue('base_schema', None)

        if parent_schemata:
            parent_schemata_expr=' + '+' + '.join(parent_schemata)
        else:
            parent_schemata_expr=''

        if base_schema:
            print >> outfile,'    schema=%s %s + Schema((' % (base_schema, parent_schemata_expr)
        elif self.i18n_support and element.isI18N():
            print >> outfile,'    schema=I18NBaseSchema %s + Schema((' % parent_schemata_expr
        else:
            print >> outfile,'    schema=BaseSchema %s + Schema((' % parent_schemata_expr
            
        refs=[]

        for attrDef in element.getAttributeDefs():
            name = attrDef.getName()
            #if name in self.reservedAtts:
            #    continue
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
                print >> outfile
                print >> outfile, '    '*2+self.getFieldStringFromAssociation(rel)


        print >> outfile,'    ),'
        marshaller=element.getTaggedValue('marshaller') or element.getTaggedValue('marshall')
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
            self.generateMethod(outfile,m,element)
            
        method_names=[m.getName() for m in element.getMethodDefs()]
        
        #if __init__ has to be generated for tools i want _not_ __init__ to be preserved
        #if it is added to method_names it wont be recognized as a manual method (hacky but works)
        if element.getStereoType() in self.portal_tools and '__init__' not in method_names:
            method_names.append('__init__')
            
        if self.method_preservation:
            cl=self.parsed_class_sources.get(element.getName(),None)
            if cl:
                manual_methods=[mt for mt in cl.methods.values() if mt.name not in method_names]
                if manual_methods:
                    print >> outfile, '    #manually created methods\n'
                    
                for mt in manual_methods:
                    print >> outfile, mt.src
                    print >> outfile
        

    def generateMethod(self,outfile,m,klass):
        #ignore actions and views here because they are
        #generated separately
        if m.getStereoType() in ['action','view','form']:
            return
        
        #print 'generatemethod:',m.getStereoType(),m.getName()
        if m.getStereoType()=='portlet_view':
            view_name=m.getTaggedValue('view').strip() or m.getName()
            print 'generating portlet:',view_name
            autoinstall=m.getTaggedValue('autoinstall')
            #print 'autoinstall:',autoinstall,m.getTaggedValues()
            portlet='here/%s/macros/portlet' % view_name
            #print 'portlet:',portlet
            if autoinstall=='left':
                self.left_slots.append(portlet)
            if autoinstall=='right':
                self.right_slots.append(portlet)
                
            f=makeFile(os.path.join(self.outfileName,'skins',self.projectName,view_name+'.pt'),0)
            if f:
                templdir=os.path.join(sys.path[0],'templates')
                viewTemplate=open(os.path.join(templdir,'portlet_template.pt')).read()
                f.write(viewTemplate % {'method_name':m.getName()})
            return
            
        
        paramstr=''
        params=m.getParamExpressions()
        if params:
            paramstr=','+','.join(params)
            #print paramstr
        print >> outfile
        permission=getExpression(m.getTaggedValue('permission'))
        if permission:
            print >> outfile,indent("security.declareProtected(%s,'%s')" % (permission,m.getName()),1)
            
        cls=self.parsed_class_sources.get(klass.getName(),None)
        
        if cls:
            method_code=cls.methods.get(m.getName())
        else:
            #print 'method not found:',m.getName()
            method_code=None
            
        if self.method_preservation and method_code:
            print 'preserve method:',method_code.name
            print >>outfile, method_code.src
        else:
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
        
        #also check if the parent classes can have subobjects
        baserefs=[]
        for b in element.getGenParents():
            baserefs.extend(b.getRefs())
            baserefs.extend(b.getSubtypeNames(recursive=1))
            
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
        if refs or baserefs or element.getTaggedValue('folderish') == '1':                
            # folderish
            baseclass='BaseFolder'
            folder_base_class=element.getTaggedValue('base_class') or element.getTaggedValue('folder_base_class') # folder_base_class is deprecated and for backward compability only
            if folder_base_class:
                baseclass=folder_base_class            

            if self.i18n_support and element.isI18N():
                baseclass='I18NBaseFolder'
        else:
            #contentish
            content_base_class=element.getTaggedValue('base_class')
            if content_base_class:
                baseclass=content_base_class        
            if self.i18n_support and element.isI18N():
                baseclass='I18NBaseContent'
            
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

        archetype_name=element.getTaggedValue('archetype_name') or element.getTaggedValue('label')
        if not archetype_name: archetype_name=name

        print >> outfile,'''    portal_type = meta_type = '%s' ''' % name
        print >> outfile,'''    archetype_name = '%s'   #this name appears in the 'add' box ''' %  archetype_name
        self.generateArcheSchema(outfile,element)

        if element.getStereoType() in self.portal_tools:
            tool_instance_name=element.getTaggedValue('tool_instance_name') or 'portal_'+element.getName().lower()
            print >> outfile,self.TEMPL_CONSTR_TOOL % (baseclass,tool_instance_name)
            print >> outfile

        self.generateMethods(outfile,element)

        #generateGettersAndSetters(outfile, element)
        print >> outfile, self.generateFti(element,refs)
        
        print >> outfile, self.generateModifyFti(element)   

        wrt('registerType(%s)\n' % name)
        wrt('# end of class %s\n'   % name)
        wrt('\n\n')

    MODULE_INFO_HEADER = """\
#------------------------------------------------------------------------------
# Name:         %(filename)s
# Purpose:      %(purpose)s 
#
# Author:       %(author)s <%(email)s>
# generated by: ArchGenXML Version %(version)s http://sf.net/projects/archetypes/
#
# Created:      %(date)s
# RCS-ID:       $Id: ArchGenXML.py,v 1.99 2004/02/26 10:46:55 zworkb Exp $
# Copyright:    (c) %(year)s by %(copyright)s
# Licence:      %(licence)s
#------------------------------------------------------------------------------
"""

    def generateModuleInfoHeader(self, outfile, modulename, element): 
        if self.no_module_info_header:
            return
        
        #deal with multiline docstring
        purposeline='\n#               '.join((element.getDocumentation() or 'unknown').split('\n'))
        
        author= element.getTaggedValue('author',  self.author) or 'unknown'

        fileheaderinfo = {'filename': modulename+'.py',
                          'purpose':  purposeline,
                          'author':   author,
                          'email':    element.getTaggedValue('email', self.email) or 'unknown',
                          'version':  self.version,
                          'date':     time.ctime(),
                          'year':     str(time.localtime()[0]),
                          'copyright':element.getTaggedValue('copyright', self.copyright) or author,
                          'licence':  element.getTaggedValue('licence', self.licence) or 'GNU General Public Licence (GPL) Version 2 or later',
        }        
        outfile.write(self.MODULE_INFO_HEADER % fileheaderinfo)

    def generateHeader(self, outfile, i18n=0):
        if i18n:
            s1 = self.TEMPLATE_HEADER_I18N 
        else:
            s1 = self.TEMPLATE_HEADER 
            
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
        self.portal_properties.navtree_properties._p_changed=1        
    except ValueError:
        self.portal_properties.navtree_properties.metaTypesNotToList.append('%(tool_name)s')
    except:
        raise'''

    TEMPL_CONFIGLET_UNINSTALL='''
    portal_control_panel.unregisterConfiglet('%(tool_name)s')

    # remove prodcut from navtree properties
    try:
        self.portal_properties.navtree_properties.metaTypesNotToList.remove('%(tool_name)s')
        self.portal_properties.navtree_properties._p_changed=1        
    except ValueError:
        pass
    except:
        raise'''

    def getGeneratedTools(self):
        ''' returns a list of  generated tools '''
        return [c[0] for c in self.generatedClasses if c[0].getStereoType() in self.portal_tools]

    TEMPL_DETAILLED_CREATION_PERMISSIONS='''
    # and now give it some extra permissions so that i
    # can control them on a per class limit
    for i in range(0,len(content_types)):
        perm='Add '+ capitalize(ftis[i]['id'])+'s'
        methname='add'+capitalize(ftis[i]['id'])
        meta_type = ftis[i]['meta_type']

        context.registerClass(
            meta_type=meta_type,
            constructors = (
                            getattr(locals()[meta_type],'add'+capitalize(meta_type)),
                               )
            , permission = perm
            )
'''
    def generateStdFiles(self, target,projectName,generatedModules):
        #generates __init__.py, Extensions/Install.py and the skins directory
        #the result is a QuickInstaller installable product
        print 'stdfiles'
        #remove trailing slash
        if target[-1] in ('/','\\'):
            target=target[:-1]

        templdir=os.path.join(sys.path[0],'templates')
        initTemplate=open(os.path.join(templdir,'__init__.py')).read()
        imports='\n'.join(['    import '+m for m in generatedModules])
        tool_classes=self.getGeneratedTools()

        if tool_classes:
            toolinit=self.TEMPL_TOOLINIT % ','.join([m+'.'+c.getName() for c,m in self.generatedClasses if c.getStereoType() in self.portal_tools])
        else: toolinit=''

        add_content_permission = self.creation_permission or 'Add %s content' % self.projectName
        init_params={'project_name':self.projectName,'add_content_permission': getExpression(add_content_permission),'imports':imports, 'toolinit':toolinit }

        if self.detailled_creation_permissions:
            init_params['extra_perms']=self.TEMPL_DETAILLED_CREATION_PERMISSIONS
        else:
            init_params['extra_perms']=""

        initTemplate=initTemplate % init_params
        of=makeFile(os.path.join(target,'__init__.py'))
        of.write(initTemplate)
        of.close()

        installTemplate=open(os.path.join(templdir,'Install.py')).read()
        extDir=os.path.join(target,'Extensions')
        makeDir(extDir)
        of=makeFile(os.path.join(extDir,'Install.py'))

        #handling of hide_folder_tabs
        hide_folder_tabs=''
        for c in [cn[0] for cn in self.generatedClasses if cn[0].getTaggedValue('hide_folder_tabs',None)]:
            hide_folder_tabs+="'"+c.getName()+"', "

        #handling of tools
        autoinstall_tools=[c[0].getName() for c in self.generatedClasses if c[0].getStereoType() in self.portal_tools and c[0].getTaggedValue('autoinstall') == '1' ]

        if self.getGeneratedTools():
            copy(os.path.join(templdir,'tool.gif'), os.path.join(target,'tool.gif') )

        #handling of tools with configlets
        register_configlets='#auto build\n'
        unregister_configlets='#auto build\n'
        for c in [cn[0] for cn in self.generatedClasses
                            if cn[0].getStereoType() in self.portal_tools and
                               cn[0].getTaggedValue('autoinstall','0') == '1' and
                               cn[0].getTaggedValue('configlet', None)
                 ]:
            configlet_title=    c.getTaggedValue('configlet_title',c.getName())
            configlet_section=  c.getTaggedValue('configlet_section', 'Products')
            if not configlet_section in ['Plone','Products','Members']:
                configlet_section='Products'

            configlet_condition=c.getTaggedValue('configlet_condition','')
            configlet_icon=     c.getTaggedValue('configlet_icon','site_icon.gif')
            configlet_view=     '/'+c.getTaggedValue('configlet_view')
            configlet_descr=    c.getTaggedValue('configlet_description',
                                                 'ArchGenXML generated Configlet "'+configlet_title+'" in Tool "'+c.getName()+'".')

            tool_instance_name = c.getTaggedValue('tool_instance_name', 'portal_'+ c.getName().lower() )
            register_configlets+=self.TEMPL_CONFIGLET_INSTALL % {
                'tool_name':c.getName(),
                'tool_instance': tool_instance_name,
                'configlet_title':configlet_title,
                'configlet_url':tool_instance_name+configlet_view,
                'configlet_condition':configlet_condition,
                'configlet_section':configlet_section,
                'configlet_icon':configlet_icon,
                'configlet_description':configlet_descr,
                } + '\n'

            unregister_configlets+=self.TEMPL_CONFIGLET_UNINSTALL % {
                'tool_name':c.getName()
                } + '\n'

        of.write(installTemplate % {'project_dir':os.path.split(target)[1],
                                    'no_use_of_folder_tabs':'['+hide_folder_tabs+']',
                                    'autoinstall_tools':repr(autoinstall_tools),
                                    'register_configlets':register_configlets,
                                    'unregister_configlets':unregister_configlets,
                                    'left_slots':repr(self.left_slots),
                                    'right_slots':repr(self.right_slots)
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
            if el.isInternal() or el.getStereoType() in self.stub_stereotypes:
                continue

            print >>of
            if el.getRefs() + el.getSubtypeNames(recursive=1):
                print >>of,apeconfig_folder % {'project_name':self.projectName,'class_name':el.getCleanName()}
            else:
                print >>of,apeconfig_object % {'project_name':self.projectName,'class_name':el.getCleanName()}

        print >>of,'</configuration>'
        of.close()

    def generate(self, root, projectName=None ):
        dirMode=0
        outfile=None

        dirMode=1
        
        READMEHIGHEST = """\
Directory 'skins/%s_public':

This skin layer has highest priority, put templates and scripts here that are 
supposed to overload existing ones. 

I.e. if you want to change want a site-wide change of Archetypes skins 
base_edit, base_view, etc or also Plone skins like maintemplate or 
document_view, put it in here."""
        
        READMELOWEST = """\
Directory 'skins/%s':

This skin layer has low priority, put unique templates and scripts here.

I.e. if you to want to create own unique views or forms for your product, this 
is the right place."""
        

        if self.outfileName:
            #create the directories
            makeDir(self.outfileName)
            makeDir(os.path.join(self.outfileName,'skins'))
            makeDir(os.path.join(self.outfileName,'skins',self.projectName))
            makeDir(os.path.join(self.outfileName,'skins',
                                 self.projectName+'_public'))

            of=makeFile(os.path.join(self.outfileName,'skins',
                                     self.projectName+'_public','readme.txt')
            )
            print >> of, READMEHIGHEST % self.projectName
            of.close()

            of=makeFile(os.path.join(self.outfileName,'skins',
                                     self.projectName,'readme.txt'))
            print >> of, READMELOWEST % self.projectName
            of.close()

            # and now start off with the class files
            generatedModules=self.generatedModules=[]
            self.generatedClasses=[]

            for element in root.getChildren():
                #skip stub and internal classes
                if element.isInternal() or element.getStereoType() in self.stub_stereotypes:
                    continue

                module=element.getName()
                generatedModules.append(module)
                outfilepath=os.path.join(self.outfileName,module+'.py')
                if self.method_preservation:
                    try:
                        #print 'existing sources found for:',element.getName(),outfilepath
                        mod=PyParser.PyModule(outfilepath) 
                        #mod.printit()
                        self.parsed_sources.append(mod)
                        for c in mod.classes.values():
                            #print 'found class:',c.name
                            self.parsed_class_sources[c.name]=c
                        
                    except IOError:
                        #print 'no source found'
                        pass
                    except :
                        print
                        print '***'
                        print '***Error while reparsing the file '+outfilepath
                        print '***'
                        print
                        
                        raise
                    
                outfile=makeFile(outfilepath)
                self.generateModuleInfoHeader(outfile, module, element)
                self.generateHeader(outfile, i18n=self.i18n_support and element.isI18N())
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
        print 'Parsing...'
        print '-------------'
        if not self.noclass:
            if suff.lower() in ('.xmi','.xml'):
                print 'opening xmi'
                self.root=root=XMIParser.parse(self.xschemaFileName,packages=self.packages)
            elif suff.lower() in ('.zargo','.zuml'):
                print 'opening zargo'
                zf=ZipFile(self.xschemaFileName)
                xmis=[n for n in zf.namelist() if os.path.splitext(n)[1].lower()=='.xmi']
                assert(len(xmis)==1)
                buf=zf.read(xmis[0])
                self.root=root=XMIParser.parse(xschema=buf,packages=self.packages)
            elif suff.lower() == '.xsd':
                self.root=root=XSDParser.parse(self.xschemaFileName)
            else:
                raise TypeError,'input file not of type .xsd, .xmi, .xml, .zargo, .zuml'

            #if no output filename given, ry to guess it from the model
            if not self.outfileName:
                self.outfileName=root.getName()

            if not self.outfileName:
                raise TypeError,'output filename not specified'

            print 'outfile:',self.outfileName
        else:
            self.root=root=XMIParser.XMIElement() #create empty element

        print 'Generating...'
        print '-------------'
        if self.method_preservation:
            print 'method bodies will be preserved'
        else:
            print 'method bodies will be overwritten'
            
        self.generate(root)
    
    TEMPLATE_HEADER = """\
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *

    """

    TEMPLATE_HEADER_I18N = """\
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.I18NArchetypes.public import *

    """

def main():

    options={}
    options['version']=version()
    options['author'] = None
    options['email'] = None
    options['copyright'] = None
    options['licence'] = None
    options['no_module_info_header'] = None
    args = sys.argv[1:]
    opts, args = getopt.getopt(args, 'f:a:t:o:s:p:P:n',
                              ['ape','actions','default-actions','no-actions',
                               'ape','ape-support','noclass','unknown-types-as-string',
                               'method-preservation','no-method-preservation',
                               'i18n-support','i18n','no-module-info-header',
                               'author=','e-mail=','copyright=','licence=','creation-permission=',
                               'detailled-creation-permissions','no-detailled-creation-permissions'])
    prefix = ''
    outfileName = None
    yesno={'yes':1,'y': 1, 'no':0, 'n':0}

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

        if option[0] in ('--unknown-types-as-string',):
            options['unknownTypesAsString'] = 1
        elif option[0] == '-a':
            options['generateActions'] = yesno[option[1]]
        elif option[0] == '--actions':
            options['generateActions'] = 1
        elif option[0] == '--default-actions':
            options['generateDefaultActions'] = 1
        elif option[0] == '--no-method-preservation':
            options['method_preservation'] = 0
        elif option[0] == '--method-preservation':
            options['method_preservation'] = 1
        elif option[0] == '--no-actions':
            options['generateActions'] = 0

        if option[0] == '-n':
            options['noclass'] = 1
        if option[0] == '--noclass':
            options['noclass'] = 1
        if option[0] in ('--ape','--ape-support'):
            options['ape_support'] = 1
        if option[0] in ('--i18n-support','--i18n'):
            options['i18n_support'] = 1

        if option[0] == '--no-module-info-header':
            options['no_module_info_header'] = 1            
        elif option[0] == '--author':
            options['author'] = option[1]
        elif option[0] == '--e-mail':
            options['email'] = option[1]
        elif option[0] == '--copyright':
            options['copyright'] = option[1]
        elif option[0] == '--licence':
            options['licence'] = option[1]
        elif option[0] == '--creation-permission':
            options['creation_permission'] = option[1]
        elif option[0] == '--detailled-creation-permissions':
            options['detailled_creation_permissions'] = 1
        elif option[0] == '--no-detailled-creation-permissions':
            options['detailled_creation_permissions'] = 0
        

    if len(args) < 1 and not options.get('noclass',0):
        usage()
        
    if len(args):
        xschemaFileName = args[0]
    else:
        xschemaFileName = ''

    if not outfileName: # if outfilename is not given by the -o oprion try
                        # getting the second regular argument
        if len(args) > 1:
            outfileName=args[1]

    if not outfileName:
        usage()

    gen=ArchetypesGenerator(xschemaFileName,outfileName, **options)
    gen.parseAndGenerate()

ARCHGENXML_VERSION_LINE = """\
ArchGenXML %(version)s 
(c) 2003 BlueDynamics GmbH, under GNU General Public License 2.0 or later
"""

USAGE_TEXT = """\
Usage: python ArchGenXML.py -o <target> [ options ] <xmi-source-file>

OPTIONS:
    -o <target>
        Output file directory path for data  representation classes. Last part 
        is used for internal directory namings.
        
    -P <name1>,<name2>...
        names of packages to parse in source file 
        
    -a --actions
        generates actions (default)

    --no-actions
        do not generates actions

    --method-preservation
        methods in the target sources will be preserved (default)

    --no-method-preservation 
        methods in the target sources will be preserved

    -t --unknown-types-as-string 
        unknown attribute types will be treated as text

    --ape-support
        generate apeconf.xml and generators for ape (needs Archetypes 1.1+)

    --i18n-support
        support for i18NArchetypes. Attributes with a stereotype 'i18n' or a 
        taggedValue 'i18n' set to '1' are multilingual.

    --creation-permission=<perm> 
        specifies which permission to create content default:Add [project] 
        content

    --detailled-creation-permissions  
        seperate creation permissions per class

    --no-module-info-header      
        do not generate module info header

    --author=<string>            
        set default author string for module info headers, taggedValue will 
        override this

    --e-mail=<string>
        set default e-mail adress string for module info headers, taggedValue 
        will override this

    --copyright=<string>
        set default copyright string for module info headers, taggedValue will 
        override this

    --licence=<string>
        set default licence string for module info-headers, taggedValue will 
        override this

"""

def usage():
    print USAGE_TEXT
    sys.exit(-1)
    
def version():
    ver=open(os.path.join(sys.path[0],'version.txt')).read().strip()
    print ARCHGENXML_VERSION_LINE % {'version': ver}
    return ver

if __name__ == '__main__':
    main()
    #import pdb
    #pdb.run('main()')
