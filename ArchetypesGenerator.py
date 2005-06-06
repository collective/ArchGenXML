#-----------------------------------------------------------------------------
# Name:        ArchetypesGenerator.py
# Purpose:     main class generating archetypes code out of an UML-model
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# RCS-ID:      $Id$
# Copyright:   (c) 2003-2005 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

import getopt, os.path, time, sys

from zipfile import ZipFile
from StringIO import StringIO
from shutil import copy
from types import StringTypes

from xml.dom import minidom

# AGX-specific imports
import XSDParser, XMIParser, PyParser
from UMLProfile import UMLProfile

from documenttemplate.documenttemplate import HTML

from codesnippets import *
import utils
from odict import odict
from utils import makeFile, readFile, makeDir,mapName, wrap, indent, getExpression, \
    isTGVTrue, isTGVFalse, readTemplate, getFileHeaderInfo

from BaseGenerator import BaseGenerator
from WorkflowGenerator import WorkflowGenerator

_marker=[]

try:
    from i18ndude import catalog as msgcatalog
except ImportError:
    has_i18ndude = False
else:
    has_i18ndude = True

try:
    "abca".strip('a')
except:
    has_enhanced_strip_support = False
else:
    has_enhanced_strip_support = True


#
# Global variables etc.
#
Elements = []
AlreadyGenerated = []
Force = 0


class DummyModel:
    def __init__(self,name=''):
        self.name=name
    def getName(self):
        return self.name
    getFilePath=getName
    getModuleFilePath=getName
    getProductModuleName=getName
    getProductName=getName
    def hasStereoType(self,s):
        return 0

    def getClasses(self,*a,**kw):
        return []
    getInterfaces=getClasses
    getPackages=getClasses
    getStateMachines=getClasses
    def isRoot(self):
        return 1
    
    def getAnnotation(self,*a,**kw):
        return None
    
    def getDocumentation(self,**kw):
        return None
    def hasTaggedValue(*a,**kw):
        return None
    def getParent(*a,**kw):
        return None

class ArchetypesGenerator(BaseGenerator):
    generator_generator='archetypes'
    default_class_type='content_class'

    uml_profile=UMLProfile(BaseGenerator.uml_profile)


    uml_profile.addStereoType('portal_tool',['XMIClass'],
        description='turns a class into a portal tool')
    uml_profile.addStereoType('stub',['XMIClass'],
        description='This class wont get generated')
    uml_profile.addStereoType('content_class',['XMIClass'],
        description='turns a class into a portal tool',dispatching=1,
        generator='generateArchetypesClass')

    uml_profile.addStereoType('tests',['XMIPackage'],
        description='this package will be treated as test package')
    uml_profile.addStereoType('plone_testcase',['XMIClass'],dispatching=1,
        generator='generateBaseTestcaseClass',template='tests/PloneTestcase.py')
    uml_profile.addStereoType('testcase',['XMIClass'],dispatching=1,
        generator='generateTestcaseClass',template='tests/GenericTestcase.py')
    uml_profile.addStereoType('setup_testcase',['XMIClass'],dispatching=1,
        generator='generateTestcaseClass',template='tests/SetupTestcase.py')
    uml_profile.addStereoType('interface_testcase',['XMIClass'],dispatching=1,
        generator='generateTestcaseClass',template='tests/InterfaceTestcase.py')
    uml_profile.addStereoType('relation_implementation',['XMIClass','XMIAssociation','XMIPackage'],
        description='specifies how relations should be implemented',default='basic')

    uml_profile.addStereoType('field',['XMIClass'],dispatching=1,
        generator='generateFieldClass',template='field.py')
    uml_profile.addStereoType('widget',['XMIClass'],dispatching=1,
        generator='generateWidgetClass',template='widget.py')
    uml_profile.addStereoType('value_class',['XMIDependency'],
        description='declares a class to be used as value class for a certain field class (see <<field>> stereotype)')

    infoind = 0
    force=1
    unknownTypesAsString=0
    generateActions=1
    generateDefaultActions=0
    prefix=''
    prefix=''
    parse_packages=[] #packages to scan for classes
    generate_packages=[] #packages to be generated
    noclass=0   # if set no module is reverse engineered,
                #just an empty project + skin is created
    ape_support=0 #generate ape config and serializers/gateways for APE
    method_preservation=1 #should the method bodies be preserved? defaults now to 0 will change to 1
    i18n_content_support=0
    i18n_at=['i18n-archetypes','i18n', 'i18n-at']
    generate_datatypes=['field','compound_field']


    build_msgcatalog=1
    striphtml=0

    reservedAtts=['id',]
    portal_tools=['portal_tool','tool']
    variable_schema='variable_schema'
    stub_stereotypes=['odStub','stub']
    archetype_stereotype = ['archetype']
    vocabulary_item_stereotype = ['vocabulary_term']
    vocabulary_container_stereotype = ['vocabulary']
    cmfmember_stereotype = ['CMFMember', 'member']
    python_stereotype = ['python', 'python_class']

    left_slots=[]
    right_slots=[]
    force_plugin_root=1 #should be 'Products.' be prepended to all absolute paths?
    customization_policy=0
    backreferences_support=0

    parsed_class_sources={} #dict containing the parsed sources by class names (for preserving method codes)
    parsed_sources=[] #list containing the parsed sources (for preserving method codes)

    #taggedValues that are not strings, e.g. widget or vocabulary
    nonstring_tgvs=['widget','vocabulary','required','precision','storage',
                    'enforceVocabulary', 'multiValued', 'visible']

    msgcatstack = []

    # ATVM integration

    # a vocabularymap collects all used vocabularies
    # format { productsname: (name, meta_type) }
    # if metatype is None, it defaults to SimpleVocabulary
    vocabularymap = {}

    # End ATVM integrationer

    # if a reference has the same name as another _and_
    # its source object is the same, we want only one ReferenceWidget _unless_
    # we have a tagged value 'single' on the reference
    reference_groups = list()

    # for each class an own permission can be defined, how should be able to add
    # it. It default to "Add Portal Content" and
    creation_permissions = []

    # the stack is needed to remind permissions while a subproduct is generated
    creation_permission_stack = []

    def __init__(self,xschemaFileName, **kwargs):
        self.outfileName=kwargs['outfilename']

        if self.outfileName[-1] in ('/','\\'):
            self.outfileName=self.outfileName[:-1]

        path=os.path.split(self.outfileName)
        self.targetRoot=path[0]
        #print 'targetRoot:',self.targetRoot
        #os.chdir(self.targetRoot or '.')

        self.xschemaFileName=xschemaFileName
        self.__dict__.update(kwargs)


    def makeFile(self,fn,force=1):
        ffn=os.path.join(self.targetRoot,fn)
        return makeFile(ffn,force=force)

    def readFile(self,fn):
        ffn=os.path.join(self.targetRoot,fn)
        return readFile(ffn)

    def makeDir(self,fn,force=1):
        ffn=os.path.join(self.targetRoot,fn)
        return makeDir(ffn,force=force)

    def getSkinPath(self,element):
        return os.path.join(element.getRootPackage().getFilePath(),'skins',element.getRootPackage().getModuleName())

    def generateDependentImports(self,element):
        res=BaseGenerator.generateDependentImports(self,element)
        
        generate_expression_validator=False
        for att in element.getAttributeDefs():
            if att.getTaggedValue('validation_expression'):
                generate_expression_validator=True
        
        if generate_expression_validator:
            out=StringIO()
            print >>out,res
            print >>out,'from Products.validation.validators import ExpressionValidator'
            res=out.getvalue()
                
        return res

    def addMsgid(self,msgid,msgstr,element,fieldname):
        """add a msgid to the catalog if it not exists. if it exists and not
           listed in occurrences, then add its occurence."""
        if has_i18ndude and self.build_msgcatalog and len(self.msgcatstack):
            msgcat=self.msgcatstack[len(self.msgcatstack)-1]
            package=element.getPackage()
            module_id=os.path.join(element.getPackage().getFilePath(includeRoot=0),element.getName()+'.py')
            if not msgcat.has_key(msgid):
                # add new msgid
                msgcat[msgid] = (msgstr, [(module_id, [msgstr])], [])
            else:
                # check if occurrence is listed
                entry=msgcat[msgid]
                for entry_id, entry_ex in entry[1]:
                    if entry_id == module_id:
                        return
                # isnt listed, so add it
                entry[1].append((module_id, [msgstr]))

    def generateMethodActions(self,element):
        outfile=StringIO()
        print >> outfile
        for m in element.getMethodDefs():
            code=indent(m.getTaggedValue('code',''),1)
            if m.hasStereoType( ['action','view','form']):
                action_name=m.getTaggedValue('action','').strip()
                if not action_name:
                    action_name=m.getTaggedValue(m.getStereoType(), m.getName()).strip()
                #print 'generating ' + m.getStereoType()+':',action_name
                dict={}

                if not action_name.startswith('string:') and not action_name.startswith('python:'):
                    action_target='string:$object_url/'+action_name
                else:
                    action_target=action_name

                dict['action']=getExpression(action_target)
                dict['action_category']=getExpression(m.getTaggedValue('category','object'))
                dict['action_id']=m.getTaggedValue('id',m.getName())
                dict['action_label'] = m.getTaggedValue('action_label') or \
                                       m.getTaggedValue('label',m.getName())
                # action_label is deprecated and for backward compability only!
                dict['permission']=getExpression(m.getTaggedValue('permission','View'))

                condition=m.getTaggedValue('condition') or '1'
                dict['condition']='python:'+condition

                if not (m.hasTaggedValue('create_action') and isTGVFalse(m.getTaggedValue('create_action'))):
                    print >>outfile, ACT_TEMPL % dict

            if m.hasStereoType('view'):
                f=self.makeFile(os.path.join(self.getSkinPath(element),action_name+'.pt'),0)
                if f:
                    templdir=os.path.join(sys.path[0],'templates')
                    viewTemplate=open(os.path.join(templdir,'action_view.pt')).read()
                    f.write(viewTemplate % code)

            elif m.hasStereoType('form'):
                f=self.makeFile(os.path.join(self.getSkinPath(element),action_name+'.cpt'),0)
                if f:
                    templdir=os.path.join(sys.path[0],'templates')
                    viewTemplate=open(os.path.join(templdir,'action_view.pt')).read()
                    f.write(viewTemplate % code)

            elif m.hasStereoType(['portlet_view','portlet']):
                view_name=m.getTaggedValue('view').strip() or m.getName()
                autoinstall=m.getTaggedValue('autoinstall')
                portlet='here/%s/macros/portlet' % view_name
                if autoinstall=='left':
                    self.left_slots.append(portlet)
                if autoinstall=='right':
                    self.right_slots.append(portlet)

                f=self.makeFile(os.path.join(self.getSkinPath(element),view_name+'.pt'),0)
                if f:
                    templdir=os.path.join(sys.path[0],'templates')
                    viewTemplate=open(os.path.join(templdir,'portlet_template.pt')).read()
                    f.write(viewTemplate % {'method_name':m.getName()})

        res=outfile.getvalue()
        return res


    def generateAdditionalImports(self, element):
        outfile=StringIO()

        if element.hasAssocClass:
            print >> outfile,'from Products.Archetypes.ReferenceEngine import ContentReferenceCreator'
            
        useRelations=0
        
        #check wether we have to import Relation's Relation Field
        for rel in element.getFromAssociations():
            if self.getOption('relation_implementation',rel,'basic') == 'relations':
                useRelations=1

        for rel in element.getToAssociations():
            if self.getOption('relation_implementation',rel,'basic') == 'relations' and \
                (rel.getTaggedValue('inverse_relation_name') or rel.fromEnd.isNavigable) :
                useRelations=1

        if useRelations:
            print >> outfile,'from Products.Relations.field import RelationField'
                
        if element.hasStereoType(self.variable_schema):
            print >> outfile,'from Products.Archetypes.VariableSchemaSupport import VariableSchemaSupport'

        # ATVocabularyManager imports
        if element.hasStereoType(self.vocabulary_item_stereotype):
            print >> outfile, 'from Products.ATVocabularyManager.tools import registerVocabularyTerm'
        if element.hasStereoType(self.vocabulary_container_stereotype):
            print >> outfile, 'from Products.ATVocabularyManager.tools import registerVocabulary'
        if element.hasAttributeWithTaggedValue('vocabulary:type','ATVocabularyManager'):
            print >> outfile, 'from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary'

        print >> outfile, ''
        return outfile.getvalue()
        


    def generateModifyFti(self,element):
        hide_actions=element.getTaggedValue('hide_actions', '').strip()
        if not hide_actions:
            return ''

        # Also permit comma separation, since Poseidon doesn't like multi-line
        # tagged values and specifying multiple tagged values is a pain
        hide_actions = hide_actions.replace(',', '\n')

        hide_actions=', '.join(["'"+a.strip()+"'" for a in hide_actions.split('\n')])
        return MODIFY_FTI % {'hideactions':hide_actions, }


    def generateFti(self, element, subtypes):
        ''' generates Factory Type Information related attributes on the class'''

        hasActions=False
        actTempl=ACTIONS_START
        base_actions=element.getTaggedValue('base_actions', '').strip()
        if base_actions:
            hasActions=True
            base_actions += ' + '
            actTempl = actTempl % base_actions
        else:
            actTempl = actTempl % ''

        if self.generateDefaultActions or element.getTaggedValue('default_actions'):
            hasActions=True
            actTempl += DEFAULT_ACTIONS
            if subtypes:
                actTempl=actTempl+DEFAULT_ACTIONS_FOLDERISH

        method_actions=self.generateMethodActions(element)
        if method_actions.strip():
            hasActions=True
            actTempl +=method_actions
        actTempl+=ACTIONS_END

        ftiTempl=FTI_TEMPL
        if self.generateActions and hasActions:
            ftiTempl += actTempl

        immediate_view = element.getTaggedValue('immediate_view') or 'base_view'
        default_view = element.getTaggedValue('default_view') or immediate_view

        # global_allow
        ga = not isTGVFalse(self.getOption('global_allow', element, None))
        if ga:
            # In principle, allow globally
            global_allow = 1
            # Unless it is only contained by another element
            if element.isDependent():
                # WARNING! isDependent() doesn't seem to work,
                # aggregates and compositions aren't detected.
                # 2005-05-11 reinout
                global_allow = 0
            # Or if it is a hidden element
            if element.hasStereoType('hidden'):
                global_allow = 0
            # Or if it is a tool-like thingy
            if (element.hasStereoType(self.portal_tools) or 
                element.hasStereoType(self.vocabulary_item_stereotype) or
                element.hasStereoType(self.cmfmember_stereotype) or 
                element.isAbstract()):
                global_allow = 0
        else:
            global_allow=0

        has_content_icon=''
        content_icon=element.getTaggedValue('content_icon')
        if not content_icon:
            has_content_icon='#'
            content_icon = element.getCleanName()+'.gif'

        # If we are generating a tool, include the template which sets
        # a tool icon
        if element.hasStereoType(self.portal_tools):
            ftiTempl += TOOL_FTI_TEMPL

        has_toolicon=''
        toolicon = element.getTaggedValue('toolicon')
        if not toolicon:
            has_toolicon='#'
            toolicon = element.getCleanName()+'.gif'

        # Allow discussion?
        allow_discussion = element.getTaggedValue('allow_discussion','0')

        # Filter content types?
        # Filter by default if it's a folder-like thingy
        filter_default = self.elementIsFolderish(element)
        # But a tagged value overrides
        filter_content_types = isTGVTrue(element.getTaggedValue('filter_content_types',
                                                                filter_default))
        # Set a type description.

        typeName = element.getTaggedValue('archetype_name') or \
                    element.getTaggedValue('label') or \
                    element.getName ()

        typeDescription = getExpression(element.getTaggedValue('typeDescription', typeName))

        res=ftiTempl % {
            'subtypes'             : repr(tuple(subtypes)),
            'has_content_icon'     : has_content_icon,
            'content_icon'         : content_icon,
            'has_toolicon'         : has_toolicon,
            'toolicon'             : toolicon,
            'allow_discussion'     : allow_discussion,
            'global_allow'         : global_allow,
            'immediate_view'       : immediate_view,
            'default_view'         : default_view,
            'filter_content_types' : filter_content_types,
            'typeDescription'      : typeDescription,
            'type_name_lc'         : element.getName ().lower ()}

        return res

    # TypeMap for Fields, format is
    #   type: {field: 'Y',
    #          lines: [key1=value1,key2=value2, ...]
    #   ...
    #   }
    typeMap= {
        'string': {
            'field': 'StringField',
            'map': {},
        },
        'text':  {
            'field': 'TextField',
            'map': {},
        },
        'richtext':  {
            'field': 'TextField',
            'map': {
                'default_output_type':"'text/html'",
                'allowable_content_types': "('text/plain','text/structured','text/html','application/msword',)",
            },
        },
        'selection': {
            'field': 'StringField',
            'map': {},
        },
        'multiselection': {
            'field': 'LinesField',
            'map': {'multiValued': '1'},
        },
        'integer': {
            'field': 'IntegerField',
            'map': {},
        },
        'float': {
            'field': 'FloatField',
            'map': {},
        },
        'fixedpoint': {
            'field': 'FixedPointField',
            'map': {},
        },
        'lines': {
            'field': 'LinesField',
            'map': {},
        },
        'date': {
            'field': 'DateTimeField',
            'map': {},
        },
        'image': {
            'field': 'ImageField',
            'map': {
                'storage':'AttributeStorage()',
            },
        },
        'file': {
            'field': 'FileField',
            'map': {
                'storage':'AttributeStorage()',
            },
        },
        'reference': {
            'field': 'ReferenceField',
            'map': {},
        },
        'relation': {
            'field': 'RelationField',
            'map': {},
        },
        'backreference': {
            'field': 'BackReferenceField',
            'map': {},
        },
        'boolean': {
            'field': 'BooleanField',
            'map': {},
        },
        'computed': {
            'field': 'ComputedField',
            'map': {},
        },
        'photo': {
            'field': 'PhotoField',
            'map': {},
        },
        'generic': {
            'field': '%(type)sField',
            'map': {},
        },
    }

    widgetMap={
        'fixedpoint': 'DecimalWidget' ,
        'float': 'DecimalWidget' ,
        'text': 'TextAreaWidget' ,
        'richtext': 'RichWidget' ,
        'file': 'FileWidget',
        'date' : 'CalendarWidget',
        'selection' : 'SelectionWidget',
        'multiselection' : 'MultiSelectionWidget',
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
        'String':'string',
        '':'string',     #
        None:'string',
    }

    hide_classes=['EARootClass','int','float','boolean','long','bool','void','string',
        'dict','tuple','list','object','integer',
        'integer','java::lang::int','java::lang::string','java::lang::long',
        'java::lang::float','java::lang::void']+\
        list(typeMap.keys())+list(coerceMap.keys()) # Enterprise Architect and other automagically created crap Dummy Class

    def coerceType(self, intypename):
        #print 'coerceType: ',intypename,' -> ',
        typename=intypename.lower()
        if typename in self.typeMap.keys():
            return typename
        
        if typename=='copy':
            return typename

        if self.unknownTypesAsString:
            ctype=self.coerceMap.get(typename.lower(),'string')
        else:
            ctype=self.coerceMap.get(typename.lower(),None)
            if ctype is None:
                return 'generic' #raise ValueError,'Warning: unknown datatype : >%s< (use the option --unknown-types-as-string to force unknown types to be converted to string' % typename

        #print ctype,'\n'
        return ctype

    def getFieldAttributes(self,element):
        """ converts the tagged values of a field into extended attributes for the archetypes field """
        noparams=['documentation','element.uuid','transient','volatile',
                  'widget','copy_from',]
        convtostring=['expression']
        map={}
        tgv=element.getTaggedValues()

        for kt in [('storage',),('callStorageOnSet',),('call_storage_on_set','callStorageOnSet')]:
            if len(kt)>1:
                skey=kt[0]
                key=kt[1]
            else:
                skey=kt[0]
                key=kt[0]

            if skey not in tgv.keys():
                v=self.getOption(skey,element,None)
                if v:
                    tgv.update({key:v})


        # set permissions, if theres one arround in the model
        perm=self.getOption('read_permission',element,default=None)
        if perm:
            tgv.update({'read_permission':perm})
        perm=self.getOption('write_permission',element,default=None)
        if perm:
            tgv.update({'write_permission':perm})

        # set attributes from tgv
        for k in tgv.keys():
            if k not in noparams and not k.startswith('widget:'):
                v=tgv[k]
                if v is None:
                    print '!: Warning: Empty tagged value for "%s" in field "%s"' %(k,element.getName())
                    continue

                if k not in self.nonstring_tgvs:
                    v=getExpression(v)
                # [optilude] Permit python: if people forget they don't have to (I often do!)
                else:
                    if v.startswith ('python:'):
                        v = v[7:]

                formatted=''
                for line in v.split('\n'):
                    formatted+=line
                map.update( {k:formatted.strip()} )
        return map

    def getWidget(self, type, element, fieldname, elementclass):
        """ returns either default widget, widget according to
        attributes or no widget.

        atributes/tgv's can be:
            * widget and a whole widget code block or
            * widget:PARAMETER which will be rendered as a PARAMETER=value

        """
        tgv=element.getTaggedValues()
        widgetcode = type.capitalize()+'Widget'
        widgetmap=odict()
        custom = False # is there a custom setting for widget?
        widgetoptions=[t for t in tgv.items() if t[0].startswith('widget:')]

        # check if a global default overrides a widget. setting defaults is
        # provided through getOption.
        # to set an default just put:
        # default:widget:type = widgetname
        # as a tagged value on the package or model
        if hasattr(element,'type') and element.type!='NoneType':
            atype = element.type
        else:
            atype=type
        default_widget = self.getOption('default:widget:%s' % atype, element, None)
        if default_widget:
            widgetcode = default_widget+'(\n'

        modulename= elementclass.getPackage().getProductName()
        check_map=odict()
        check_map['label']              = "'%s'" % fieldname.capitalize()
        check_map['label_msgid']        = "'%s_label_%s'" % (modulename,fieldname)
        check_map['description']        = "'Enter a value for %s.'" % fieldname
        check_map['description_msgid']  = "'%s_help_%s'" % (modulename,fieldname)
        check_map['i18n_domain']        = "'%s'" % modulename

        wt={} # helper
        if tgv.has_key('widget'):
            # Custom widget defined in attributes
            custom = True
            formatted=''
            for line in tgv['widget'].split('\n'):
                if formatted:
                    line=indent(line.strip(),1)
                formatted+=line+'\n'
            widgetcode =  formatted

        elif [wt.update({t[0]:t[1]}) for t in widgetoptions if t[0] == u'widget:type']:
            custom = True
            widgetcode = wt['widget:type']

        elif self.widgetMap.has_key(type) and not default_widget:
            # default widget for this type found in widgetMap
            custom = True
            widgetcode = self.widgetMap[type]

        if ')' not in widgetcode: # XXX bad check *sigh*

            for tup in widgetoptions:
                key=tup[0][7:]
                val=tup[1]
                if key == 'type':
                    continue
                if key not in self.nonstring_tgvs:
                    val=getExpression(val)
                # [optilude] Permit python: if people forget they don't have to (I often do!)
                else:
                    if val.startswith ('python:'):
                        val = val[7:]

                widgetmap.update({key:val})

            if '(' not in widgetcode:
                widgetcode += '(\n'

            ## before update the widget mapping, try to make a
            ## better description based on the given label
            if widgetmap.has_key('label'):
                check_map['description'] = "\'Enter a value for %s.\'" % widgetmap['label'][3:-3].lower()

            for k in check_map:
                if not (k in widgetmap.keys()): # XXX check if disabled
                    widgetmap.update( {k: check_map[k]} )
            if 'label_msgid' in widgetmap.keys() and has_enhanced_strip_support:
                self.addMsgid(widgetmap['label_msgid'].strip("'").strip('"'),
                    (widgetmap.has_key('label') and widgetmap['label'].strip("'").strip('"')) or fieldname,
                    elementclass,
                    fieldname
                )
            if 'description_msgid' in widgetmap.keys() and has_enhanced_strip_support:
                self.addMsgid(widgetmap['description_msgid'].strip("'"),
                    (widgetmap.has_key('description') and widgetmap['description'].strip("'")) or fieldname,
                    elementclass,
                    fieldname
                )

            widgetcode += indent( \
                ',\n'.join(['%s=%s' % (key,widgetmap[key]) for key in widgetmap]),
                1,
                skipFirstRow=0) \
                + ',\n'
            widgetcode +=')'

        return widgetcode

    def getFieldFormatted(self,name,fieldtype,map={},doc=None, rawType='String', indent_level=0):
        ''' returns the formatted field definitions for the schema '''
        res = ''

        # capitalize only first letter of fields class name, keep camelcase
        a=rawType[0].upper()
        rawType=a+rawType[1:]

        # add comment
        if doc:
            res+=indent(doc,indent_level,'#')+'\n'+res

        # If this is a generic field and the user entered MySpecialField,
        # then don't suffix it with 'field''
        if rawType.endswith('Field'):
            rawType = rawType[:-5]

        res+=indent("%s('%s',\n" % (fieldtype % {'type':rawType},name), indent_level)
        if map:
            res+=indent(',\n'.join(['%s=%s' % (key,map[key]) \
                                for key in map if key.find(':')<0 ]) ,
                    indent_level+1) + ',\n'
        res+=indent('),\n',indent_level)

        return res

    def getFieldString(self, element, classelement):
        ''' gets the schema field code '''
        typename=str(element.type)

        if element.getMaxOccurs()>1:
            ctype='lines'
        else:
            ctype=self.coerceType(typename)

        map = typeMap[ctype]['map'].copy()

        res=self.getFieldFormatted(element.getCleanName(),
            self.typeMap[ctype]['field'].copy(),
            map )

        return res

    def getFieldStringFromAttribute(self, attr, classelement):
        ''' gets the schema field code '''
        #print 'typename:%s:'%attr.getName(),attr.type,
        
        if not hasattr(attr,'type') or attr.type=='NoneType':
            ctype='string'
        else:
            ctype=self.coerceType(str(attr.type))

        if ctype=='copy':
            name = getattr(attr,'rename_to',attr.getName())
            field="copied_fields['%s'],\n" % name
            return field
            

        map=self.typeMap[ctype]['map'].copy()
        if attr.hasDefault():
            map.update( {'default':getExpression(attr.getDefault())} )
        map.update(self.getFieldAttributes(attr))
        widget=self.getWidget( \
                ctype,
                attr,
                attr.getName(),
                classelement )

        if not widget.startswith ('GenericWidget'):
            map.update( {
                'widget': widget })


        # ATVocabularyManager: Add NamedVocabulary to field.
        vocaboptions = {}
        for t in attr.getTaggedValues().items():
            if t[0].startswith('vocabulary:'):
                vocaboptions[t[0][11:]]=t[1]
        if vocaboptions:
            if not 'name' in vocaboptions.keys():
                vocaboptions['name'] = '%s_%s' % (classelement.getCleanName(), \
                                                  attr.getName())
            if not 'term_type' in vocaboptions.keys():
                vocaboptions['term_type'] = 'SimpleVocabularyItem'

            if not 'vocabulary_type' in vocaboptions.keys():
                vocaboptions['vocabulary_type'] = 'SimpleVocabulary'

            map.update( {
                'vocabulary':'NamedVocabulary("""%s""")' % vocaboptions['name']
            } )

            # remember this vocab-name and if set its meta_type
            package = classelement.getPackage()
            currentproduct = package.getProductName()
            if not currentproduct in self.vocabularymap.keys():
                self.vocabularymap[currentproduct] = {}

            if not vocaboptions['name'] in self.vocabularymap[currentproduct]:
                self.vocabularymap[currentproduct] = (vocaboptions['name'],
                                                      vocaboptions['vocabulary_type'],
                                                      vocaboptions['term_type'])

        # end ATVM

        atype=self.typeMap[ctype]['field']

        if ctype != 'generic' and self.i18n_content_support in self.i18n_at and attr.isI18N():
            atype='I18N'+atype

        doc=attr.getDocumentation(striphtml=self.striphtml)
        if map.has_key('validation_expression'):
            expression=map['validation_expression']
            #import pdb;pdb.set_trace()
            map['validators']="(ExpressionValidator('python:%s'),)" % expression[1:-1]
            del map['validation_expression']
            
        res=self.getFieldFormatted(attr.getName(),
            atype,
            map,
            doc,
            rawType=attr.getType()
            )

        return res

    def getFieldStringFromAssociation(self, rel, classelement):
        ''' gets the schema field code '''
        multiValued=0
        obj=rel.toEnd.obj
        name=rel.toEnd.getName()
        relname=rel.getName()
        #field=rel.getTaggedValue('reference_field') or self.typeMap['reference']['field'] #the relation can override the field

        if obj.isAbstract():
            allowed_types= tuple(obj.getGenChildrenNames())
        else:
            allowed_types=(obj.getName(), ) + tuple(obj.getGenChildrenNames())

        if int(rel.toEnd.mult[1]) == -1:
            multiValued=1
        if name == None:
            name=obj.getName()+'_ref'

        if self.getOption('relation_implementation',rel,'basic') == 'relations':
            field=rel.getTaggedValue('reference_field') or \
                  rel.toEnd.getTaggedValue('reference_field') or \
                  self.typeMap['relation']['field'] #the relation can override the field

            map=self.typeMap['relation']['map'].copy()
            map.update({
                'multiValued':   multiValued,
                'relationship':  "'%s'" % relname,
                }
            )
            map.update(self.getFieldAttributes(rel.toEnd))
            map.update( {'widget':self.getWidget('Reference', rel.toEnd, name, classelement)} )
        else:
            field=rel.getTaggedValue('reference_field') or \
                  rel.toEnd.getTaggedValue('reference_field') or \
                  self.typeMap['reference']['field'] #the relation can override the field
            map=self.typeMap['reference']['map'].copy()
            map.update({
                'allowed_types': repr(allowed_types),
                'multiValued':   multiValued,
                'relationship':  "'%s'" % relname,
                }
            )
            map.update(self.getFieldAttributes(rel.toEnd))
    
            map.update( {'widget':self.getWidget('Reference', rel.toEnd, name, classelement)} )
    
            if getattr(rel,'isAssociationClass',0):
                #associationclasses with stereotype "stub" and tagged value "import_from" will not use ContentReferenceCreator
    
                if rel.hasStereoType(self.stub_stereotypes) :
                    map.update({'referenceClass':"%s" % rel.getName()})
                    # do not forget the import!!!
    
                else:
                    map.update({'referenceClass':"ContentReferenceCreator('%s')" % rel.getName()})


        doc=rel.getDocumentation(striphtml=self.striphtml)
        res=self.getFieldFormatted(name,field,map,doc)
        return res

    def getFieldStringFromBackAssociation(self, rel, classelement):
        ''' gets the schema field code '''
        multiValued=0
        obj=rel.fromEnd.obj
        name=rel.fromEnd.getName()
        relname=rel.getName()

        if obj.isAbstract():
            allowed_types= tuple(obj.getGenChildrenNames())
        else:
            allowed_types=(obj.getName(), ) + tuple(obj.getGenChildrenNames())

        if int(rel.fromEnd.mult[1]) == -1:
            multiValued=1
        if name == None:
            name=obj.getName()+'_ref'

        if self.getOption('relation_implementation',rel,'basic') == 'relations'\
              and (rel.fromEnd.isNavigable or rel.getTaggedValue('inverse_reference_name')):
            field=rel.getTaggedValue('relation_field') or self.typeMap['relation']['field'] #the relation can override the field
            map=self.typeMap['relation']['map'].copy()
            backrelname=rel.getTaggedValue('inverse_relation_name') or relname+'_inverse'

            map.update({
                'multiValued':   multiValued,
                'relationship':  "'%s'" % backrelname,
                }
            )
            map.update(self.getFieldAttributes(rel.fromEnd))
            map.update( {'widget':self.getWidget('Reference', rel.fromEnd, name, classelement)} )
        else:
            field=rel.getTaggedValue('reference_field') or rel.toEnd.getTaggedValue('back_reference_field') or self.typeMap['backreference']['field'] #the relation can override the field
            map=self.typeMap['backreference']['map'].copy()
            if rel.fromEnd.isNavigable and (self.backreferences_support or self.getOption('backreferences_support',rel,'0')=='1'):
                map.update({
                    'allowed_types': repr(allowed_types),
                    'multiValued':   multiValued,
                    'relationship':  "'%s'" % relname,
                    }
                )
                map.update(self.getFieldAttributes(rel.fromEnd))
                map.update( {'widget':self.getWidget('BackReference', rel.fromEnd, name, classelement)} )
        
                if getattr(rel,'isAssociationClass',0):
                    map.update({'referenceClass':"ContentReferenceCreator('%s')" % rel.getName()})
            else:
                return None

        doc=rel.getDocumentation(striphtml=self.striphtml)
        res=self.getFieldFormatted(name,field,map,doc)
        return res

    # Generate get/set/add member functions.
    def generateArcheSchema(self, element, base_schema):
        """ generates the Schema """
        # first copy fields from other schemas if neccessary.
        outfile=StringIO()
        startmarker=True
        for attr in element.getAttributeDefs():
            if str(attr.type)=='copy':
                if startmarker:
                    startmarker=False
                    print >>outfile, 'copied_fields = {}'
                copyfrom = getattr(attr,'copy_from','BaseSchema')
                name = getattr(attr,'rename_to',attr.getName())
                print >>outfile, "copied_fields['%s'] = %s['%s'].copy()" % (name, copyfrom, attr.getName())
                map = self.getFieldAttributes(attr)
                for key in map:
                    print >>outfile, "copied_fields['%s'].%s = %s" % (name, 
                                        key, map[key])
                tgv=attr.getTaggedValues()
                for key in tgv.keys():
                    if not key.startswith('widget:'):
                        continue
                    if key not in self.nonstring_tgvs:
                        tgv[key]=getExpression(tgv[key])                    
                    print >>outfile, "copied_fields['%s'].widget.%s = %s" % (name, 
                                        key[7:], tgv[key])
                           

        print >>outfile, SCHEMA_START
        aggregatedClasses=[]

        for attrDef in element.getAttributeDefs():
            name = attrDef.getName()
            #if name in self.reservedAtts:
            #    continue
            mappedName = mapName(name)

            #print attrDef

            print >> outfile, indent(self.getFieldStringFromAttribute(attrDef, element),1)

        for child in element.getChildren():
            name = child.getCleanName()
            if name in self.reservedAtts:
                continue
            unmappedName = child.getUnmappedCleanName()
            if child.getRef():
                aggregatedClasses.append(str(child.getRef()))

            if child.isIntrinsicType():
                print >> outfile, indent(self.getFieldString(child, element),1)

        #print 'rels:',element.getName(),element.getFromAssociations()
        # and now the associations
        for rel in element.getFromAssociations():
            name = rel.fromEnd.getName()
            end=rel.fromEnd

            #print 'generating from assoc'
            if name in self.reservedAtts:
                continue
            print >> outfile
            print >> outfile, indent(self.getFieldStringFromAssociation(rel, element),1)

                
        #Back References
        for rel in element.getToAssociations():
            name = rel.fromEnd.getName()

            #print "backreference"
            if name in self.reservedAtts:
                continue

            fc=self.getFieldStringFromBackAssociation(rel, element)
            if fc:
                print >> outfile
                print >> outfile, indent(fc,1)


        print >> outfile,'),'
        marshaller=element.getTaggedValue('marshaller') or element.getTaggedValue('marshall')
        if marshaller:
            print >> outfile, 'marshall='+marshaller

        print >> outfile,')\n'
        
        return outfile.getvalue()

    def generateMethods(self, outfile, element, mode='class'):
        print >> outfile
        print >> outfile,'    #Methods'

        generatedMethods=[]
        allmethnames=[m.getName() for m in element.getMethodDefs(recursive=1)]

        for m in element.getMethodDefs():
            self.generateMethod(outfile,m,element,mode=mode)
            allmethnames.append(m.getName())
            generatedMethods.append(m)

        for interface in element.getRealizationParents():
            meths=[m for m in interface.getMethodDefs(recursive=1) if m.getName() not in allmethnames]
            # i dont want to extra generate methods that are already defined in the class
            if meths:
                print >>outfile,'    #methods from Interface %s'%interface.getName()
                for m in meths:
                    self.generateMethod(outfile,m,element,mode=mode)
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
                if manual_methods:
                    print >> outfile, '    #manually created methods\n'

                for mt in manual_methods:
                    declaration = cl.getProtectionDeclaration(mt.getName())
                    if declaration:
                        print >> outfile, declaration
                    print >> outfile, mt.src
                    print >> outfile


    def generateMethod(self, outfile, m, klass, mode='class'):
        #ignore actions and views here because they are
        #generated separately
        if m.hasStereoType(['action','view','form','portlet_view']):
            return

        paramstr=''
        params=m.getParamExpressions()
        if params:
            paramstr=','+','.join(params)
            #print paramstr
        print >> outfile

        if mode == 'class':
            # [optilude] Added check for permission:mode - public (default), private or protected
            # [jensens]  You can also use the visibility value from UML (implemented for 1.2 only!)
            # tgv overrides UML-mode!
            permissionMode = m.getVisibility() or 'public'

            # A public method means it's part of the class' public interface,
            # not to be confused with the fact that Zope has a method called
            # declareProtected() to protect a method which is *part of the
            # class' public interface* with a permission. If a method is public
            # and has no permission set, declarePublic(). If it has a permission
            # declareProtected() by that permission.
            if permissionMode == 'public':
                rawPerm=m.getTaggedValue('permission',None)
                permission=getExpression(rawPerm)
                if rawPerm:
                    print >> outfile,indent("security.declareProtected(%s, '%s')" % (permission,m.getName()),1)
                else:
                    print >> outfile,indent("security.declarePublic('%s')" % (m.getName(),),1)
            # A private method is always declarePrivate()'d
            elif permissionMode == 'private':
                print >> outfile,indent("security.declarePrivate('%s')" % (m.getName(),),1)

            # A protected method is also declarePrivate()'d. The semantic
            # meaning of 'protected' is that is hidden from the outside world,
            # but accessible to subclasses. The model may wish to be explicit
            # about this intention (even though python has no concept of
            # such protection). In this case, it's still a privately declared
            # method as far as TTW code is concerned.
            elif permissionMode == 'protected':
                print >> outfile,indent("security.declarePrivate('%s')" % (m.getName(),),1)

            # A package-level method should be without security declarartion -
            # it is accessible to other methods in the same module, and will
            # use the class/module defaults as far as TTW code is concerned.
            elif permissionMode == 'package':
                # No declaration
                print >> outfile,indent("# Use class/module security defaults",1)
            else:
                print indent("! Warning: method visibility should be 'public', 'private', 'protected' or 'package', got %s." % permissionMode, self.infoind)

        cls=self.parsed_class_sources.get(klass.getPackage().getFilePath()+'/'+klass.getName(),None)

        if cls:
            method_code=cls.methods.get(m.getName())
        else:
            #print 'method not found:',m.getName()
            method_code=None

        if self.method_preservation and method_code:
            #print 'preserve method:',method_code.name
            print >>outfile, method_code.src
        else:
            if mode=='class':
                print >> outfile,'    def %s(self%s):' % (m.getName(),paramstr)
            elif mode=='interface':
                print >> outfile,'    def %s(%s):' % (m.getName(),paramstr[1:])

            code=m.taggedValues.get('code','')
            doc=m.getDocumentation(striphtml=self.striphtml)
            if doc is not None:
                print >> outfile, indent('"""\n%s\n"""' % doc ,2)

            if code and mode=='class':
                print >> outfile, indent('\n'+code,2)
            else:
                print >> outfile, indent('\n'+'pass',2)

        print >> outfile


    def generateBaseTestcaseClass(self,element,template):
        #write runalltests.py and framework.py
        runalltests=readTemplate('tests/runalltests.py')
        framework=readTemplate('tests/framework.py')

        of=self.makeFile(os.path.join(element.getPackage().getFilePath(),'runalltests.py'))
        of.write(runalltests)
        of.close()

        of=self.makeFile(os.path.join(element.getPackage().getFilePath(),'framework.py'))
        of.write(framework)
        of.close()

        return self.generateTestcaseClass(element,template)

    def generateTestcaseClass(self,element,template):
        print indent('Generating testcase: '+element.getName(),self.infoind)
        
        assert element.hasStereoType('plone_testcase') or element.getCleanName().startswith('test'), \
            "names of test classes _must_ start with 'test', but this class is named '%s'" % element.getCleanName()

        assert element.getPackage().getCleanName() == 'tests', \
            "testcase classes only make sense inside a package called 'tests' \
                 but this class is named '%s' and located in package '%s'" % (element.getCleanName(),element.getPackage().getCleanName())
        
        if element.getGenParents():
            parent=element.getGenParents()[0]
        else:
            parent=None

        return BaseGenerator.generatePythonClass(self, element, template, parent=parent)

    def generateWidgetClass(self,element,template,zptname='widget.pt'):
        print indent('Generating widget: '+element.getName(),self.infoind)

        #generate the template
        templpath=os.path.join(self.getSkinPath(element),'%s.pt' % element.getCleanName())
        fieldpt=self.readFile(templpath)
        if not fieldpt:
            templ=readTemplate(zptname)
            d={ 'klass':element,
                'generator':self,
                'parsed_class':element.parsed_class,
                'builtins'   : __builtins__,
                'utils'       :utils,
    
                }
            d.update(__builtins__)
            zptcode=HTML(templ,d)()
    
            fp=self.makeFile(templpath)
            print >>fp,zptcode
            fp.close()

        # and now the python code
        if element.getGenParents():
            parent=element.getGenParents()[0]
            parentname=parent.getCleanName()
        else:
            parent=None
            parentname='TypesWidget'

        return BaseGenerator.generatePythonClass(self, element, template,parent=parent,parentname=parentname)

    def generateFieldClass(self,element,template):
        print indent('Generating field: '+element.getName(),self.infoind)

        # and now the python code
        if element.getGenParents():
            parent=element.getGenParents()[0]
            parentname=parent.getCleanName()
        else:
            if element.getAttributeDefs():
                parent=None
                parentname='CompoundField'
            else:
                parent=None
                parentname='ObjectField'
            
        widgets=element.getClientDependencyClasses(targetStereotypes=['widget'])
        if widgets:
            widget=widgets[0]
            widgetname=widget.getCleanName()
        else:
            widget=None
            widgetname='StringWidget'

        return BaseGenerator.generatePythonClass(self, element, template,
            parent=parent,parentname=parentname,
            widget=widget,widgetname=widgetname)

    def elementIsFolderish(self, element):
        # This entire method hould probably be moved off to the element classes.
        # Copy-pasted from generateArchetypesClass()...
        aggregatedClasses = element.getRefs() + element.getSubtypeNames(recursive=0,filter=['class'])
        #also check if the parent classes can have subobjects
        baseaggregatedClasses=[]
        for b in element.getGenParents():
            baseaggregatedClasses.extend(b.getRefs())
            baseaggregatedClasses.extend(b.getSubtypeNames(recursive=1))
        isFolderish = aggregatedClasses or baseaggregatedClasses or \
                      isTGVTrue(element.getTaggedValue('folderish')) or \
                      element.hasStereoType('folder')
        return bool(isFolderish)

    def generateArchetypesClass(self, element,**kw):
        print indent('Generating class: '+element.getName(),self.infoind)

##        if element.hasStereoType(self.python_stereotype):
##            return BaseGenerator.generateClass(self,element)


        outfile=StringIO()
        print >>outfile, self.generateHeader(element)

        name = element.getCleanName()

        wrt = outfile.write
        wrt('\n')

        parentnames = [p.getCleanName() for p in element.getGenParents()]
        print >>outfile,self.generateDependentImports(element)
        print >>outfile,self.generateAdditionalImports(element)

        if self.detailled_creation_permissions:
            creation_permission = "'Add %s Content'" % element.getCleanName()
        else:
            creation_permission = None

        cpfromoption = self.getOption('creation_permission', element, None)
        if cpfromoption:
            creation_permission = "'%s'" % cpfromoption

        # imports needed for CMFMember subclassing
        if element.hasStereoType(self.cmfmember_stereotype):
            wrt(CMFMEMBER_IMPORTS)
            # and set the add content permission to what CMFMember needs
            creation_permission = 'ADD_MEMBER_PERMISSION'

        # imports needed for optional support of SQLStorage
        if isTGVTrue(self.getOption('sql_storage_support',element,0)):
            wrt('from Products.Archetypes.SQLStorage import *\n')

        # imports by tagged values
        additionalImports=self.getOption('imports',element,None,True)
        if additionalImports:
            wrt("# additional imports from tagged value 'import'\n")
            wrt(additionalImports)
            wrt('\n')

        # [optilude] Import config.py
        wrt(TEMPLATE_CONFIG_IMPORT % {'module' : element.getRootPackage().getProductModuleName()})
        wrt('\n')

        # CMFMember needs a special factory method
        if element.hasStereoType(self.cmfmember_stereotype):
            wrt(CMFMEMBER_ADD % {'module':element.getRootPackage().getProductModuleName(),
                                 'prefix':self.prefix,
                                 'name': name})

        # Normally, archgenxml also looks at the parents of the
        # current class for allowed subitems. Likewise, subclasses of
        # classes allowed as subitems are also allowed on this
        # class. Classic polymorphing. In case this isn't desired, set
        # the tagged value 'disable_polymorphing' to 1.
        disable_polymorphing = element.getTaggedValue('disable_polymorphing', 0)
        if disable_polymorphing:
            recursive = 0
        else:
            recursive = 1
        aggregatedClasses = element.getRefs() + element.getSubtypeNames(recursive=recursive,
                                                                        filter=['class'])
        # We *do* want the resursive=0 below, though!
        aggregatedInterfaces = element.getRefs() + element.getSubtypeNames(recursive=0,
                                                                           filter=['interface'])
        # [xiru] We need to remove duplicated values and avoid mixture 
        # between unicode and string content types identifiers
        if element.getTaggedValue('allowed_content_types'):
            aggregatedClasses = [str(e) for e in aggregatedClasses]
            for e in element.getTaggedValue('allowed_content_types').split(','):
                if str(e) not in aggregatedClasses:
                    aggregatedClasses.append(str(e))

        # if it's a derived class check if parent has stereotype 'archetype'
        parent_is_archetype = False
        for p in element.getGenParents():
            parent_is_archetype = parent_is_archetype or \
                                  p.hasStereoType(self.archetype_stereotype)
        #also check if the parent classes can have subobjects
        baseaggregatedClasses=[]
        for b in element.getGenParents():
            baseaggregatedClasses.extend(b.getRefs())
            baseaggregatedClasses.extend(b.getSubtypeNames(recursive=1))

        #also check if the interfaces used can have subobjects
        baseaggregatedInterfaces=[]
        for b in element.getGenParents(recursive=1):
            baseaggregatedInterfaces.extend(b.getSubtypeNames(recursive=1,filter=['interface']))

        additionalParents=element.getTaggedValue('additional_parents')
        if additionalParents:
            parentnames=list(parentnames)+additionalParents.split(',')

        if self.elementIsFolderish(element):
            # folderish

            if element.hasStereoType('ordered'):
                baseclass ='OrderedBaseFolder'
                baseschema='OrderedBaseFolderSchema'
            elif element.hasStereoType(['large','btree']):
                baseclass ='BaseBTreeFolder'
                baseschema='BaseFolderSchema'
            else:
                baseclass ='BaseFolder'
                baseschema='BaseFolderSchema'

            # XXX: How should <<ordered>> affect this?
            if self.i18n_content_support in self.i18n_at and element.isI18N():
                baseclass='I18NBaseFolder'
                baseschema='I18NBaseFolderSchema'

            if element.getTaggedValue('folder_base_class'):
                raise ValueError, "DEPRECATED: Usage of Tagged Value "\
                      "folder_base_class' in class %s" % element.getCleanName
        else:
            # contentish
            baseclass ='BaseContent'
            baseschema='BaseSchema'
            if self.i18n_content_support in self.i18n_at and element.isI18N():
                baseclass ='I18NBaseContent'
                baseschema='I18NBaseSchema'

        # if a parent is already an archetype we dont need a baseschema!
        if parent_is_archetype:
            baseclass = None

        # CMFMember support
        if element.hasStereoType(self.cmfmember_stereotype):
            baseclass = 'BaseMember.Member'
            baseschema= 'BaseMember.id_schema'

        ## however: tagged values have priority
        # tagged values for base-class overrule
        if element.getTaggedValue('base_class'):
            baseclass=element.getTaggedValue('base_class')

        # tagged values for base-schema overrule
        if element.getTaggedValue('base_schema'):
            baseschema =  element.getTaggedValue('base_schema')

        # normally a one of the Archetypes base classes are set.
        # if you dont want it set the TGV to zero '0'


        # [optilude] Also - ignore the standard class if this is an abstract/mixin
        if baseclass and not isTGVFalse(element.getTaggedValue('base_class',1)) \
           and not element.isAbstract ():
              baseclasses=baseclass.split(',')
              parentnames=parentnames+baseclasses

        # Remark: CMFMember support include VariableSchema support
        if element.hasStereoType(self.variable_schema) and \
             not element.hasStereoType(self.cmfmember_stereotype):
            parentnames.insert(0,'VariableSchemaSupport')

        # a tool needs to be a unique object
        if element.hasStereoType(self.portal_tools):
            print >>outfile,TEMPL_TOOL_HEADER
            parentnames.insert(0,'UniqueObject')

        parents=','.join(parentnames)

        # protected section
        self.generateProtectedSection(outfile,element,'module-header')

        # here comes the schema
        print >> outfile, self.generateArcheSchema(element,baseschema)

        # protected section
        self.generateProtectedSection(outfile,element,'after-schema')

        if not element.isComplex():
            print "I: stop complex: ", element.getName()
            return outfile.getvalue()
        if element.getType() in AlreadyGenerated:
            print "I: stop already generated:", element.getName()
            return outfile.getvalue()
        AlreadyGenerated.append(element.getType())

        if self.ape_support:
            print >>outfile,TEMPL_APE_HEADER % {'class_name':name}

        # [optilude] It's possible parents may become empty now...
        if parents:
            parents = "(%s)" % (parents,)
        else:
            parents = ''
        # [optilude] ... so we can't have () around the last %s
        classDeclaration = 'class %s%s%s:\n' % (self.prefix, name, parents)

        wrt(classDeclaration)
        doc = element.getDocumentation(striphtml=self.striphtml)
        parsedDoc = ''
        if element.parsed_class:
            parsedDoc = element.parsed_class.getDocumentation()
        if doc:
            print >>outfile,indent('"""\n%s\n"""' % doc, 1)
        elif parsedDoc:
            # Bit tricky, parsedDoc is already indented...
            print >>outfile, '    """%s"""' % parsedDoc

        print >>outfile,indent('security = ClassSecurityInfo()',1)

        print >>outfile,self.generateImplements(element,parentnames)
        print >>outfile
        header=element.getTaggedValue('class_header')
        if header:
            print >>outfile,indent(header, 1)

        archetype_name=element.getTaggedValue('archetype_name') or element.getTaggedValue('label')
        if not archetype_name:
            archetype_name=name

        # [optilude] Only output portal type and AT name if it's not an abstract
        # mixin
        if not element.isAbstract ():
            print >> outfile, CLASS_ARCHETYPE_NAME %  archetype_name
            print >> outfile, CLASS_PORTAL_TYPE % name

        #allowed_content_classes
        parentAggregates=''
        
        if isTGVTrue(element.getTaggedValue('inherit_allowed_types', True)) and element.getGenParents():
            parentAggregates = '+ ' + ' + '.join(tuple(["list(getattr(%s,'allowed_content_types',[]))"%p.getCleanName() for p in element.getGenParents()]))
        print >> outfile, CLASS_ALLOWED_CONTENT_TYPES % (repr(aggregatedClasses),parentAggregates)

        #allowed_content_interfaces
        parentAggregatedInterfaces=''
        if isTGVTrue(element.getTaggedValue('inherit_allowed_types', True)) and element.getGenParents():
            parentAggregatedInterfaces = '+ ' + ' + '.join(tuple(['getattr('+p.getCleanName()+",'allowed_content_interfaces',[])" for p in element.getGenParents()]))

        if aggregatedInterfaces or baseaggregatedInterfaces:
            print >> outfile, CLASS_ALLOWED_CONTENT_INTERFACES % \
                  (repr(aggregatedInterfaces),parentAggregatedInterfaces)


        # FTI as attributes on class
        # [optilude] Don't generate FTI for abstract mixins
        if not element.isAbstract ():
            fti=self.generateFti(element,aggregatedClasses)
            print >> outfile,fti

        # prepare schema as class attribute
        parent_schema=["getattr(%s,'schema',Schema(()))" % p.getCleanName() \
                       for p in element.getGenParents()]

        if parent_is_archetype and \
           not element.hasStereoType(self.cmfmember_stereotype):
            schema = parent_schema
        else:
            # [optilude] Ignore baseschema in abstract mixin classes
            if element.isAbstract ():
                schema = parent_schema
            else:
                schema = [baseschema] + parent_schema

        # own schema overrules base and parents
        schema += ['schema']

        if element.hasStereoType(self.cmfmember_stereotype):
            for addschema in ['contact_schema','plone_schema',
                              'security_schema','login_info_schema',]:
                if isTGVTrue(element.getTaggedValue(addschema, '1')):
                    schema.append('BaseMember.%s' % addschema)
            if isTGVTrue(element.getTaggedValue(addschema, '1')):
                schema.append('ExtensibleMetadata.schema')

        print >> outfile, indent('schema = ' + ' + \\\n         '.join(schema),1)
        print >> outfile

        self.generateProtectedSection(outfile,element,'class-header',1)

        # tool __init__
        if element.hasStereoType(self.portal_tools):
            tool_instance_name=element.getTaggedValue('tool_instance_name') or 'portal_%s' % element.getName().lower()
            print >> outfile,TEMPL_CONSTR_TOOL % (baseclass,tool_instance_name)
            self.generateProtectedSection(outfile,element,'constructor-footer',2)
            print >> outfile

        self.generateMethods(outfile,element)

        # [optilude] Don't do modify FTI for abstract mixins
        if not element.isAbstract ():
            print >> outfile, self.generateModifyFti(element)

        # [optilude] Don't register type for abstract classes or tools
        if not (element.isAbstract ()):
            wrt( REGISTER_ARCHTYPE % name)

        # ATVocabularyManager: registration of class
        if element.hasStereoType(self.vocabulary_item_stereotype) and \
           not element.isAbstract ():
            # XXX TODO: fetch container_class - needs to be refined:
            # check if parent has vocabulary_container_stereotype and use its
            # name as container
            # else check for TGV vocabulary_container
            # fallback: use SimpleVocabulary
            container = element.getTaggedValue('vocabulary:portal_type','SimpleVocabulary')
            wrt( REGISTER_VOCABULARY_ITEM % (name, container) )
        if element.hasStereoType(self.vocabulary_container_stereotype):
            wrt( REGISTER_VOCABULARY_CONTAINER % name )

        wrt('# end of class %s\n\n'   % name)

        self.generateProtectedSection(outfile,element,'module-footer')

        ## handle add content permissions
        if not element.hasStereoType(self.portal_tools):
            cpfromtgv = element.getTaggedValue('creation_permission', None)
            if cpfromtgv:
                creation_permission= "'%s'" % cpfromtgv
            ## abstract classes does not need an Add permission
            if creation_permission and not element.isAbstract():
                self.creation_permissions.append( [element.getCleanName(), creation_permission] )

        return outfile.getvalue()

    def generateInterface(self, outfile, element):
        wrt = outfile.write
##        print 'Interface:',element.getName()
##        print 'parents:',element.getGenParents()

        parentnames = [p.getCleanName() for p in element.getGenParents()]

        print >>outfile,self.generateDependentImports(element)
        print >>outfile,self.generateAdditionalImports(element)

        print >> outfile, IMPORT_INTERFACE

        additionalImports=element.getTaggedValue('imports')
        if additionalImports:
            wrt(additionalImports)

        aggregatedClasses = element.getRefs() + element.getSubtypeNames(recursive=1)

        AlreadyGenerated.append(element.getType())
        name = element.getCleanName()

        wrt('\n')

        additionalParents=element.getTaggedValue('additional_parents')
        if additionalParents:
            parentnames=list(parentnames)+additionalParents.split(',')

        if not [c for c in element.getGenParents() if c.isInterface()]:
            parentnames.insert(0,'Base')
        parents=','.join(parentnames)

        s1 = 'class %s%s(%s):\n' % (self.prefix, name, parents)

        wrt(s1)
        doc=element.getDocumentation(striphtml=self.striphtml)
        print >>outfile,indent('"""\n%s\n"""' % doc, 1)

        header=element.getTaggedValue('class_header')
        if header:
            print >>outfile,indent(header, 1)

        self.generateMethods(outfile,element,mode='interface')

        wrt('# end of class %s\n'   % name)


    def getAuthors(self, element):
        authors = self.getOption('author', element, self.author) or 'unknown'
        authors = authors.split(',')
        authors = [i.strip() for i in authors]

        emails = self.getOption('email', element, self.email) or 'unknown'
        emails = emails.split(',')
        emails = ['<%s>' % i.strip() for i in emails]

        authoremail = []
        for author in authors:
            if authors.index(author) < len(emails):
                authoremail.append("%s %s" % (author, emails[authors.index(author)]))
            else:
                authoremail.append("%s <unknown>" % author)

        authorline = wrap(", ".join(authoremail),77)

        return authors, emails, authorline

    def getHeaderInfo(self, element):
        #deal with multiline docstring
        purposeline=('\n').join( \
            (element.getDocumentation(striphtml=self.striphtml,wrap=79) or 'unknown').split('\n') )

        copyright = COPYRIGHT % \
            (str(time.localtime()[0]),
             self.getOption('copyright', element, self.copyright) or self.author)

        licence = ('\n# ').join( \
            wrap(self.getOption('license', element, GPLTEXT),77).split('\n') )

        authors, emails, authorline = self.getAuthors(element)

        rcs_id = self.getOption('rcs_id', element, False)

        if rcs_id:
            rcs_id_tag = '\nRCS-ID $'+'I'+'d'+'$'
        else:
            rcs_id_tag = ''

        if self.getOption('generated_date', element, False):
            date = '# Generated: %s\n' % time.ctime()
        else:
            date = ''

        moduleinfo = {  'purpose':      purposeline,
                        'authors':      ', '.join(authors),
                        'emails' :      ', '.join(emails),
                        'authorline':   authorline,
                        'version':      self.version,
                        'date':         date,
                        'copyright':    '\n# '.join(wrap(copyright,77).split('\n')),
                        'licence':      licence,
                        'rcs_id_tag':   rcs_id_tag
        }

        return moduleinfo

    def generateModuleInfoHeader(self, outfile, modulename, element):
        if not self.module_info_header:
            return
        fileheaderinfo = self.getHeaderInfo(element)
        fileheaderinfo.update({'filename': modulename+'.py'})
        outfile.write(MODULE_INFO_HEADER % fileheaderinfo)

    def generateHeader(self, element):
        outfile=StringIO()
        i18ncontent = self.getOption('i18ncontent',element,
                                        self.i18n_content_support)

        if i18ncontent in self.i18n_at and element.isI18N():
            s1 = TEMPLATE_HEADER_I18N_I18N_AT
        elif i18ncontent == 'linguaplone':
            s1 = TEMPLATE_HEADER_I18N_LINGUAPLONE
        else:
            s1 = TEMPLATE_HEADER

        outfile.write(s1)

        return outfile.getvalue()

    def getTools(self,package,autoinstallOnly=0):
        """ returns a list of  generated tools """
        res=[c for c in package.getClasses(recursive=1) if
                    c.hasStereoType(self.portal_tools)]
                  
        if autoinstallOnly:
            res=[c for c in res if isTGVTrue(c.getTaggedValue('autoinstall')) ]
        
        return res

    def getGeneratedTools(self,package):
        """ returns a list of  generated tools """
        return [c for c in self.getGeneratedClasses(package) if
                    c.hasStereoType(self.portal_tools)]

    def generateStdFiles(self, package):
        if package.isRoot():
            self.generateStdFilesForProduct(package)
        else:
            self.generateStdFilesForPackage(package)

    def generateStdFilesForPackage(self, package):
        """Generate the standard files for a non-root package"""

        # Generate an __init__.py
        self.generatePackageInitPy(package)

    def updateVersionForProduct(self, package):
        """Increment the build number in verion.txt"""

        build=1
        versionbase='0.1'
        fp=os.path.join(package.getFilePath(),'version.txt')
        vertext=self.readFile(fp)
        if vertext:
            versionbase=vertext=vertext.strip()
            parsed=vertext.split(' ')
            if parsed.count('build'):
                ind=parsed.index('build')
                try:
                    build=int(parsed[ind+1]) + 1
                except:
                    build=1

                versionbase=' '.join(parsed[:ind])

        version='%s build %d\n' % (versionbase,build)
        of=self.makeFile(fp)
        print >>of,version,
        of.close()

    def generateInstallPy(self, package):
        """Generate Extensions/Install.py from the DTML template"""

        # create Extension directory
        installTemplate=open(os.path.join(sys.path[0],'templates','Install.py')).read()
        extDir=os.path.join(package.getFilePath(),'Extensions')
        self.makeDir(extDir)

        # make __init__.py
        ipy=self.makeFile(os.path.join(extDir,'__init__.py'))
        ipy.write('# make me a python module\n')
        ipy.close()

        # prepare (d)TML varibles
        d={'package'    : package,
           'generator'  : self,
           'builtins'   : __builtins__,
           'utils'       :utils,
        }
        d.update(__builtins__)

        templ=readTemplate('Install.py')
        dtml=HTML(templ,d)
        res=dtml()

        of=self.makeFile(os.path.join(extDir,'Install.py'))
        of.write(res)
        of.close()

        return

    def generateConfigPy(self, package):
        """ generates: config.py """

        configpath=os.path.join(package.getFilePath(),'config.py')
        parsed_config=self.parsePythonModule(package.getFilePath(), 'config.py')
        creation_permission = self.getOption('creation_permission', package, None) or \
                              package.getProductName().capitalize()
        default_creation_permission = 'Add %s Content' % creation_permission

        # prepare (d)TML varibles
        d={'package'                    : package,
           'generator'                  : self,
           'builtins'                   : __builtins__,
           'utils'                      : utils,
           'creation_permissions'       : self.creation_permissions,
           'parsed_config'              : parsed_config,
           'default_creation_permission': default_creation_permission,
        }
        d.update(__builtins__)

        templ=readTemplate('config.py')
        dtml=HTML(templ,d)
        res=dtml()

        of=self.makeFile(configpath)
        of.write(res)
        of.close()

        return

    def generateProductInitPy(self, package):
        """ Generate __init__.py at product root from the DTML template"""

        # Get the names of packages and classes to import
        packageImports = [m.getModuleName() for m in package.getAnnotation('generatedPackages') if not m.hasStereoType('tests') or []]
        classImports   = [m.getModuleName() for m in package.generatedModules if not m.hasStereoType('tests')]
        
        # Find additional (custom) permissions
        additional_permissions=[]
        addperms= self.getOption('additional_permission',package,default=[]),
        for line in addperms:
            if len(line)>0:
                line=line.split('|')
                line[0]=line[0].strip()
                if len(line)>1:
                    line[1]=["'%s'" % r.strip() for r in line[1].split(',')]
                additional_permissions.append(line)

        # Find out if we need to initialise any tools
        generatedTools = self.getGeneratedTools(package)
        hasTools = 0
        toolNames = []
        if generatedTools:
            toolNames = [c.getQualifiedName(package, includeRoot=0) for c in generatedTools]
            hasTools = 1

        # Get the preserved code section
        parsed = self.parsePythonModule(package.getFilePath (), '__init__.py')
        
        protectedInitCodeH = self.getProtectedSection(parsed, 'custom-init-head', 0)
        protectedInitCodeT = self.getProtectedSection(parsed, 'custom-init-top', 1)
        protectedInitCodeB = self.getProtectedSection(parsed, 'custom-init-bottom', 1)

        # prepare DTML varibles
        d={'generator'                     : self,
           'utils'                         : utils,
           'package'                       : package,
           'product_name'                  : package.getProductName (),
           'package_imports'               : packageImports,
           'class_imports'                 : classImports,
           'additional_permissions'        : additional_permissions,
           'has_tools'                     : hasTools,
           'tool_names'                    : toolNames,
           'creation_permissions'          : self.creation_permissions,
           'protected_init_section_head'   : protectedInitCodeH,
           'protected_init_section_top'    : protectedInitCodeT,
           'protected_init_section_bottom' : protectedInitCodeB,
        }

        templ=readTemplate('__init__.py')
        dtml=HTML(templ,d)
        res=dtml()

        of=self.makeFile(os.path.join(package.getFilePath(),'__init__.py'))
        of.write(res)
        of.close()

        return

    def generatePackageInitPy(self, package):
        """ Generate __init__.py for packages from the DTML template"""

        # Get the names of packages and classes to import
        packageImports = [m.getModuleName () for m in package.getAnnotation('generatedPackages') or []]
        classImports   = [m.getModuleName () for m in package.generatedModules]

        # Get the preserved code sections
        parsed = self.parsePythonModule(package.getFilePath (), '__init__.py')
        headerCode = self.getProtectedSection(parsed, 'init-module-header')
        footerCode = self.getProtectedSection(parsed, 'init-module-footer')

        # Prepare DTML varibles
        d={'generator'                     : self,
           'package'                       : package,
           'utils'                         : utils,
           'package_imports'               : packageImports,
           'class_imports'                 : classImports,
           'protected_module_header'       : headerCode,
           'protected_module_footer'       : footerCode,
           }

        templ=readTemplate('__init_package__.py')
        dtml=HTML(templ,d)
        res=dtml()

        of=self.makeFile(os.path.join(package.getFilePath(),'__init__.py'))
        of.write(res)
        of.close()

        return


    def generateStdFilesForProduct(self, package):
        """Generate __init__.py,  various support files and and the skins
        directory. The result is a QuickInstaller installable product
        """

        target = package.getFilePath ()

        # remove trailing slash
        if target[-1] in ('/','\\'):
            target=target[:-1]

        templdir=os.path.join(sys.path[0],'templates')

        # Create a tool.gif if necessary
        if self.getGeneratedTools(package):
            toolgif=open(os.path.join(templdir,'tool.gif')).read()
            of=self.makeFile(os.path.join(package.getFilePath(),'tool.gif'))
            of.write(toolgif)
            of.close()

        # Generate a refresh.txt for the product
        of=self.makeFile(os.path.join(package.getFilePath(),'refresh.txt'))
        of.close()

        # Increment version.txt build number
        self.updateVersionForProduct(package)

        # Generate product root __init__.py
        self.generateProductInitPy(package)

        # Create a customisation policy if required
        if self.customization_policy:
            of=self.makeFile(os.path.join(package.getFilePath(),'CustomizationPolicy.py'),0)
            if of:
                cpTemplate=readTemplate('CustomizationPolicy.py')
                d={'package':package,'generator':self}
                cp=HTML(cpTemplate,d)()
                of.write(cp)
                of.close()

        # Generate config.py from template
        self.generateConfigPy(package)

        # Generate Extensions/Install.py
        self.generateInstallPy(package)



    def generateApeConf(self, target,package):
        #generates apeconf.xml

        #remove trailing slash
        if target[-1] in ('/','\\'):
            target=target[:-1]

        templdir=os.path.join(sys.path[0],'templates')
        apeconfig_object=open(os.path.join(templdir,'apeconf_object.xml')).read()
        apeconfig_folder=open(os.path.join(templdir,'apeconf_folder.xml')).read()

        of=self.makeFile(os.path.join(target,'apeconf.xml'))
        print >> of, TEMPL_APECONFIG_BEGIN
        for el in self.root.getClasses():
            if el.isInternal() or el.hasStereoType(self.stub_stereotypes):
                continue

            print >>of
            if el.getRefs() + el.getSubtypeNames(recursive=1):
                print >>of,apeconfig_folder % {'project_name':package.getProductName(),'class_name':el.getCleanName()}
            else:
                print >>of,apeconfig_object % {'project_name':package.getProductName(),'class_name':el.getCleanName()}

        print >>of, TEMPL_APECONFIG_END
        of.close()

    def getGeneratedClasses(self,package):
        classes=package.getAnnotation('generatedClasses') or []
        for p in package.getPackages():
            if not p.isProduct():
                classes.extend(self.getGeneratedClasses(p))
        res=[]
        for c in classes:
            if c not in res:
                res.append(c)
        return res

    def generatePackage(self,package,recursive=1):

        if package.hasStereoType(self.stub_stereotypes):
            return
        package.generatedModules=[]
        if package.getName().lower() == 'java' or package.getName().lower().startswith('java') or not package.getName():
            #to suppress these unneccesary implicit created java packages (ArgoUML and Poseidon)
            print indent('ignore package:'+package.getName(),self.infoind)
            return

        self.makeDir(package.getFilePath())

        for element in package.getClasses()+package.getInterfaces():
            #skip stub and internal classes
            if element.isInternal() or element.getName() in self.hide_classes \
               or element.getName().lower().startswith('java::'): # Enterprise Architect fix!
                print indent('Ignore unnecessary class: '+element.getName(),self.infoind)
                if element.getName() == 'XPointField':
                    print 'hide_classes:',self.hide_classes
                    import pdb;pdb.set_trace()
                    
                continue
            if element.hasStereoType(self.stub_stereotypes):
                print indent('Ignore stub class: '+element.getName(),self.infoind)
                continue

            module=element.getModuleName()
            package.generatedModules.append(element)
            outfilepath=os.path.join(package.getFilePath(), module+'.py')
            #print 'writing class:',outfilepath

            if self.method_preservation:
                try:
                    #print 'existing sources found for:',element.getName(),outfilepath
                    mod=PyParser.PyModule(os.path.join(self.targetRoot, outfilepath))
                    #mod.printit()
                    self.parsed_sources.append(mod)
                    for c in mod.classes.values():
                        #print 'parse module:',c.name
                        self.parsed_class_sources[package.getFilePath()+'/'+c.name]=c
                except IOError:
                    #print 'no source found at %s' % os.path.join(self.targetRoot, outfilepath)
                    pass
                except :
                    print
                    print '***'
                    print '***Error while reparsing the file '+outfilepath
                    print '***'
                    print

                    raise

            try:
                outfile=StringIO()
                #print element.getPackage().getFilePath()+'/'+element.name
                element.parsed_class = self.parsed_class_sources.get(element.getPackage().getFilePath()+'/'+element.name,None)
                self.generateModuleInfoHeader(outfile, module, element)
                if not element.isInterface():
                    print >>outfile, self.generateClass(element)
                    generated_classes = package.getAnnotation('generatedClasses') or []
                    generated_classes.append(element)
                    package.annotate('generatedClasses', generated_classes)
                else:
                    self.generateInterface(outfile,element)

                classfile=self.makeFile(outfilepath)
                buf=outfile.getvalue()
                print >> classfile,buf
                classfile.close()
            except:
                #roll back the changes
                # and dont swallow the exception
                raise

        #generate subpackages
        generatedPkg = package.getAnnotation('generatedPackages') or []
        for p in package.getPackages():
            if p.isProduct():
                self.infoind+=+1
                self.generateProduct(p)
                self.infoind-=1
            else:
                print indent('generating package: '+ p.getName(),self.infoind)
                self.infoind+=1
                self.generatePackage(p,recursive=1)
                self.infoind-=1
                generatedPkg.append(p)
                package.annotate('generatedPackages',generatedPkg)

        self.generateStdFiles(package)
        
    def generateRelation(self, doc, collection, relname, relid, 
            sourcetype=None, targettype=None,
            sourceinterface=None,targetinterface=None,
            sourcecardinality=(None,None),
            targetcardinality=(None,None),
            assocclassname=None,
            inverse_relation_id=None,
            primary=0,
            ):
                
        ruleset=doc.createElement('Ruleset')
        ruleset.setAttribute('id',relname)
        ruleset.setAttribute('uid',relid)
        collection.appendChild(ruleset)
        
        #type and interface constraints
        if sourcetype or targettype:
            typeconst=doc.createElement('TypeConstraint')
            typeconst.setAttribute('id','type_constraint')
            ruleset.appendChild(typeconst)

        if sourceinterface or targetinterface:
            ifconst=doc.createElement('InterfaceConstraint')
            ifconst.setAttribute('id','interface_constraint')
            ruleset.appendChild(ifconst)


        if sourcetype:
            el=doc.createElement('allowedSourceType')
            typeconst.appendChild(el)
            el.appendChild(doc.createTextNode(sourcetype))
        if sourceinterface:
            el=doc.createElement('allowedSourceInterface')
            ifconst.appendChild(el)
            el.appendChild(doc.createTextNode(sourceinterface))

        if targettype:
            el=doc.createElement('allowedTargetType')
            typeconst.appendChild(el)
            el.appendChild(doc.createTextNode(targettype))
        if targetinterface:
            ifconst.setAttribute('id','interface_constraint')
            el=doc.createElement('allowedTargetInterface')
            ifconst.appendChild(el)
            el.appendChild(doc.createTextNode(targetinterface))
            

        #association constraint
        if assocclassname:
            contref=doc.createElement('ContentReference')
            ruleset.appendChild(contref)
            contref.setAttribute('id','content_reference')
            pt=doc.createElement('portalType')
            contref.appendChild(pt)
            pt.appendChild(doc.createTextNode(assocclassname))

            pt=doc.createElement('shareWithInverse')
            contref.appendChild(pt)
            pt.appendChild(doc.createTextNode('1'))

            el=doc.createElement('primary')
            el.appendChild(doc.createTextNode(str(primary)))
            contref.appendChild(el)
        
        #cardinality
        targetcardinality=list(targetcardinality)
        if targetcardinality[0]==-1:targetcardinality[0]=None
        if targetcardinality[1]==-1:targetcardinality[1]=None

        if targetcardinality != (None,None):
            const=doc.createElement('CardinalityConstraint')
            ruleset.appendChild(const)
            const.setAttribute('id','cardinality')
            if targetcardinality[0]:
                el=doc.createElement('minTargetCardinality')
                const.appendChild(el)
                el.appendChild(doc.createTextNode(str(targetcardinality[0])))
            if targetcardinality[1]:
                el=doc.createElement('maxTargetCardinality')
                const.appendChild(el)
                el.appendChild(doc.createTextNode(str(targetcardinality[1])))
            
            
        #create the inverse relation
        if inverse_relation_id:
            const=doc.createElement('InverseImplicator')
            ruleset.appendChild(const)
            const.setAttribute('id','inverse_relation')
            el=doc.createElement('inverseRuleset')
            const.appendChild(el)
            el.setAttribute('uidref',inverse_relation_id)
            
        
        return ruleset
    
    def generateRelations(self,package):
        doc=minidom.Document()
        lib=doc.createElement('RelationsLibrary')
        doc.appendChild(lib)
        coll=doc.createElement('RulesetCollection')
        coll.setAttribute('id',package.getCleanName())
        lib.appendChild(coll)
        package.num_generated_relations=0
        
        for assoc in package.getAssociations(recursive=1):
            if self.getOption('relation_implementation',assoc,'basic') != 'relations':
                continue
            
            source=assoc.fromEnd.obj
            target=assoc.toEnd.obj
            
            targetcard=list(assoc.toEnd.mult)
            sourcecard=list(assoc.fromEnd.mult)
            sourcecard[0]=None #temporary pragmatic fix
            targetcard[0]=None #temporary pragmatic fix
            print 'relation:',assoc.getName(),'target cardinality:',targetcard,'sourcecard:',sourcecard
            sourcetype=None
            targettype=None
            sourceinterface=None
            targetinterface=None

            if source.isInterface():
                sourceinterface=source.getCleanName()
            else:
                sourcetype=source.getCleanName()
                
            if target.isInterface():
                targetinterface=target.getCleanName()
            else:
                targettype=target.getCleanName()    
                
            
            inverse_relation_name=assoc.getTaggedValue('inverse_relation_name',None) 
            if not inverse_relation_name and assoc.fromEnd.isNavigable:
                inverse_relation_name=assoc.getCleanName()+'_inverse'
                
            assocclassname=getattr(assoc,'isAssociationClass',0) and assoc.getCleanName() or assoc.getTaggedValue('association_class')
                
            self.generateRelation(doc, coll,
                assoc.getCleanName(), 
                assoc.getId(),
                sourcetype=sourcetype,
                targettype=targettype,
                sourceinterface=sourceinterface,
                targetinterface=targetinterface,
                sourcecardinality=sourcecard,
                targetcardinality=targetcard,

                assocclassname=assocclassname,
                inverse_relation_id=inverse_relation_name,
                primary=1
                )
                
            #create the counterrelation
            if inverse_relation_name:
                self.generateRelation(doc, coll,
                    inverse_relation_name, 
                    inverse_relation_name,
                    sourcetype=targettype,
                    targettype=sourcetype,
                    sourceinterface=targetinterface,
                    targetinterface=sourceinterface,
                    sourcecardinality=targetcard,
                    targetcardinality=sourcecard,
    
                    assocclassname=assocclassname,
                    inverse_relation_id=assoc.getId()
                    )
                
            package.num_generated_relations += 1
                
        if package.num_generated_relations:    
            of=self.makeFile(os.path.join(package.getFilePath(),'relations.xml'))
            print >>of,doc.toprettyxml()
            of.close()
        
        
    def generateProduct(self, root):
        dirMode=0
        outfile=None

        if self.generate_packages and root.getCleanName() not in self.generate_packages:
            print indent('Info: Skipping package:' + root.getCleanName(),self.infoind)
            return

        dirMode=1
        if root.hasStereoType(self.stub_stereotypes):
            print indent('Skipping stub Product:' + root.getName(), self.infoind)
            return

        print indent(">>> Starting new Product: " +root.getName(),self.infoind)
        self.infoind+=1

        # before generate a Product we need to push the current permissions on a
        # stack in orderto reinitialize the permissions
        self.creation_permission_stack.append(self.creation_permissions)
        self.creation_permissions = []

        #create the directories
        self.makeDir(root.getFilePath())
        self.makeDir(os.path.join(root.getFilePath(),'skins'))
        self.makeDir(os.path.join(root.getFilePath(),'skins',
            root.getProductModuleName()))
        self.makeDir(os.path.join(root.getFilePath(),'skins',
            root.getProductModuleName()+'_public'))

        of=self.makeFile(os.path.join(root.getFilePath(),'skins',
            root.getProductModuleName()+'_public','readme.txt')
        )
        print >> of, READMEHIGHEST % root.getProductName()
        of.close()

        of=self.makeFile(os.path.join(root.getFilePath(),'skins',
                                root.getProductModuleName(),'readme.txt'))
        print >> of, READMELOWEST % root.getProductName()
        of.close()

        # prepare messagecatalog
        if has_i18ndude and self.build_msgcatalog:
            self.makeDir(os.path.join(root.getFilePath(),'i18n'))
            filepath=os.path.join(root.getFilePath(),'i18n','generated.pot')
            if not os.path.exists(filepath):
                templdir=os.path.join(sys.path[0],'templates')
                PotTemplate = open(os.path.join(sys.path[0],'templates','generated.pot')).read()
                PotTemplate = PotTemplate % {
                    'author':self.author or 'unknown author',
                    'email':self.email or 'unknown@email.address',
                    'year': str(time.localtime()[0]),
                    'datetime': time.ctime(),
                    'charset':sys.getdefaultencoding(),
                    'package': root.getProductName(),
                }
                of=self.makeFile(filepath)
                of.write(PotTemplate)
                of.close()
            self.msgcatstack.append(msgcatalog.MessageCatalog(
                    filename=os.path.join(self.targetRoot, filepath) ))




        package=root

        self.generateRelations(root)
        self.generatePackage(root)

        if self.ape_support:
            self.generateApeConf(root.getFilePath(),root)

        
        # write messagecatalog
        if has_i18ndude and self.build_msgcatalog:
            filepath=os.path.join(root.getFilePath(),'i18n','generated.pot')
            of=self.makeFile(filepath) or open(filepath,'w')
            pow=msgcatalog.POWriter(of,self.msgcatstack.pop() )
            pow.write()
            of.close()


        #start Workflow creation
        wfg=WorkflowGenerator(package,self)
        wfg.generateWorkflows()
        self.infoind-=1
        self.creation_permissions = self.creation_permission_stack.pop()

    def parseAndGenerate(self):

        # and now start off with the class files
        self.generatedModules=[]

        suff=os.path.splitext(self.xschemaFileName)[1].lower()
        print 'Parsing...'
        print '==============='
        if not self.noclass:
            if suff.lower() in ('.xmi','.xml'):
                print 'opening xmi'
                self.root=root=XMIParser.parse(self.xschemaFileName,
                    packages=self.parse_packages,generator=self,    
                    generate_datatypes=self.generate_datatypes)
                    
            elif suff.lower() in ('.zargo','.zuml','.zip'):
                print 'opening zargo'
                zf=ZipFile(self.xschemaFileName)
                xmis=[n for n in zf.namelist() if os.path.splitext(n)[1].lower()in ['.xmi','.xml']]
                assert(len(xmis)==1)
                buf=zf.read(xmis[0])
                self.root=root=XMIParser.parse(xschema=buf,
                    packages=self.parse_packages, generator=self,
                    generate_datatypes=self.generate_datatypes)
            elif suff.lower() == '.xsd':
                self.root=root=XSDParser.parse(self.xschemaFileName)
            else:
                raise TypeError,'input file not of type .xsd, .xmi, .xml, .zargo, .zuml'

            if self.outfileName:
                root.setName(os.path.split(self.outfileName)[1])

            print 'outfile:',self.outfileName
        else:
            self.root=root=DummyModel(self.outfileName)
        print 'Generating...'
        print '=============='
        if self.method_preservation:
            print 'method bodies will be preserved'
        else:
            print 'method bodies will be overwritten'
        if not has_enhanced_strip_support:
            print "Warning: Can't build i18n message catalog. Needs 'python 2.3' or later."
        if self.build_msgcatalog and not has_i18ndude:
            print "Warning: Can't build i18n message catalog. Module 'i18ndude' not found."
        if not XMIParser.has_stripogram:
            print "Warning: Can't strip html from doc-strings. Module 'stripogram' not found."
        self.generateProduct(root)
