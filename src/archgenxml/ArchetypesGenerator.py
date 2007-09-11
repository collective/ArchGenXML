# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:        ArchetypesGenerator.py
# Purpose:     main class generating archetypes code out of an UML-model
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# Copyright:   (c) 2003-2007 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys
import time
import types
import os.path
import logging
import datetime
from types import StringTypes
from sets import Set
import utils
from odict import odict
from codesnippets import *

from xml.dom import minidom
from zipfile import ZipFile
from cStringIO import StringIO

# AGX-specific imports
import PyParser
import XMIParser
import atmaps
from archgenxml.interfaces import IOptions

from atumlprofile import at_uml_profile

from BaseGenerator import BaseGenerator
from WorkflowGenerator import WorkflowGenerator

from CodeSectionHandler import handleSectionedFile

from documenttemplate.documenttemplate import HTML

from zope import interface
from zope import component

from archgenxml.plone.interfaces import IConfigPyView
from archgenxml.uml.interfaces import *

_marker = []
log = logging.getLogger('generator')

try:
    from i18ndude import catalog as msgcatalog
except ImportError:
    has_i18ndude = False
else:
    has_i18ndude = True

try:
    'abca'.strip('a')
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
    
    def __init__(self, name=''):
        self.name = name

    def getName(self):
        return self.name

    def hasStereoType(self, s, umlprofile=None):
        return True

    def getClasses(self, *a, **kw):
        return []

    def isRoot(self):
        return 1

    def getAnnotation(self, *a, **kw):
        return None

    def getDocumentation(self, **kw):
        return None

    def hasTaggedValue(self, *a, **kw):
        return None

    def getParent(self, *a, **kw):
        return None
    
    getCleanName = getName
    getFilePath = getName
    getModuleFilePath = getName
    getProductModuleName = getName
    getProductName = getName
    
    getInterfaces = getClasses
    getPackages = getClasses
    getStateMachines = getClasses
    getAssociations = getClasses


class ArchetypesGenerator(BaseGenerator):
    
    generator_generator = 'archetypes'
    default_class_type = 'content_class'
    default_interface_type = 'z3'
    
    uml_profile = at_uml_profile
    
    hide_classes = atmaps.HIDE_CLASSES
    typeMap = atmaps.TYPE_MAP
    widgetMap = atmaps.WIDGET_MAP
    coerceMap = atmaps.COERCE_MAP

    build_msgcatalog = 1
    striphtml = 0

    reservedAtts = ['id']
    portal_tools = ['portal_tool', 'tool']
    variable_schema = 'variable_schema'

    stub_stereotypes = ['odStub','stub']
    archetype_stereotype = ['archetype']
    vocabulary_item_stereotype = ['vocabulary_term']
    vocabulary_container_stereotype = ['vocabulary']
    remember_stereotype = ['remember']
    python_stereotype = ['python', 'python_class', 'view']
    folder_stereotype = ['atfolder', 'folder', 'ordered', 'large', 'btree']
    atct_stereotype = ['atfolder', 'atfile', 'atdocument', 'atevent',]

    generate_datatypes = ['field', 'compound_field']

    # Should be 'Products.' be prepended to all absolute paths?
    force_plugin_root = 1

    customization_policy = 0
    backreferences_support = 0

    # Contains the parsed sources by class names (for preserving method codes)
    parsed_class_sources = {}

    # Contains the parsed sources (for preserving method codes)
    parsed_sources = []

    # TaggedValues that are not strings, e.g. widget or vocabulary
    nonstring_tgvs = atmaps.NONSTRING_TGVS

    msgcatstack = []

    # ATVM: collects all used vocabularies in the format:
    # { productsname: (name, meta_type) }
    # If metatype is None, it defaults to SimpleVocabulary.
    vocabularymap = {}

    # If a reference has the same name as another _and_
    # its source object is the same, we want only one ReferenceWidget
    # _unless_ we have a tagged value 'single' on the reference
    reference_groups = []

    # for each class an own permission can be defined, how should be able to add
    # it. It default to "Add Portal Content" and
    creation_permissions = []

    # the stack is needed to remind permissions while a subproduct is generated
    creation_permission_stack = []

    def __init__(self, xschemaFileName, **kwargs):
        # The **kwargs are the options that were extracted by the
        # optionparser. A few rows down, they're used to update
        # self.__dict__, which *does* work, but providing a utility
        # that you can call from anywhere ought to be a bit
        # cleaner. And it prevents us from passing along this
        # generator all the time. [reinout]
        BaseGenerator.__init__(self)
        self.options = component.getUtility(IOptions, name='options')

        log.debug("Initializing ArchetypesGenerator. "
                  "We're being passed a file '%s' and keyword "
                  "arguments %r.", xschemaFileName, kwargs)
        self.xschemaFileName = xschemaFileName
        self.__dict__.update(kwargs)
        self._calcGlobalOptions()
        log.debug("Initialization finished.")

    def _calcGlobalOptions(self):
        outfilename = self.options.option('outfilename')
        log.debug("Outfilename is '%s'.",
                  outfilename)
        if outfilename:
            # Remove trailing delimiters on purpose
            if outfilename[-1] in ('/','\\'):
                outfilename = outfilename[:-1]
                log.debug("Stripped off the eventual trailing slashes: '%s'.",
                          outfilename)
            # Split off the parent directory part so that
            # we can call ArchgenXML.py -o /tmp/prod prod.xmi
            path = os.path.split(outfilename)
            targetRoot = path[0]
            log.debug("Targetroot is set to everything except the last "
                      "directory in the outfilename: %s.", targetRoot)
        else:
            log.debug("Outfilename hasn't been set. Setting "
                      "targetroot to the current directory.")
            targetRoot = '.'
        extraOptions = {}
        extraOptions['targetRoot'] = targetRoot
        extraOptions['outfilename'] = outfilename
        self.options.storeOptions(extraOptions)
        # Temporary old behaviour:
        self.targetRoot = targetRoot
        self.outfilename = outfilename

    def makeFile(self, fn, force=1, binary=0):
        return utils.makeFile(fn, force=force, binary=binary)

    def readFile(self,fn):
        ffn = os.path.join(self.targetRoot, fn)
        return utils.readFile(ffn)

    def makeDir(self, fn, force=1):
        log.debug("Calling makeDir to create '%s'.", fn)
        ffn = os.path.join(self.targetRoot, fn)
        log.debug("Together with the targetroot that means '%s'.", ffn)
        return utils.makeDir(ffn, force=force)

    def getSkinPath(self, element):
        fp = element.getRootPackage().getFilePath()
        mn = element.getRootPackage().getModuleName()
        return os.path.join(fp, 'skins', mn)

    def generateDependentImports(self, element):
        out = StringIO()
        res = BaseGenerator.generateDependentImports(self, element)
        print >> out, res
        print >> out, TEMPLATE_CMFDYNAMICVIEWFTI_IMPORT

        generate_expression_validator = False
        for att in element.getAttributeDefs():
            if att.getTaggedValue('validation_expression'):
                generate_expression_validator = True
        if generate_expression_validator:
            print >> out, 'from Products.validation.validators import ' + \
                          'ExpressionValidator'
        
        # Check for necessity to import DataGridField and DataGridWidget
        import_datagrid = False
        for att in element.getAttributeDefs():
            if att.getType() == 'datagrid':
                import_datagrid = True
                break

        if import_datagrid:
            print >>out, 'from Products.DataGridField import ' + \
                         'DataGridField, DataGridWidget'

        # Check for necessity to import ATColorPickerWidget
        import_color = False
        for att in element.getAttributeDefs():
            if att.getType() == 'color':
                import_color = True
                break

        if import_color:
            print >>out, 'from Products.ATColorPickerWidget.' + \
                         'ColorPickerWidget import ColorPickerWidget'

        # Check for necessity to import CountryWidget
        import_country = False
        for att in element.getAttributeDefs():
            if att.getType() == 'country':
                import_country = True
                break
        
        if import_country:
            print >>out, 'from Products.ATCountryWidget.Widget import ' + \
                         'CountryWidget'

        # Check for necessity to import ArrayField
        import_array_field = False
        for att in element.getAttributeDefs():
            if att.getUpperBound() != 1:
                import_array_field = True
                break

        if import_array_field:
            print >>out, 'from Products.CompoundField.ArrayField ' + \
                         'import ArrayField'

        start_marker = True
        for iface in self.getAggregatedInterfaces(element):
            if start_marker:
                print >>out, 'from Products.Archetypes.AllowedTypesByIface' + \
                             ' import AllowedTypesByIfaceMixin'
                start_marker = False
            print >>out, 'from %s import %s' % ( \
                         iface.getQualifiedModuleName(forcePluginRoot=True),
                         iface.getCleanName())

        if self.backreferences_support:
            print >>out, 'from Products.ATBackRef.BackReferenceField ' + \
                         'import BackReferenceField, BackReferenceWidget'
            
        return out.getvalue()

    def addMsgid(self, msgid, msgstr, element, fieldname):
        """Adds a msgid to the catalog if it not exists.

        If it exists and not listed in occurrences, then add its occurence.
        """
        log.debug("Add msgid %s" % msgid)
        msgid = utils.normalize(msgid)
        if has_i18ndude and self.build_msgcatalog and len(self.msgcatstack):
            msgcat = self.msgcatstack[len(self.msgcatstack)-1]
            package = element.getPackage()
            module_id = os.path.join( \
                            element.getPackage().getFilePath(includeRoot=0),
                            element.getName()+'.py')
            msgcat.add(msgid, msgstr=msgstr, references=[module_id])
    
    def getMethodActionsDict(self, element):
        log.debug("Generating method actions dict...")
        log.debug("First finding our methods.")
        
        ret = []
        
        for m in element.getMethodDefs():
            method_name = m.getName()
            code = utils.indent(m.getTaggedValue('code', ''), 1)
            if m.hasStereoType(['action', 'view', 'form'],
                               umlprofile=self.uml_profile):
                log.debug("Method has stereotype action/view/form.")
                action_name = m.getTaggedValue('action','').strip()
                if not action_name:
                    log.debug("No tagged value 'action', trying '%s' with a "
                              "default to the methodname.",
                              m.getStereoType())
                    action_name=m.getTaggedValue(m.getStereoType(),
                                                 method_name).strip()
                log.debug("Ok, generating %s for %s.",
                          m.getStereoType(), action_name)
                dict={}

                if not action_name.startswith('string:') \
                  and not action_name.startswith('python:'):
                    action_target='string:${object_url}/'+action_name
                else:
                    action_target=action_name

                dict['action'] = action_target
                dict['category'] = m.getTaggedValue('category', 'object')
                dict['id'] = m.getTaggedValue('id',method_name)
                dict['name'] = m.getTaggedValue('label',method_name)
                dict['permissions'] = m.getTaggedValue('permission', ['View'])

                condition=m.getTaggedValue('condition') or '1'
                dict['condition']='python:%s' % condition

                if not (m.hasTaggedValue('create_action') \
                  and utils.isTGVFalse(m.getTaggedValue('create_action'))):
                    #print >>outfile, ACT_TEMPL % dict
                    ret.append(dict)

            #LATER
            
            #if m.hasStereoType('view', umlprofile=self.uml_profile):
            #    f=self.makeFile(os.path.join(self.getSkinPath(element),action_name+'.pt'),0)
            #    if f:
            #        
            #        viewTemplate=open(os.path.join(self.templateDir,'action_view.pt')).read()
            #        f.write(viewTemplate % code)
            #
            #elif m.hasStereoType('form', umlprofile=self.uml_profile):
            #    f=self.makeFile(os.path.join(self.getSkinPath(element),action_name+'.cpt'),0)
            #    if f:
            #
            #        viewTemplate=open(os.path.join(self.templateDir,'action_view.pt')).read()
            #        f.write(viewTemplate % code)

        #res=outfile.getvalue()
        #return res
        return ret

    def generateAdditionalImports(self, element):
        outfile = StringIO()

        if element.hasAssocClass:
            print >> outfile,'from Products.Archetypes.ReferenceEngine ' + \
                             'import ContentReferenceCreator'

        useRelations = 0

        #check wether we have to import Relation's Relation Field
        for rel in element.getFromAssociations():
            if self.getOption('relation_implementation',
                              rel,
                              'basic') == 'relations':
                useRelations = 1

        for rel in element.getToAssociations():
            if self.getOption('relation_implementation',rel,'basic') == 'relations' and \
                (rel.getTaggedValue('inverse_relation_name') or rel.fromEnd.isNavigable) :
                useRelations = 1

        if useRelations:
            print >> outfile,'from Products.Relations.field import RelationField'

        if element.hasStereoType(self.variable_schema, umlprofile=self.uml_profile):
            print >> outfile,'from Products.Archetypes.VariableSchemaSupport import VariableSchemaSupport'

        # ATVocabularyManager imports
        if element.hasStereoType(self.vocabulary_item_stereotype, umlprofile=self.uml_profile):
            print >> outfile, 'from Products.ATVocabularyManager.tools import registerVocabularyTerm'
        if element.hasStereoType(self.vocabulary_container_stereotype, umlprofile=self.uml_profile):
            print >> outfile, 'from Products.ATVocabularyManager.tools import registerVocabulary'
        if self.getOption('vocabulary:type', element, None) == 'ATVocabularyManager' or \
           element.hasAttributeWithTaggedValue('vocabulary:type','ATVocabularyManager'):
            print >> outfile, 'from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary'

        if element.hasStereoType(self.atct_stereotype,
                                 umlprofile=self.uml_profile):
            log.debug("ATCT stereotype found, adding imports.")
            for stereotypeName in self.atct_stereotype:
                if element.hasStereoType(stereotypeName,
                                         umlprofile=self.uml_profile):
                    st = self.uml_profile.getStereoType(stereotypeName)
                    imports = st.get('imports', [])
                    for import_ in imports:
                        print >> outfile, import_

        return outfile.getvalue()


    def getImportsByTaggedValues(self, element):
        # imports by tagged values
        additionalImports=self.getOption('imports', element, default=None,
                                         aggregate=True)
        return additionalImports


    def generateModifyFti(self,element):
        hide_actions = element.getTaggedValue('hide_actions', '').strip()
        if not hide_actions:
            return ''

        # Also permit comma separation, since Poseidon doesn't like multi-line
        # tagged values and specifying multiple tagged values is a pain
        hide_actions = hide_actions.replace(',', '\n')

        hide_actions=', '.join(["'"+a.strip()+"'" for a in hide_actions.split('\n')])
        return MODIFY_FTI % {'hideactions':hide_actions, }
        
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
                  'widget','copy_from','source_name']
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

        # check for global settings
        searchable = self.getOption('searchable', element, default = _marker)
        if searchable is not _marker:
             tgv.update({'searchable': searchable})
        index = self.getOption('index', element, default=_marker)
        if index is not _marker:
             tgv.update({'index': index})

        # set attributes from tgv
        for k in tgv.keys():
            if k not in noparams and not k.startswith('widget:'):
                v = tgv[k]
                if v is None:
                    log.warn(u"Empty tagged value for tag '%s' in field '%s'.",
                             k, element.getName())
                    continue
                if type(v) in StringTypes:
                    v = v.decode('utf8')
                    if k not in self.nonstring_tgvs:
                        v=utils.getExpression(v)
                    # [optilude] Permit python: if people forget they
                    # don't have to (I often do!)
                    else:
                        if v.startswith('python:'):
                            v = v[7:]

                map.update({k: v})
        return map

    def getWidget(self, widgettype, element, fieldname, elementclass, fieldclassname=None):
        """ returns either default widget, widget according to
        attributes or no widget.

        atributes/tgv's can be:
            * widget and a whole widget code block or
            * widget:PARAMETER which will be rendered as a PARAMETER=value

        """
        tgv = element.getTaggedValues()
        widgetcode = widgettype.capitalize()+'Widget'
        widgetmap = odict()
        custom = False # is there a custom setting for widget?
        widgetoptions = [t for t in tgv.items() if t[0].startswith('widget:')]

        # check if a global default overrides a widget. setting defaults is
        # provided through getOption.
        # to set an default just put:
        # default:widget:widgettype = widgetname
        # as a tagged value on the package or model
        if hasattr(element,'widgettype') and element.type != 'NoneType':
            atype = element.type
        else:
            atype = widgettype
        default_widget = self.getOption('default:widget:%s' % fieldclassname, element, None)
        if not default_widget:
            default_widget = self.getOption('default:widget:%s' % atype, element, None)
        
        if default_widget:
            widgetcode = default_widget + u'(\n'

        modulename = elementclass.getPackage().getProductName()
        check_map = odict()
        check_map['label']              = u"'%s'" % fieldname.capitalize().decode('utf8')
        check_map['label_msgid']        = u"'%s_label_%s'" % (modulename, utils.normalize(fieldname, 1))
        check_map['description_msgid']  = u"'%s_help_%s'" % (modulename, utils.normalize(fieldname, 1))
        check_map['i18n_domain']        = u"'%s'" % modulename

        wt = {} # helper

        if tgv.has_key('widget'):
            # Custom widget defined in attributes
            custom = True
            formatted = u''
            for line in tgv['widget'].split(u'\n'):
                if formatted:
                    line = utils.indent(line.strip(), 1)
                formatted += u"%s\n" % line
            widgetcode =  formatted

        elif [wt.update({t[0]:t[1]}) for t in widgetoptions if t[0] == u'widget:type']:
            custom = True
            widgetcode = wt['widget:type']
        
        elif self.widgetMap.has_key(widgettype) and not default_widget:
            # default widget for this widgettype found in widgetMap
            custom = True
            widgetcode = self.widgetMap[widgettype]

        elif fieldclassname and not default_widget:
            # use fieldclassname if and only if no default widget has been given
            widgetcode="%s._properties['widget'](\n" % fieldclassname

        if ')' not in widgetcode: # XXX bad check *sigh*

            for tup in widgetoptions:
                key=tup[0][7:]
                val=tup[1]
                if key == 'type':
                    continue
                if key not in self.nonstring_tgvs:
                    val=utils.getExpression(val)
                    # [optilude] Permit python: if people forget they don't have to (I often do!)
                else:
                    if type(val) in StringTypes:
                        if val.startswith('python:'):
                            val = val[7:]

                widgetmap.update({key:val})

            if '(' not in widgetcode:
                widgetcode += '(\n'

            ## before update the widget mapping, try to make a
            ## better description based on the given label

            for k in check_map:
                if not (k in widgetmap.keys()): # XXX check if disabled
                    widgetmap.update( {k: check_map[k]} )

            # remove description_msgid if there is no description
            if 'description' not in widgetmap.keys() and \
               'description_msgid' in widgetmap.keys(): 
                del widgetmap['description_msgid']

            if 'label_msgid' in widgetmap.keys() and has_enhanced_strip_support:
                self.addMsgid(widgetmap['label_msgid'].strip("'").strip('"'),
                    widgetmap.has_key('label') and widgetmap['label'].strip("'").strip('"') or fieldname,
                    elementclass,
                    fieldname
                )
            if 'description_msgid' in widgetmap.keys() and has_enhanced_strip_support:
                self.addMsgid(widgetmap['description_msgid'].strip("'").strip('"'),
                    widgetmap.has_key('description') and widgetmap['description'].strip("'").strip('"') or fieldname,
                    elementclass,
                    fieldname
                )
            keqvs = list()
            for key in widgetmap:
                value = widgetmap[key]
                if (type(value) != types.UnicodeType
                    and type(value) in StringTypes):
                    # StringTypes filters out integer values
                    value = value.decode('utf-8')
                keqv = u'%s=%s' % (key, value)
                keqvs.append(keqv)

            widgetcode += utils.indent( \
                u',\n'.join(keqvs),
                1,
                skipFirstRow=0) \
                + u',\n'
            widgetcode += u')'

        return widgetcode

    def getFieldFormatted(self, name, fieldtype, map={}, doc=None,
                          indent_level=0, rawType='String', array_field=False):
        """Return the a formatted field definition for the schema.
        """

        log.debug("Trying to get formatted field. name='%s', fieldtype='%s', "
                  "doc='%s', rawType='%s'.", name, fieldtype, doc, rawType)
	name = utils.normalize(name, 1)
        res = u''
        if array_field:
            array_options={}
            for key in map.keys():
                if key.startswith(u'array:'):
                    nkey=key[len(u'array:'):]
                    array_options[nkey]=map[key]
                    del map[key]
            
        # Capitalize only first letter of fields class name, keep camelcase
        a = rawType[0].upper()
        rawType = a + rawType[1:]

        # Add comment
        if doc:
            res += utils.indent(doc, indent_level, u'#') + u'\n' + res

        # If this is a generic field and the user entered MySpecialField,
        # then don't suffix it with 'field''
        if rawType.endswith(u'Field'):
            rawType = rawType[:-5]

        res += utils.indent(u"%s(\n    name='%s',\n" % (
                   fieldtype % {'type': rawType}, name), indent_level)
        if map:
            prepend = utils.indent(u'', indent_level)
            for key in map:
                if key.find(u':') >= 0:
                    continue
                lines = map[key]
                if isinstance(lines, basestring):
                    linebreak = lines.find(u'\n')

                    if linebreak < 0:
                        linebreak = len(lines)
                    firstline = lines[:linebreak]
                else:
                    firstline = lines

                res += u'%s%s=%s' % (prepend, key, firstline)
                if isinstance(lines, basestring) and linebreak < len(lines):
                    for line in lines[linebreak+1:].split(u'\n'):
                        line = utils.indent(line, indent_level + 1)
                        res += u"\n%s" % line

                prepend = u',\n%s' % utils.indent('', indent_level +1)

        res += u'\n%s' % utils.indent(u'),', indent_level) + u'\n\n'

        if array_field:
            res = res.strip()
            if array_options.get('widget', None):
                if array_options['widget'].find('(') == -1:
                    array_options['widget'] += u'()'

            array_defs = u',\n'.join([u"%s=%s" % item for item in array_options.items()])
            res =  ARRAYFIELD % ( utils.indent(res, 2), utils.indent(array_defs, 2) ) 
            
        return res

    def getFieldsFormatted(self, field_specs):
        """Return the formatted field definitions for the schema from field_specs.
        """
        res = u''
        for field_spec in field_specs:
            log.debug("field_spec is %r.",
                      field_spec)
            try:
                # The following is needed to work around a bug in Sunew's
                # array_field fix. Apparently associations don't have the
                # rawType key. Should be fixed elsewhere, though.
                if type(field_spec) in StringTypes:
                    # need this for copied fields
                    res += field_spec
                elif (field_spec.has_key('rawType') and
                    field_spec.has_key('array_field')):
                    res += self.getFieldFormatted(field_spec['name'], 
                                                  field_spec['fieldtype'],
                                                  field_spec['map'],
                                                  field_spec['doc'],
                                                  field_spec['indent_level'],
                                                  field_spec['rawType'],
                                                  field_spec['array_field'],
                                                  )
                else:
                    res += self.getFieldFormatted(field_spec['name'], 
                                                  field_spec['fieldtype'],
                                                  field_spec['map'],
                                                  field_spec['doc'],
                                                  field_spec['indent_level']
                                                  )
            except Exception, e:
                log.critical("Couldn't render fields from field_specs: '%s'.",
                             field_specs)
                raise
        return res

    def getFieldSpec(self, element, classelement, indent_level=0):
        """Gets the schema field code."""
        typename = element.type
        ctype = self.coerceType(typename)
        map = typeMap[ctype]['map'].copy()
        res= {'name': element.getCleanName(),
              'fieldtype': self.typeMap[ctype]['field'].copy(),
              'map': map,
              'indent_level': indent_level}
        return res

    def addVocabulary(self, element, attr, map):
        # ATVocabularyManager: Add NamedVocabulary to field.
        vocaboptions = {}
        for t in attr.getTaggedValues().items():
            if t[0].startswith('vocabulary:'):
                vocaboptions[t[0][11:]] = t[1]
        if vocaboptions:
            if not 'name' in vocaboptions.keys():
                vocaboptions['name'] = '%s_%s' % (element.getCleanName(), \
                                                  attr.getName())
            if not 'term_type' in vocaboptions.keys():
                vocaboptions['term_type'] = self.getOption('vocabulary:term_type', attr, 'SimpleVocabularyTerm')

            if not 'vocabulary_type' in vocaboptions.keys():
                vocaboptions['vocabulary_type'] = self.getOption('vocabulary:vocabulary_type', attr, 'SimpleVocabulary')

            if not 'type' in vocaboptions.keys():
                vtype = self.getOption('vocabulary:type', attr, None)
                if vtype:
                    vocaboptions['type'] = vtype

            map.update({
                'vocabulary':'NamedVocabulary("""%s""")' % vocaboptions['name']
            })

            # remember this vocab-name and if set its portal_type
            package = element.getPackage()
            currentproduct = package.getProductName()
            if not currentproduct in self.vocabularymap.keys():
                self.vocabularymap[currentproduct] = {}

            if not vocaboptions['name'] in self.vocabularymap[currentproduct].keys():
                self.vocabularymap[currentproduct][vocaboptions['name']] = (
                                                vocaboptions['vocabulary_type'],
                                                vocaboptions['term_type'])
            else:
                log.warn("Vocabulary with name '%s' defined more than once.",
                         vocaboptions['name'])

        # end ATVM

    def getFieldSpecFromAttribute(self, attr, classelement, indent_level=0):
        """Gets the schema field code."""

        if not hasattr(attr, 'type') or attr.type == 'NoneType':
            ctype = 'string'
        else:
            ctype = self.coerceType(attr.type)

        if ctype=='copy':
            name = getattr(attr, 'rename_to', attr.getName())
            field = "    copied_fields['%s'],\n\n" % name
            return field

        map = self.typeMap[ctype]['map'].copy()
        if attr.hasDefault():
            map.update({'default': utils.getExpression(attr.getDefault())})
        map.update(self.getFieldAttributes(attr))

        atype = self.typeMap[ctype]['field']

        if ctype=='generic':
            fieldclassname=attr.type            
        else:
            fieldclassname=atype

        widget = self.getWidget(ctype, attr, attr.getName(), classelement, fieldclassname=fieldclassname)

        if not widget.startswith('GenericWidget'):
            map.update({'widget': widget})

        self.addVocabulary(classelement, attr, map)

        doc=attr.getDocumentation(striphtml=self.strip_html)

        if attr.hasTaggedValue('validators'):
            #make validators to a list in order to append the ExpressionValidator
            val = attr.getTaggedValue('validators')
            try:
                map['validators'] = tuple(eval(val))
            except:
                map['validators'] = tuple(val.split(','))

        if map.has_key('validation_expression'):
            #append the validation_expression to the validators
            expressions = attr.getTaggedValue('validation_expression').split('\n')
            errormsgs = attr.getTaggedValue('validation_expression_errormsg').split('\n')
            if errormsgs and errormsgs != [''] \
               and len(errormsgs) != len(expressions):
                log.critical('validation_expression and validation_expression_'
                             'errormsg tagged value must have the same size '
                             '(%s, %s)' %(expressions,errormsgs))
            def corresponding_error(errormsgs, ind):
                if errormsgs and errormsgs != ['']:
                    return ", '"+errormsgs[ind]+"'"
                return ""
            expval = ["""ExpressionValidator('''python:%s'''%s)""" %
                      (expression,corresponding_error(errormsgs,exp_index))
                      for exp_index,expression in enumerate(expressions)]

            if map.has_key('validators'):
                map['validators'] = repr(map.get('validators',())) + \
                                    '+('+','.join(expval)+',)'
            else:
                map['validators'] = '(' + ','.join(expval) + ',)'

            del map['validation_expression']
            if map.has_key('validation_expression_errormsg'):
                del map['validation_expression_errormsg']

        res={'name':attr.getName(),
            'fieldtype':atype,
            'map':map,
            'doc':doc,
            'indent_level':indent_level,
            'rawType':attr.getType(),
            'array_field':attr.getUpperBound() != 1}

        return res

    def getFieldSpecFromAssociation(self, rel, classelement, indent_level=0):
        """Return the schema field code."""

        log.debug("Getting the field string from an association.")
        multiValued = 0
        obj = rel.toEnd.obj
        name = rel.toEnd.getName()
        relname = rel.getName()
        log.debug("Endpoint name: '%s'.", name)
        log.debug("Relationship name: '%s'.", relname)

        if obj.isAbstract():
            allowed_types= tuple(obj.getGenChildrenNames())
        else:
            try:
                isFlavor = obj.hasStereotype('flavor', umlprofile=self.uml_profile)
            except AttributeError:
                isFlavor = False
            if isFlavor == True:
                allowed_types=tuple(obj.getRealizationChildrenNames(recursive=True))
            else:
                allowed_types=(obj.getName(),) + tuple(obj.getGenChildrenNames())

        if int(rel.toEnd.mult[1]) == -1:
            multiValued = 1
        if name == None:
            name = obj.getName()+'_ref'

        if self.getOption('relation_implementation', rel, 'basic') == 'relations':
            log.debug("Using the 'relations' relation implementation.")
            # The relation can override the field
            field = self.getOption('reference_field',rel,None) or \
                    rel.getTaggedValue('reference_field') or \
                    rel.toEnd.getTaggedValue('reference_field') or \
                    rel.getTaggedValue('field') or \
                    rel.toEnd.getTaggedValue('field') or \
                    self.typeMap['relation']['field']
            # TBD: poseidon reference-as-field handling or so...
            if not field:
                message = "Somehow we couldn't get at the fieldname. " \
                          "Use normal drawn associations instead of " \
                          "a named reference."
                log.critical(message)
                raise message

            map = self.typeMap['relation']['map'].copy()
            map.update({'multiValued': multiValued,
                        'relationship': "'%s'" % relname})
            map.update(self.getFieldAttributes(rel.toEnd))
            map.update({'widget': self.getWidget('Reference', rel.toEnd,
                                                 name, classelement)})
        else:
            log.debug("Using the standard relation implementation.")
            # The relation can override the field
            field = rel.getTaggedValue('reference_field') or \
                    rel.toEnd.getTaggedValue('reference_field') or \
                    self.typeMap['reference']['field']
            # TBD: poseidon reference-as-field handling or so...
            if not field:
                message = "Somehow we couldn't get at the fieldname. " \
                          "Use normal drawn associations instead of " \
                          "a named reference."
                log.critical(message)
                raise message
            map = self.typeMap['reference']['map'].copy()
            map.update({'allowed_types': repr(allowed_types),
                        'multiValued': multiValued,
                        'relationship': "'%s'" % relname})
            map.update(self.getFieldAttributes(rel.toEnd))
            map.update({'widget':self.getWidget('Reference', rel.toEnd,
                                                name, classelement)})

            if getattr(rel,'isAssociationClass',0):
                # Association classes with stereotype "stub" and tagged
                # value "import_from" will not use ContentReferenceCreator
                if rel.hasStereoType(self.stub_stereotypes,
                                     umlprofile=self.uml_profile) :
                    map.update({'referenceClass':"%s" % rel.getName()})
                    # do not forget the import!!!
                else:
                    map.update({'referenceClass':"ContentReferenceCreator('%s')"
                                % rel.getName()})

        doc=rel.getDocumentation(striphtml=self.strip_html)
        res={'name':name,
            'fieldtype':field,
            'map':map,
            'doc':doc,
            'indent_level':indent_level}
        return res

    def getFieldSpecFromBackAssociation(self, rel, classelement, indent_level=0):
        """Gets the schema field code"""
        multiValued = 0
        obj = rel.fromEnd.obj
        name = rel.fromEnd.getName()
        relname = rel.getName()

        if obj.isAbstract():
            allowed_types= tuple(obj.getGenChildrenNames())
        else:
            allowed_types=(obj.getName(),) + tuple(obj.getGenChildrenNames())

        if int(rel.fromEnd.mult[1]) == -1:
            multiValued = 1
        if name == None:
            name = obj.getName() + '_ref'

        if self.getOption('relation_implementation', rel, 'basic') == \
           'relations'  and (rel.fromEnd.isNavigable or \
           rel.getTaggedValue('inverse_relation_name')):
            # The relation can override the field
            field = rel.getTaggedValue('relation_field') or \
                    rel.getTaggedValue('field') or \
                    rel.fromEnd.getTaggedValue('field') or \
                    self.typeMap['relation']['field']
            map = self.typeMap['relation']['map'].copy()
            backrelname = rel.getInverseName()
            map.update({'multiValued': multiValued,
                        'relationship': "'%s'" % backrelname})
            map.update(self.getFieldAttributes(rel.fromEnd))
            map.update({'widget':self.getWidget('Reference', rel.fromEnd,
                                                name, classelement)} )
        else:
            # The relation can override the field
            field = rel.getTaggedValue('reference_field') or \
                    rel.toEnd.getTaggedValue('back_reference_field') or \
                    self.typeMap['backreference']['field']
            map = self.typeMap['backreference']['map'].copy()
            if rel.fromEnd.isNavigable and (self.backreferences_support or \
               self.getOption('backreferences_support', rel, '0') == '1'):
                map.update({'allowed_types': repr(allowed_types),
                            'multiValued': multiValued,
                            'relationship': "'%s'" % relname})
                map.update(self.getFieldAttributes(rel.fromEnd))
                map.update({'widget':self.getWidget('BackReference', rel.fromEnd,
                                                    name, classelement)})

                if getattr(rel,'isAssociationClass',0):
                    map.update({'referenceClass': "ContentReferenceCreator('%s')"
                                % rel.getName()})
            else:
                return None

        doc = rel.getDocumentation(striphtml=self.strip_html)
        res={'name':name,
            'fieldtype':field,
            'map':map,
            'doc':doc,
            'indent_level':indent_level}
        return res

    def getLocalFieldSpecs(self, element, indent_level=0):
        field_specs = []
        aggregatedClasses = []

        for attrDef in element.getAttributeDefs():
            name = attrDef.getName()
            #if name in self.reservedAtts:
            #    continue
            mappedName = utils.mapName(name)

            field_specs.append(self.getFieldSpecFromAttribute(attrDef, element,
                                                    indent_level=indent_level+1))

        for child in element.getChildren():
            name = child.getCleanName()
            if name in self.reservedAtts:
                continue
            unmappedName = child.getUnmappedCleanName()
            if child.getRef():
                aggregatedClasses.append(str(child.getRef()))

            if child.isIntrinsicType():
                field_specs.append(self.getFieldSpec(child, element,
                                                    indent_level=indent_level+1))

        # only add reference fields if tgv generate_reference_fields
        if utils.toBoolean(
                self.getOption('generate_reference_fields', element, True) ):
            #print 'rels:',element.getName(),element.getFromAssociations()
            # and now the associations
            for rel in element.getFromAssociations():
                name = rel.fromEnd.getName()
                end=rel.fromEnd

                #print 'generating from assoc'
                if name in self.reservedAtts:
                    continue
                field_specs.append(self.getFieldSpecFromAssociation(rel,
                                                    element,
                                                    indent_level=indent_level+1))

            #Back References
            for rel in element.getToAssociations():
                name = rel.fromEnd.getName()

                #print "backreference"
                if name in self.reservedAtts:
                    continue
                fc=self.getFieldSpecFromBackAssociation(rel,
                                                    element,
                                                    indent_level=indent_level+1)
                if fc:
                    field_specs.append(fc)

        return field_specs

    # Generate get/set/add member functions.
    def generateArcheSchema(self, element, field_specs, base_schema=None, 
                            outfile=None):
        """ generates the Schema """
        asString = False
        if outfile is None:
            outfile = StringIO()
            asString = True
        # first copy fields from other schemas if neccessary.
        startmarker = True
        for attr in element.getAttributeDefs():
            if attr.type.lower() == 'copy':
                if startmarker:
                    startmarker=False
                    print >> outfile, 'copied_fields = {}'
                copyfrom = attr.getTaggedValue('copy_from', base_schema)
                name = attr.getTaggedValue('source_name',attr.getName())
                print >> outfile, "copied_fields['%s'] = %s['%s'].copy(%s)" % \
                         (attr.getName(), copyfrom, name, name!=attr.getName() \
                         and ("name='%s'" % attr.getName()) or '')
                map = self.getFieldAttributes(attr)
                for key in map:
                    if key.startswith('move:'):
                        continue
                    print >>outfile, "copied_fields['%s'].%s = %s" % \
                                     (attr.getName(), key, map[key])
                tgv = attr.getTaggedValues()
                for key in tgv.keys():
                    if not key.startswith('widget:'):
                        continue
                    if key not in self.nonstring_tgvs:
                        tgv[key]=utils.getExpression(tgv[key])
                    print >>outfile, "copied_fields['%s'].widget.%s = %s" % \
                                     (attr.getName(), key[7:], tgv[key])
                    # add pot msgid if necessary
                    widgetkey = key[7:]
                    widgetvalue = tgv[key]
                    fieldname = attr.getName()
                    if widgetkey=='label_msgid':
                        self.addMsgid(widgetvalue.strip("'").strip('"'),
                                      tgv.has_key('widget:label') and
                                      tgv['widget:label'].strip("'").strip('"')
                                      or fieldname, element, fieldname)
                    if widgetkey=='description_msgid':
                        self.addMsgid(widgetvalue.strip("'").strip('"'),
                                      tgv.has_key('widget:description') and
                                      tgv['widget:description'].strip("'").strip('"')
                                      or fieldname, element, fieldname)

        fieldsformatted = self.getFieldsFormatted(field_specs) + u'),'        
        print >> outfile, SCHEMA_START
        print >> outfile, fieldsformatted.encode('utf8')

        marshaller=element.getTaggedValue('marshaller')
        # deprecated tgv 'marschall' here, that's a duplicate
        if marshaller:
            print >> outfile, 'marshall='+marshaller

        print >> outfile, ')\n'
        if asString:
            return outfile.getvalue()

    def generateFieldMoves(self, outfile, schemaName, field_specs):
        """Generate moveField statements for the schema from field_specs.
        """

        for field_spec in field_specs:
            if type(field_spec) in StringTypes or \
               not field_spec.has_key('map'): 
                continue
            for key in field_spec['map'].keys():
                if key.startswith('move:'):
                    move_key = key[5:]
                    move_from = field_spec['name']
                    move_to = field_spec['map'][key]
                    if move_key == 'before':
                        print >> outfile, "%s.moveField('%s', before=%s)" % (schemaName, move_from, move_to)
                    elif move_key == 'after':
                        print >> outfile, "%s.moveField('%s', after=%s)" % (schemaName, move_from, move_to)
                    elif move_key == 'top' and move_to: # must be true
                        print >> outfile, "%s.moveField('%s', pos='top')" % (schemaName, move_from)
                    elif move_key == 'bottom' and move_to: # must be true
                        print >> outfile, "%s.moveField('%s', pos='bottom')" % (schemaName, move_from)
                    elif move_key == 'pos':
                        print >> outfile, "%s.moveField('%s', pos=%s)" % (schemaName, move_from, move_to)

        print >> outfile

    def generateMethods(self, outfile, element, mode='class'):
        print >> outfile,'    # Methods'

        generatedMethods = []
        allmethnames = [m.getName() for m in element.getMethodDefs(recursive=1)]

        for m in element.getMethodDefs():
            self.generateMethod(outfile, m, element, mode=mode)
            allmethnames.append(m.getName())
            generatedMethods.append(m)

        for interface in element.getRealizationParents():
            meths = [m for m in interface.getMethodDefs(recursive=1)
                     if m.getName() not in allmethnames]
            # Filter out doubles.
            # That can happen if two interfaces both have the same method.
            uniqueMethods = {}
            for method in meths:
                name = method.getName()
                uniqueMethods[name] = method
            meths = uniqueMethods.values()
            # We don't want to extra generate methods
            # that are already defined in the class
            if meths:
                print >> outfile, '\n    # Methods from Interface %s' % \
                      interface.getName()
                for m in meths:
                    self.generateMethod(outfile, m, element, mode=mode)
                    allmethnames.append(m.getName())
                    generatedMethods.append(m)

        # Contains _all_ generated method names
        method_names = [m.getName() for m in generatedMethods]

        #if __init__ has to be generated for tools i want _not_ __init__ to be preserved
        #if it is added to method_names it wont be recognized as a manual method (hacky but works)
        if element.hasStereoType(self.portal_tools, umlprofile=self.uml_profile) and '__init__' not in method_names:
            method_names.append('__init__')

        # As above .. 
        if element.hasStereoType(
                self.remember_stereotype,
                umlprofile=self.uml_profile) and '__call__' not in method_names:
            method_names.append('__call__') 

        #as __init__ above if at_post_edit_script has to be generated for tools
        #I want _not_ at_post_edit_script to be preserved (hacky but works)
        #if it is added to method_names it wont be recognized as a manual method
        if element.hasStereoType(self.portal_tools, umlprofile=self.uml_profile) \
           and 'at_post_edit_script' not in method_names:
            method_names.append('at_post_edit_script')

        log.debug("We are to preserve methods, so we're looking for manual methods.")
        cl = self.parsed_class_sources.get(element.getPackage().getFilePath()+'/'+element.name, None)
        if cl:
            log.debug("The class has the following methods: %r.", cl.methods.keys())
            manual_methods = [mt for mt in cl.methods.values() if mt.name not in method_names]
            manual_methods.sort(lambda a,b: cmp(a.start, b.start))  # sort methods according to original order
            log.debug("Found the following manual methods: %r.", manual_methods)
            if manual_methods:
                print >> outfile, '\n    # Manually created methods\n'

            for mt in manual_methods:
                declaration = cl.getProtectionDeclaration(mt.getName())
                if declaration:
                    print >> outfile, declaration
                print >> outfile, mt.src
            print >> outfile

    def generateMethod(self, outfile, m, klass, mode='class'):
        #ignore actions and views here because they are generated separately
        if m.hasStereoType(['action', 'view', 'form'], 
                           umlprofile=self.uml_profile):
            return

        wrt = outfile.write
        paramstr = ''
        params = m.getParamExpressions()
        if params:
            paramstr = ',' + ','.join(params)

        print >> outfile

        if mode == 'class':
            declaration = self.generateMethodSecurityDeclaration(m)
            if declaration:
                print >> outfile, declaration

        cls = self.parsed_class_sources.get(klass.getPackage().getFilePath() +
                                            '/' + klass.getName(), None)
        if cls:
            method_code = cls.methods.get(m.getName())
        else:
            method_code = None

        if method_code:            
            wrt(method_code.src.encode('utf8'))
            # Holly hack: methods ending with a 'pass' command doesn't have
            # an extra blank line after reparsing the code, so we add it
            if method_code.src.split('\n')[-1].strip() == 'pass':
                print >> outfile
        else:
            if mode=='class':
                print >> outfile, '    def %s(self%s):' % (m.getName(), paramstr)
            elif mode=='interface':
                print >> outfile, '    def %s(%s):' % (m.getName(), paramstr[1:])

            code = m.taggedValues.get('code', '')
            doc = m.getDocumentation(striphtml=self.strip_html)
            if doc is not None:
                print >> outfile, utils.indent('"""%s\n"""' % doc, 2,
                                               stripBlank=True)
            if code and mode == 'class':
                print >> outfile, utils.indent('\n'+code, 2)
            else:
                print >> outfile, utils.indent('pass', 2)

        if m.isStatic():
            print >> outfile, '    %s = staticmethod(%s)\n' % (m.getName(),m.getName())

    ## Generate Functional base testcase class.
    #
    # This method generates the python class that is the base class for function - 
    # broswer based - testcases.  This entails insuring that the 
    # runallfunctionaltests.py files exist, then generating the base class itself.
    #
    # @param self The object pointer.
    # @param element The XMI element that is being generated.
    # @param template The template file to use in generating the output.
    def generateBaseFunctionalTestcaseClass(self,element,template):
        log.debug('write testFunctional.py, only if needed.')

        if not os.path.exists(os.path.join(self.targetRoot, element.getPackage().getFilePath(),'testFunctional.py')):
            file=self.readTemplate('tests/testFunctional.py')
            of=self.makeFile(os.path.join(element.getPackage().getFilePath(),'testFunctional.py'))
            of.write(file)
            of.close()

        log.debug('generate base functional testcase class')
        return self.generateFunctionalTestcaseClass(element,template)
    
    def generateBaseTestcaseClass(self,element,template):
        log.debug('write runalltests.py and framework.py')
        runalltests=self.readTemplate('tests/runalltests.py')
        framework=self.readTemplate('tests/framework.py')

        log.debug('generate base testcase class')
        of=self.makeFile(os.path.join(element.getPackage().getFilePath(),'runalltests.py'))
        of.write(runalltests)
        of.close()

        of=self.makeFile(os.path.join(element.getPackage().getFilePath(),'framework.py'))
        of.write(framework)
        of.close()

        return self.generateTestcaseClass(element,template)

    def generateDocTestcaseClass(self,element,template ):
        #write runalltests.py and framework.py
        testdoc_t=self.readTemplate('tests/testdoc.txt')
        testdoc=HTML(testdoc_t,{'klass':element })()


        testname=element.getTaggedValue('doctest_name') or element.getCleanName()
        self.makeDir(os.path.join(element.getPackage().getProduct().getFilePath(),
                                  'doc'))
        docfile=os.path.join(element.getPackage().getProduct().getFilePath(),
                             'doc', '%s.txt' % testname)
        if not self.readFile(docfile):
            of=self.makeFile(docfile)
            of.write(testdoc)
            of.close()

        init='#'
        of=self.makeFile(os.path.join(element.getPackage().getProduct().getFilePath(),
                                      'doc', '__init__.py' ))

        of.write(init)
        of.close()


        return self.generateTestcaseClass(element,template,testname=testname)

    ##
    #
    def generateFunctionalTestcaseClass(self, element, template, **kw):
        log.info("%sGenerating testcase '%s'.", '    '*self.infoind, 
                 element.getName())

        assert element.hasStereoType('plonefunctional_testcase', 
                                     umlprofile=self.uml_profile) or \
                                     element.getCleanName().startswith('browser'), \
               "names of test classes _must_ start with 'browser', but this class is named '%s'" % element.getCleanName()

        assert element.getPackage().getCleanName() == 'tests', \
            "testcase classes only make sense inside a package called 'tests' \
                 but this class is named '%s' and located in package '%s'" % \
                 (element.getCleanName(),element.getPackage().getCleanName())

        if element.getGenParents():
            parent = element.getGenParents()[0]
        else:
            parent = None

        return BaseGenerator.generatePythonClass(self, element, template, 
                                                 parent=parent, nolog=True, 
                                                 **kw)
        
    def generateTestcaseClass(self, element, template, **kw):
        log.info("%sGenerating testcase '%s'.", '    ' * self.infoind, 
                 element.getName())

        assert element.hasStereoType('plone_testcase', 
                                     umlprofile=self.uml_profile) or \
                                     element.getCleanName().startswith('test'), \
               "names of test classes _must_ start with 'test', but this class is named '%s'" % element.getCleanName()

        assert element.getPackage().getCleanName() == 'tests', \
            "testcase classes only make sense inside a package called 'tests' \
                 but this class is named '%s' and located in package '%s'" % \
                 (element.getCleanName(),element.getPackage().getCleanName())

        if element.getGenParents():
            parent = element.getGenParents()[0]
        else:
            parent = None

        return BaseGenerator.generatePythonClass(self, element, template, 
                                                 parent=parent, nolog=True, 
                                                 **kw)

    def generateWidgetClass(self, element, template, zptname='widget.pt'):
        log.info("%sGenerating widget '%s'.",
                 "    "*self.infoind, element.getName())

        # Generate the template
        macroname = '%s.pt' % element.getTaggedValue('macro',
                                                     element.getCleanName())
        templpath = os.path.join(self.getSkinPath(element), macroname)
        fieldpt = self.readFile(templpath)
        if not fieldpt:
            templ = self.readTemplate(zptname)
            d = {
                'klass': element,
                'generator': self,
                'parsed_class': element.parsed_class,
                'builtins': __builtins__,
                'utils': utils,
            }
            d.update(__builtins__)
            zptcode = HTML(templ,d)()

            fp = self.makeFile(templpath)
            print >> fp, zptcode
            fp.close()

        # And now the python code
        if element.getGenParents():
            parent = element.getGenParents()[0]
            parentname = parent.getCleanName()
        else:
            parent = None
            parentname = 'TypesWidget'

        return BaseGenerator.generatePythonClass(self, element, template,
                                                 parent=parent,
                                                 parentname=parentname)

    def generateFieldClass(self, element, template):
        log.info("%sGenerating field: '%s'.",
                 '    '*self.infoind, element.getName())

        # Generate the python code
        if element.getGenParents():
            parent = element.getGenParents()[0]
            parentname = parent.getCleanName()
        else:
            if element.getAttributeDefs():
                parent = None
                parentname = 'CompoundField'
            else:
                parent = None
                parentname = 'ObjectField'

        widgets = element.getClientDependencyClasses(targetStereotypes=['widget'])
        if widgets:
            widget = widgets[0]
            widgetname = widget.getCleanName()
        else:
            widget = None
            widgetname = None
        klass = BaseGenerator.generatePythonClass(self, element, template,
                                                  parent=parent,
                                                  parentname=parentname,
                                                  widget=widget,
                                                  widgetname=widgetname)
        return klass

    def elementIsFolderish(self, element):
        log.debug("Determining whether the element '%s' is folderish...",
                  element.name)
        # This entire method hould probably be moved off to the element classes.
        # Copy-pasted from generateArchetypesClass()...
        aggregatedClasses = element.getRefs() + \
                            element.getSubtypeNames(recursive=0,filter=['class'])
        log.debug("Found %s aggregated classes.",
                  len(aggregatedClasses))
        #also check if the parent classes can have subobjects
        baseaggregatedClasses=[]
        for b in element.getGenParents():
            baseaggregatedClasses.extend(b.getRefs())
            baseaggregatedClasses.extend(b.getSubtypeNames(recursive=1))
        log.debug("Found %s parents with aggregated classes.",
                  len(baseaggregatedClasses))
        aggregatedInterfaces=self.getAggregatedInterfaces(element, includeBases=1)
        log.debug("Found %s aggregated interfaces.",
                  len(aggregatedInterfaces))
        log.debug("Based on this info and the tagged value 'folderish' or the "
                  "stereotypes 'folder' and 'ordered', we look if it's a folder.")
        isFolderish = aggregatedInterfaces or aggregatedClasses or \
                      baseaggregatedClasses or \
                      element.hasStereoType(self.folder_stereotype, 
                                            umlprofile=self.uml_profile)
        log.debug("End verdict on folderish character: %s.",
                  bool(isFolderish))
        return bool(isFolderish)

    def getAggregatedInterfaces(self,element,includeBases=1):
        res = element.getAggregatedClasses(recursive=0,filter=['interface'])
        if includeBases:
            for b in element.getGenParents(recursive=1):
                res.extend(self.getAggregatedInterfaces(b,includeBases=0))

        return res

    def getArchetypesBase(self, element, parentnames, parent_is_archetype):
        """ find bases (baseclass and baseschema) and return a
            3-tuple (baseclass, baseschema, parentnames)

            Normally a one of the Archetypes base classes are set.
            if you dont want it set the TGV to zero '0'
        """
        if self.elementIsFolderish(element):
            # folderish

            if element.hasStereoType('ordered', umlprofile=self.uml_profile):
                baseclass ='OrderedBaseFolder'
                baseschema ='OrderedBaseFolderSchema'
            elif element.hasStereoType(['large','btree'],
                                       umlprofile=self.uml_profile):
                baseclass ='BaseBTreeFolder'
                baseschema ='BaseBTreeFolderSchema'
            elif element.hasStereoType(['atfolder'],
                                       umlprofile=self.uml_profile):
                baseclass ='ATFolder'
                baseschema ='ATFolderSchema'
            else:
                baseclass ='BaseFolder'
                baseschema ='BaseFolderSchema'

        else:
            # contentish
            if element.hasStereoType(['atfile'],
                                       umlprofile=self.uml_profile):
                baseclass ='ATFile'
                baseschema ='ATFileSchema'
            elif element.hasStereoType(['atevent'],
                                       umlprofile=self.uml_profile):
                baseclass ='ATEvent'
                baseschema ='ATEventSchema'
            elif element.hasStereoType(['atdocument'],
                                       umlprofile=self.uml_profile):
                baseclass ='ATDocument'
                baseschema ='ATDocumentSchema'
            else:
                baseclass = 'BaseContent'
                baseschema = 'BaseSchema'
                
        # use CMFDynamicViewFTI?
        if not parent_is_archetype and \
           self.getOption('use_dynamic_view', element, True) and \
           not element.hasStereoType(self.atct_stereotype, 
                                     umlprofile=self.uml_profile):
            parentnames.append('BrowserDefaultMixin')

        # if a parent is already an archetype we dont need a baseschema!
        if parent_is_archetype:
            baseclass = None

        # remember support
        if element.hasStereoType(self.remember_stereotype, 
                                 umlprofile=self.uml_profile):
            if 'BaseMember' not in parentnames:
                parentnames.insert(0, 'BaseMember')
            # baseschema = 'BaseMember.schema'            

        ## however: tagged values have priority
        # tagged values for base-class overrule
        if element.getTaggedValue('base_class'):
            baseclass = element.getTaggedValue('base_class')

        # tagged values for base-schema overrule
        if element.getTaggedValue('base_schema'):
            baseschema = element.getTaggedValue('base_schema')

        # [optilude] Ignore the standard class if this is an mixin
        # [jensens] An abstract class might have a base_class!
        if (baseclass and not 
            utils.isTGVFalse(element.getTaggedValue('base_class',1)) and not 
            element.hasStereoType('mixin', umlprofile=self.uml_profile)):
            baseclasses = baseclass.split(',')
            if (utils.isTGVTrue(element.getTaggedValue('parentclass_first')) or 
                utils.isTGVTrue(element.getTaggedValue('parentclasses_first')) or 
                element.hasStereoType(self.remember_stereotype, umlprofile=self.uml_profile)):
                # In case of remember, BaseMember needs to come first, to 
                # ensure that BaseMember.validate_roles overrides 
                # RoleManager.validate_roles
                # this way base_class is used after generalization parents:
                parentnames = parentnames + baseclasses 
            else:
                # this way base_class is used before anything else
                parentnames = baseclasses + parentnames 
        parentnames = list(Set([klass.strip() for klass in parentnames]))
        return baseclass, baseschema, parentnames

    def generateArchetypesClass(self, element, **kw):
        """this is the all singing all dancing core generator logic for a
           full featured Archetypes class
        """
        log.info("%sGenerating class '%s'.",
                 '    '*self.infoind, element.getName())

        name = element.getCleanName()

        # Prepare file
        outfile = StringIO()
        wrt = outfile.write

        # dealing with creation-permissions and -roles for this type
        klass = element.getCleanName()
        if self.getOption('detailed_creation_permissions', element, None):
            product = element.getPackage().getProduct().getCleanName()
            creation_permission = "'%s: Add %s'" % (product, klass)
        else:
            creation_permission = None
        creation_roles = "('Manager', 'Owner')"
        cpfromoption = self.getOption('creation_permission', element, None)
        if cpfromoption:
            creation_permission = self.processExpression(cpfromoption)
        crfromoption = self.getOption('creation_roles', element, None)
        if crfromoption:
            creation_roles = self.processExpression(crfromoption)

        # generate header
        wrt(self.generateHeader(element))

        # generate basic imports

        dependentImports = self.generateDependentImports(element)
        if dependentImports.strip():
            log.debug("Generating dependent imports...")
            wrt(dependentImports)

        additionalImports = self.generateAdditionalImports(element)
        if additionalImports:
            log.debug("Generating additional imports...")
            wrt(additionalImports)

        # imports needed for remember subclassing
        if element.hasStereoType(self.remember_stereotype,
                                 umlprofile=self.uml_profile):
            wrt(REMEMBER_IMPORTS)
            # and set the add content permission to what remember needs
            creation_permission = u'ADD_MEMBER_PERMISSION'
            creation_roles = None

        # imports needed for optional support of SQLStorage
        if utils.isTGVTrue(self.getOption('sql_storage_support',element,0)):
            wrt('from Products.Archetypes.SQLStorage import *\n')

        # import Product config.py
        wrt(TEMPLATE_CONFIG_IMPORT % {
            'module': element.getRootPackage().getProductModuleName()})

        # imports by tagged values
        additionalImports = self.getImportsByTaggedValues(element)
        if additionalImports:
            wrt(u"# additional imports from tagged value 'import'\n")
            wrt(additionalImports)
            wrt(u'\n')

        # We *do* want the resursive=0 below, though!
        aggregatedInterfaces = element.getRefs() + \
                               element.getSubtypeNames(recursive=0,
                                                       filter=['interface'])

        # if it's a derived class check if parent has stereotype 'archetype'
        parent_is_archetype = False
        for p in element.getGenParents():
            parent_is_archetype = parent_is_archetype or \
                                  p.hasStereoType(self.archetype_stereotype,
                                                  umlprofile=self.uml_profile)

        # also check if the parent classes can have subobjects
        baseaggregatedClasses = []
        for b in element.getGenParents():
            baseaggregatedClasses.extend(b.getRefs())
            baseaggregatedClasses.extend(b.getSubtypeNames(recursive=1))

        #also check if the interfaces used can have subobjects
        baseaggregatedInterfaces = []
        for b in element.getGenParents(recursive=1):
            baseaggregatedInterfaces.extend(b.getSubtypeNames(recursive=1,filter=['interface']))

        parentnames = [p.getCleanName() for p in element.getGenParents()]
        additionalParents = element.getTaggedValue('additional_parents')
        if additionalParents:
            parentnames = additionalParents.split(',') + list(parentnames)

        # find base
        baseclass, baseschema, parentnames = self.getArchetypesBase(element, parentnames, parent_is_archetype)

        # variableschema support.
        if element.hasStereoType(self.variable_schema,
                                 umlprofile=self.uml_profile):
            # Including it by default anyway, since 1.4.0/dev.
            parentnames.insert(0, 'VariableSchemaSupport')

        # Interface aggregation
        if self.getAggregatedInterfaces(element):
            parentnames.insert(0, 'AllowedTypesByIfaceMixin')

        # a tool needs to be a unique object
        if element.hasStereoType(self.portal_tools, umlprofile=self.uml_profile):
            print >> outfile, TEMPL_TOOL_HEADER
            parentnames.insert(0, 'UniqueObject')

        parents = ', '.join(parentnames)

        # protected section
        self.generateProtectedSection(outfile, element, 'module-header')

        # generate local Schema from local field specifications
        field_specs = self.getLocalFieldSpecs(element)
        self.generateArcheSchema(element, field_specs, baseschema, outfile)

        # protected section
        self.generateProtectedSection(outfile, element, 'after-local-schema')

        # generate complete Schema
        # prepare schema as class attribute
        parent_schema = ["getattr(%s, 'schema', Schema(()))" % p.getCleanName()
                         for p in element.getGenParents()
                         if not p.hasStereoType(self.python_stereotype,
                                                umlprofile=self.uml_profile)]

        if (parent_is_archetype 
                and not element.hasStereoType(
                    self.remember_stereotype, umlprofile=self.uml_profile)):
            schema = parent_schema
        else:
            # [optilude] Ignore baseschema in abstract mixin classes
            if element.isAbstract():
                schema = parent_schema
            else:
                schema = [baseschema] + parent_schema

        if element.hasStereoType(self.remember_stereotype, umlprofile=self.uml_profile):
            schema.append('BaseMember.schema')
            schema.append('ExtensibleMetadata.schema')

        # own schema overrules base and parents
        schema += ['schema']

        schemaName = '%s_schema' % name
        print >> outfile, utils.indent(schemaName + ' = ' + ' + \\\n    '.join(['%s.copy()' % s for s in schema]), 0)

        # move fields based on move: tagged values
        self.generateFieldMoves(outfile, schemaName, field_specs)

        # protected section
        self.generateProtectedSection(outfile, element, 'after-schema')

        if not element.isComplex():
            print "I: stop complex: ", element.getName()
            return outfile.getvalue()
        if element.getType() in AlreadyGenerated:
            print "I: stop already generated:", element.getName()
            return outfile.getvalue()
        AlreadyGenerated.append(element.getType())

        # [optilude] It's possible parents may become empty now...
        if parents:
            parents = "(%s)" % (parents,)
        else:
            parents = ''
        # [optilude] ... so we can't have () around the last %s
        classDeclaration = 'class %s%s:\n' % (name, parents)

        wrt(classDeclaration)

        doc = element.getDocumentation(striphtml=self.strip_html)
        parsedDoc = ''
        if element.parsed_class:
            parsedDoc = element.parsed_class.getDocumentation()
        if doc:
            print >> outfile, utils.indent('"""%s\n"""' % doc, 1,
                                           stripBlank=True)
        elif parsedDoc:
            # Bit tricky, parsedDoc is already indented...
            print >> outfile, '    """%s"""' % parsedDoc
        else:
            print >> outfile, '    """\n    """'

        print >> outfile, utils.indent('security = ClassSecurityInfo()',1)

        print >> outfile, self.generateImplements(element, parentnames)

        archetype_name = element.getTaggedValue('archetype_name') or \
                         element.getTaggedValue('label')
#        if not archetype_name:
#            archetype_name = name
#        if type(archetype_name) != types.UnicodeType:
#            archetype_name = archetype_name.decode('utf8')
#        portaltype_name = element.getTaggedValue('portal_type') or name

        # [optilude] Only output portal type and AT name if it's not an abstract
        # mixin
        if not element.isAbstract():
            #print >> outfile, (CLASS_ARCHETYPE_NAME % archetype_name).encode('utf8')
            print >> outfile, CLASS_META_TYPE % name
            #print >> outfile, CLASS_PORTAL_TYPE % portaltype_name

        # Let's see if we have to set use_folder_tabs to 0.
        if utils.isTGVTrue(element.getTaggedValue('hide_folder_tabs', False)):
            print >> outfile, CLASS_FOLDER_TABS % 0

        # allowed_interfaces
        parentAggregatedInterfaces = ''
        if utils.isTGVTrue(element.getTaggedValue('inherit_allowed_types', \
           True)) and element.getGenParents():
            pattern = "getattr(%s, 'allowed_interfaces', [])"
            extras = ' + '.join([pattern % p.getCleanName()
                                 for p in element.getGenParents()])
            parentAggregatedInterfaces = '+ ' + extras

        if aggregatedInterfaces or baseaggregatedInterfaces:
            print >> outfile, CLASS_ALLOWED_CONTENT_INTERFACES % \
                  (','.join(aggregatedInterfaces), parentAggregatedInterfaces)

        # _at_rename_after_creation
        rename_after_creation = self.getOption('rename_after_creation',
                                               element, default=True)
        if rename_after_creation:
            print >> outfile, CLASS_RENAME_AFTER_CREATION % \
                  (utils.isTGVTrue(rename_after_creation) and 'True' or 'False')

        # schema attribute
        wrt(utils.indent('schema = %s' % schemaName, 1) + '\n\n')

        # Set base_archetype for remember
        if element.hasStereoType(self.remember_stereotype, umlprofile=self.uml_profile):
            wrt(utils.indent("base_archetype = %s" % baseclass, 1) + '\n\n')

        self.generateProtectedSection(outfile, element, 'class-header', 1)

        # tool __init__ and at_post_edit_script
        if element.hasStereoType(self.portal_tools, umlprofile=self.uml_profile):
            tool_instance_name = element.getTaggedValue('tool_instance_name') \
                                 or 'portal_%s' % element.getName().lower()
            print >> outfile, TEMPL_CONSTR_TOOL % (baseclass,
                                                   tool_instance_name,
                                                   archetype_name)
            self.generateProtectedSection(outfile, element,
                                          'constructor-footer', 2)
            print >> outfile, TEMPL_POST_EDIT_METHOD_TOOL
            self.generateProtectedSection(outfile, element,
                                          'post-edit-method-footer', 2)
            print >> outfile

        # Remember __call__
        if element.hasStereoType(self.remember_stereotype, umlprofile=self.uml_profile):
            print >> outfile, REMEMBER_CALL
            print >> outfile

        self.generateMethods(outfile, element)

        # [optilude] Don't do modify FTI for abstract mixins
        if not element.isAbstract():
            print >> outfile, self.generateModifyFti(element)

        # [optilude] Don't register type for abstract classes or tools
        if not (element.isAbstract() or element.hasStereoType('mixin',
           umlprofile=self.uml_profile)):
            wrt(REGISTER_ARCHTYPE % name)

        # ATVocabularyManager: registration of class
        if element.hasStereoType(self.vocabulary_item_stereotype,
           umlprofile=self.uml_profile) and not element.isAbstract():
            # XXX TODO: fetch container_class - needs to be refined:
            # check if parent has vocabulary_container_stereotype and use its
            # name as container
            # else check for TGV vocabulary_container
            # fallback: use SimpleVocabulary
            container = element.getTaggedValue('vocabulary:portal_type',
                                               'SimpleVocabulary')
            wrt(REGISTER_VOCABULARY_ITEM % (name, container))
        if element.hasStereoType(self.vocabulary_container_stereotype,
                                 umlprofile=self.uml_profile):
            wrt(REGISTER_VOCABULARY_CONTAINER % name)

        wrt('# end of class %s\n\n' % name)

        self.generateProtectedSection(outfile, element, 'module-footer')

        ## handle add content permissions
        if not element.hasStereoType(self.portal_tools,
                                     umlprofile=self.uml_profile):
            # tgv overrules
            cpfromtgv = element.getTaggedValue('creation_permission', None)
            if cpfromtgv:
                creation_permission= self.processExpression(cpfromtgv)
            crfromtgv = element.getTaggedValue('creation_roles', None)
            if crfromtgv:
                creation_roles= self.processExpression(crfromtgv)
            ## abstract classes does not need an Add permission
            if creation_permission and not element.isAbstract():
                self.creation_permissions.append([element.getCleanName(),
                                                  creation_permission,
                                                  creation_roles])
        return outfile.getvalue()

    def generateFlavor(self, element, **kw):
        """this is the all singing all dancing core generator logic for a
           full featured Flavor
        """
        log.info("%sGenerating flavor '%s'.",
                 '    '*self.infoind, element.getName())

        name = element.getCleanName()

        # Prepare file
        outfile = StringIO()
        wrt = outfile.write

        # generate header
        wrt(self.generateHeader(element))

        # generate basic imports

        dependentImports = self.generateDependentImports(element)
        if dependentImports.strip():
            log.debug("Generating dependent imports...")
            wrt(dependentImports)

        additionalImports = self.generateAdditionalImports(element)
        if additionalImports:
            log.debug("Generating additional imports...")
            wrt(additionalImports)

        # imports needed for optional support of SQLStorage
        if utils.isTGVTrue(self.getOption('sql_storage_support',element,0)):
            wrt('from Products.Archetypes.SQLStorage import *\n')

        # import Product config.py
        #wrt(TEMPLATE_CONFIG_IMPORT % {
        #    'module': element.getRootPackage().getProductModuleName()})

        # imports by tagged values
        additionalImports = self.getImportsByTaggedValues(element)
        if additionalImports:
            wrt(u"# additional imports from tagged value 'import'\n")
            wrt(additionalImports)
            wrt(u'\n')
            
        # import for flavor's interface
        wrt("from zope.interface import Interface\n")
        
        # import for flavor's event subscriber
        wrt("from Products.ContentFlavors.interfaces import IFlavorProvider\n")

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
        aggregatedClasses = element.getRefs() + \
                            element.getSubtypeNames(recursive=recursive,
                                                    filter=['class'])
        # We *do* want the resursive=0 below, though!
        aggregatedInterfaces = element.getRefs() + \
                               element.getSubtypeNames(recursive=0,
                                                       filter=['interface'])
        if element.getTaggedValue('allowed_content_types'):
            aggregatedClasses = [e for e in aggregatedClasses]
            for e in element.getTaggedValue('allowed_content_types').split(','):
                e = e.strip()
                if e not in aggregatedClasses:
                    aggregatedClasses.append(e)

        # if it's a derived class check if parent has stereotype 'archetype'
        parent_is_archetype = False
        for p in element.getGenParents():
            parent_is_archetype = parent_is_archetype or \
                                  p.hasStereoType(self.archetype_stereotype,
                                                  umlprofile=self.uml_profile)

        # also check if the parent classes can have subobjects
        baseaggregatedClasses = []
        for b in element.getGenParents():
            baseaggregatedClasses.extend(b.getRefs())
            baseaggregatedClasses.extend(b.getSubtypeNames(recursive=1))

        #also check if the interfaces used can have subobjects
        baseaggregatedInterfaces = []
        for b in element.getGenParents(recursive=1):
            baseaggregatedInterfaces.extend(b.getSubtypeNames(recursive=1,filter=['interface']))

        parentnames = [p.getCleanName() for p in element.getGenParents()]
        additionalParents = element.getTaggedValue('additional_parents')
        if additionalParents:
            parentnames = additionalParents.split(',') + list(parentnames)

        # find base
        #baseclass, baseschema, parentnames = self.getArchetypesBase(element, parentnames, parent_is_archetype)

        # Interface aggregation
        if self.getAggregatedInterfaces(element):
            parentnames.insert(0, 'AllowedTypesByIfaceMixin')
        
        # this flavor's class is an Z3 interface
        parentnames.insert(0,'Interface')

        parents = ', '.join(parentnames)
        
        # protected section
        self.generateProtectedSection(outfile, element, 'module-header')

        # generate local Schema from local field specifications
        field_specs = self.getLocalFieldSpecs(element)
        # no baseschema to be referred to
        self.generateArcheSchema(element, field_specs, None, outfile)

        # protected section
        self.generateProtectedSection(outfile, element, 'after-local-schema')

        # generate complete Schema
        # prepare schema as class attribute
        parent_schema = ["getattr(%s, 'schema', Schema(()))" % p.getCleanName()
                         for p in element.getGenParents()
                         if not p.hasStereoType(self.python_stereotype,
                                                umlprofile=self.uml_profile)]

        schema = parent_schema

        # own schema overrules base and parents
        schema += ['schema']

        schemaName = '%sSchema' % name
        print >> outfile, utils.indent(schemaName + ' = ' + ' + \\\n    '.join(['%s.copy()' % s for s in schema]), 0)

        # move fields based on move: tagged values
        self.generateFieldMoves(outfile, schemaName, field_specs)

        # protected section
        self.generateProtectedSection(outfile, element, 'after-schema')

        # declare event subscriber
        subscriber = "def apply" + name + "(context, event):\n"
        wrt(subscriber)
        wrt("    provider = IFlavorProvider(context)\n")
        wrt("    provider.flavor_names += ('"+name+".default',)\n\n")

        # protected section
        self.generateProtectedSection(outfile, element, 'after-subscriber')

        if not element.isComplex():
            print "I: stop complex: ", element.getName()
            return outfile.getvalue()
        if element.getType() in AlreadyGenerated:
            print "I: stop already generated:", element.getName()
            return outfile.getvalue()
        AlreadyGenerated.append(element.getType())

        #if self.ape_support:
        #    print >> outfile, TEMPL_APE_HEADER % {'class_name': name}

        # [optilude] It's possible parents may become empty now...
        if parents:
            parents = "(%s)" % (parents,)
        else:
            parents = ''
        
        classDeclaration = 'class %s%s:\n' % (name, parents)
        wrt(classDeclaration)

        doc = element.getDocumentation(striphtml=self.strip_html)
        parsedDoc = ''
        if element.parsed_class:
            parsedDoc = element.parsed_class.getDocumentation()
        if doc:
            print >> outfile, utils.indent('"""%s\n"""' % doc, 1,
                                           stripBlank=True)
        elif parsedDoc:
            # Bit tricky, parsedDoc is already indented...
            print >> outfile, '    """%s"""' % parsedDoc
        else:
            print >> outfile, '    """\n    """'

        #print >> outfile, self.generateImplements(element, parentnames)

        # allowed_interfaces
        parentAggregatedInterfaces = ''
        if utils.isTGVTrue(element.getTaggedValue('inherit_allowed_types', \
           True)) and element.getGenParents():
            pattern = "getattr(%s, 'allowed_interfaces', [])"
            extras = ' + '.join([pattern % p.getCleanName()
                                 for p in element.getGenParents()])
            parentAggregatedInterfaces = '+ ' + extras

        if aggregatedInterfaces or baseaggregatedInterfaces:
            print >> outfile, CLASS_ALLOWED_CONTENT_INTERFACES % \
                  (','.join(aggregatedInterfaces), parentAggregatedInterfaces)

        # But *do* add the actions, views, etc.
        #actions_views = self.generateActionsAndViews(element,
        #                                             aggregatedClasses)
        #if actions_views:
        #    print >> outfile, actions_views

        # schema attribute
        #wrt(utils.indent('schema = %s' % schemaName, 0) + '\n\n')

        #self.generateProtectedSection(outfile, element, 'class-header', 1)

        # self.generateDefaultAdapterMethods(outfile, element)

        wrt('# end of flavor %s\n\n' % name)

        self.generateProtectedSection(outfile, element, 'module-footer')
        
        # prepare for generation the flavors.zcml file of that package
        # annotate package with the list of generated flavors

        flavor = {}
        flavor['name'] = name
        flavor['packageName'] = name
        flavor['fullName'] = name + ".default"
        flavor['title'] = name + " !"
        flavor['description'] = name + "'s description"
        flavor['schemaName'] = name + "Schema"
        flavor['markerName'] = name
        flavor['handlerName'] = "apply" + name
        flavor['implementers'] = []

        for implementer in element.getRealizationChildren(recursive=True):
            # TODO: filter out those implementers whose stereotype makes the following declaration useless
            # if not implementer.hasStereotype(self.some_stereotypes_I_dont_know_which_ones):
            qualifiedImplementerClass = None
            if implementer.hasStereoType(self.stub_stereotypes):
                # In principle, don't do a thing, but...
                if implementer.getTaggedValue('import_from', None):
                    qualifiedImplementerClass = implementer.getTaggedValue('import_from') + "." + implementer.getName()
            else:
                qualifiedImplementerClass = implementer.getQualifiedModuleName(None,forcePluginRoot=self.force_plugin_root,includeRoot=0,) + "." + implementer.getName()
            if qualifiedImplementerClass:
                flavor['implementers'].append(qualifiedImplementerClass)

        # add this new flavor to a list annotated to the package of the current element
        package = element.getPackage()
        flavorsList = package.getAnnotation('generatedFlavors')
        flavorsList.append(flavor)
        package.annotate('generatedFlavors',flavorsList)

        return outfile.getvalue()

    def generateZope2Interface(self, element, **kw):
        outfile = StringIO()
        log.info("%sGenerating zope2 interface '%s'.",
                 '    '*self.infoind, element.getName())

        wrt = outfile.write

        dependentImports = self.generateDependentImports(element).strip()
        if dependentImports:
            print >> outfile, dependentImports

        additionalImports = self.generateAdditionalImports(element)
        if additionalImports:
            print >> outfile, additionalImports

        print >> outfile, IMPORT_INTERFACE

        additionalImports = element.getTaggedValue('imports')
        if additionalImports:
            wrt(additionalImports)
        print >> outfile

        aggregatedClasses = element.getRefs() + element.getSubtypeNames(recursive=1)

        AlreadyGenerated.append(element.getType())
        name = element.getCleanName()

        wrt('\n')

        parentnames = [p.getCleanName() for p in element.getGenParents()]
        additionalParents = element.getTaggedValue('additional_parents')
        if additionalParents:
            parentnames = additionalParents.split(',') + list(parentnames)

        if not [c for c in element.getGenParents() if c.isInterface()]:
            parentnames.insert(0, 'Base')
        parents = ', '.join(parentnames)

        s1 = 'class %s%s(%s):\n' % (self.prefix, name, parents)

        wrt(s1)
        doc = element.getDocumentation(striphtml=self.strip_html)
        print >> outfile, utils.indent('"""%s\n"""' % doc, 1,
                                       stripBlank=True)

        header = element.getTaggedValue('class_header')
        if header:
            print >> outfile, utils.indent(header, 1)

        wrt('\n')
        self.generateMethods(outfile, element, mode='interface')
        wrt('\n# end of class %s' % name)

        return outfile.getvalue()


    def generateHeader(self, element):
        outfile = StringIO()
        i18ncontent = self.getOption('i18ncontent', element,
                                      self.i18n_content_support)

        genparentsstereotypes = element.getRealizationParents()
        if i18ncontent == 'linguaplone' and \
             not element.hasStereoType('remember'):
            s1 = TEMPLATE_HEADER_I18N_LINGUAPLONE
        else:
            s1 = TEMPLATE_HEADER

        outfile.write(s1)
        hasz3parent = False
        if (genparentsstereotypes and
            self.default_interface_type == 'z3'):
            hasz3parent = True
        for gpst in genparentsstereotypes:
            if gpst.hasStereoType('z3'):
                hasz3parent = True
                break
        if hasz3parent or element.hasStereoType('z3'):
            outfile.write('from zope import interface\n')

        return outfile.getvalue()

    def getTools(self,package):
        """ returns a list of  generated tools """
        res=[c for c in package.getClasses(recursive=1) if
                    c.hasStereoType(self.portal_tools, umlprofile=self.uml_profile)]

        if autoinstallOnly:
            res=[c for c in res if utils.isTGVTrue(c.getTaggedValue('autoinstall', 1)) ]

        return res

    def getGeneratedTools(self,package):
        """ returns a list of  generated tools """
        return [c for c in self.getGeneratedClasses(package) if
                    c.hasStereoType(self.portal_tools, umlprofile=self.uml_profile)]

    def generateStdFiles(self, package):
        if package.isRoot():
            self.generateStdFilesForProduct(package)
        else:
            self.generateStdFilesForPackage(package)

    def generateStdFilesForPackage(self, package):
        """Generate the standard files for a non-root package."""

        # Generate an __init__.py
        self.generatePackageInitPy(package)
        # Generate a flavors.zcml
        self.generatePackageFlavorsZcml(package)

    def updateVersionForProduct(self, package):
        """Increment the build number in verion.txt,"""

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
        installTemplate = open(os.path.join(self.templateDir, 
                                            'Install.py')).read()
        extDir = os.path.join(package.getFilePath(), 'Extensions')
        self.makeDir(extDir)

        # make __init__.py
        ipy=self.makeFile(os.path.join(extDir,'__init__.py'))
        ipy.write('# make me a python module\n')
        ipy.close()

        # prepare (d)TML varibles
        d={'package'    : package,
           'generator'  : self,
           'product_name': package.getProductName(),
           'builtins'   : __builtins__,
           'utils'       :utils,
        }
        d.update(__builtins__)

        templ=self.readTemplate('Install.py')
        dtml=HTML(templ,d)
        res=dtml()

        of=self.makeFile(os.path.join(extDir,'Install.py'))
        of.write(res)
        of.close()

        return

    def generateConfigPy(self, package):
        """Generate config.py."""
        # new fangled stuff
        # Grab an adapter for the package (so from IPackage) to
        # IConfigPyView.
        assert IPackage.providedBy(package)
        view = IConfigPyView(package)
        view.run(generator=self)
        # ^^^ Above run is still full of junk.
        # But, hurray, we do have a view which cleans up this file.

    def generateProductInitPy(self, package):
        """ Generate __init__.py at product root from the DTML template"""

        # Get the names of packages and classes to import
        packageImports = [m.getModuleName() for m in 
                          package.getAnnotation('generatedPackages') or []
                          if not (m.hasStereoType('tests',
                                                  umlprofile=self.uml_profile)
                                  or m.hasStereoType('stub',
                                                     umlprofile=self.uml_profile))
                          ]
        classImports   = [m.getModuleName() for m in
                          package.generatedModules 
                          if not m.hasStereoType('tests',
                                                 umlprofile=self.uml_profile)]

        # Find additional (custom) permissions
        additional_permissions = []
        addperms = self.getOption('additional_permission',
                                  package,default=[])
        for line in addperms:
            if len(line) > 0:
                line = line.split('|')
                line[0] = line[0].strip()
                if len(line) > 1:
                    line[1] = ["'%s'" % r.strip() 
                               for r in line[1].split(',')]
                additional_permissions.append(line)

        # Find out if we need to initialise any tools
        generatedTools = self.getGeneratedTools(package)
        hasTools = 0
        toolNames = []
        if generatedTools:
            toolNames = [c.getQualifiedName(package, includeRoot=0) for c in generatedTools]
            hasTools = 1

        # Get the preserved code section
        parsed = utils.parsePythonModule(self.targetRoot,
                                         package.getFilePath(),
                                         '__init__.py')

        protectedInitCodeH = self.getProtectedSection(parsed, 'custom-init-head', 0)
        protectedInitCodeT = self.getProtectedSection(parsed, 'custom-init-top', 1)
        protectedInitCodeB = self.getProtectedSection(parsed, 'custom-init-bottom', 1)

        # prepare DTML varibles
        d={'generator': self,
           'utils': utils,
           'package': package,
           'product_name': package.getProductName(),
           'package_imports': packageImports,
           'class_imports': classImports,
           'additional_permissions': additional_permissions,
           'has_tools': hasTools,
           'tool_names': toolNames,
           'creation_permissions': self.creation_permissions,
           'protected_init_section_head': protectedInitCodeH,
           'protected_init_section_top': protectedInitCodeT,
           'protected_init_section_bottom': protectedInitCodeB,
           }

        templ=self.readTemplate('__init__product.py')
        dtml=HTML(templ,d)
        res=dtml()

        of=self.makeFile(os.path.join(package.getFilePath(),'__init__.py'))
        of.write(res)
        of.close()

        return

    def generatePackageInitPy(self, package):
        """ Generate __init__.py for packages from the DTML template"""

        # Get the names of packages and classes to import
        packageImports = [m.getModuleName() for m in 
                          package.getAnnotation('generatedPackages') or []
                          if not (m.hasStereoType('tests',
                                                  umlprofile=self.uml_profile)
                                  or m.hasStereoType('stub',
                                                     umlprofile=self.uml_profile))
                          ]
        classImports   = [m.getModuleName() for m in
                          package.generatedModules 
                          if not m.hasStereoType('tests',
                                                 umlprofile=self.uml_profile)]

        # Get the preserved code sections
        parsed = utils.parsePythonModule(self.targetRoot,
                                         package.getFilePath(),
                                         '__init__.py')
        headerCode = self.getProtectedSection(parsed, 'init-module-header')
        footerCode = self.getProtectedSection(parsed, 'init-module-footer')

        # Prepare DTML varibles
        d = {'generator': self,
             'package': package,
             'utils': utils,
             'package_imports': packageImports,
             'class_imports': classImports,
             'protected_module_header': headerCode,
             'protected_module_footer': footerCode,
             }

        templ=self.readTemplate('__init_package__.py')
        dtml=HTML(templ,d)
        res=dtml()

        of=self.makeFile(os.path.join(package.getFilePath(),'__init__.py'))
        of.write(res)
        of.close()
        return

    def subPackagesWithFlavors(self,package):
        """ returns the (possibly empty) list of direct sub-packages which (recursively) contain at least one flavor """
        sp = []
        for subPackage in package.getAnnotation('generatedPackages') or []:
            if not (subPackage.hasStereoType('tests', umlprofile=self.uml_profile) or subPackage.hasStereoType('stub',umlprofile=self.uml_profile)):
                if subPackage.getAnnotation('generatedFlavors'):
                    sp.append(subPackage)
                elif self.subPackagesWithFlavors(subPackage) != []:
                    sp.append(subPackage)
        return sp
        
    def generatePackageFlavorsZcml(self,package):
        """ Generate flavors.zcml for packages if it contains flavors """
        
        generatedFlavors = package.getAnnotation('generatedFlavors') or []
        subPackagesWithFlavors = [m.getModuleName() for m in self.subPackagesWithFlavors(package)]
            
        if generatedFlavors != [] or subPackagesWithFlavors != []:
            ppath = package.getFilePath()
            handleSectionedFile(['templates', 'flavors.zcml'],
                                os.path.join(ppath, 'flavors.zcml'),
                                sectionnames=['HEAD','FOOT'],
                                templateparams={'flavors': generatedFlavors,
                                                'subPackagesWithFlavors': subPackagesWithFlavors})

    def generateStdFilesForProduct(self, package):
        """Generate __init__.py,  various support files and and the skins
        directory. The result is a QuickInstaller installable product
        """

        target = package.getFilePath ()
        # remove trailing slash
        if target[-1] in ('/','\\'):
            target=target[:-1]
        # Create a tool.gif if necessary
        if self.getGeneratedTools(package):
            gifSourcePath = os.path.join(self.templateDir, 'tool.gif')
            toolgif = open(gifSourcePath, 'rb').read()
            gifTargetPath = os.path.join(package.getFilePath(),
                                         'tool.gif')
            of=self.makeFile(gifTargetPath, self.force, 1)
            if of:
                of.write(toolgif)
                of.close()
        # Generate a refresh.txt for the product
        of=self.makeFile(os.path.join(package.getFilePath(),'refresh.txt'))
        of.close()
        # Increment version.txt build number
        self.updateVersionForProduct(package)
        # Generate product root __init__.py
        self.generateProductInitPy(package)
        # Generate config.py from template
        self.generateConfigPy(package)
        # Generate Extensions/Install.py
        self.generateInstallPy(package)
        # Generate generic setup profile
        self.generateGSDirectory(package)
        # Generate GS skins.xml file
        self.generateGSSkinsXMLFile(package)
        # Generate GS types.xml file
        self.generateGSTypesXMLFile(package)
        # Generate GS types folder and tape.xml files
        self.generateGSTypesFolderAndXMLFiles(package)
        # Generate configure.zcml and profiles.zcml
        self.generateConfigureAndProfilesZCML(package) 
        # Generate setuphandlers.py and import_steps.xml
        self.generateGSsetuphandlers(package)
        # Generate factorytool.xml
        self.generateGSFactoryTooXMLFile(package)
        # generate GS cssregistry.xml
        self.generateGSStylesheetsXML(package)
        # generate GS jsregistry.xml
        self.generateGSJavascriptsXML(package)
        # generate toolset.xml
        self.generateGSToolsetXML(package)
        # generate membrane_tool.xml if stereotype is remember
        self.generateGSMembraneToolXML(package)
        # Generate flavors.zcml
        self.generatePackageFlavorsZcml(package)

        

    def generateConfigureAndProfilesZCML(self, package):
        """Generate configure.zcml and profiles.zcml if type registration or
        skin registration is set to 'genericsetup'
        """       
        ppath = package.getFilePath()
        pname = package.getProductName()
        
        handleSectionedFile(['templates', 'profiles.zcml'],
                            os.path.join(ppath, 'profiles.zcml'),
                            sectionnames=['profiles.zcml'],
                            templateparams={'product_name': pname})
    
        packageIncludes = [m.getModuleName() for m in 
                          package.getAnnotation('generatedPackages') or []
                          if not (m.hasStereoType('tests',
                                                  umlprofile=self.uml_profile)
                                  or m.hasStereoType('stub',
                                                     umlprofile=self.uml_profile))
                          ]

        generatedFlavors = package.getAnnotation('generatedFlavors') or []
        packagesWithFlavors = [m.getModuleName() for m in self.subPackagesWithFlavors(package)]
        containsFlavors = generatedFlavors != [] or packagesWithFlavors != []

        handleSectionedFile(['templates', 'configure.zcml'],
                            os.path.join(ppath, 'configure.zcml'),
                            sectionnames=['configure.zcml'],
                            templateparams={'packages': packageIncludes,
                                            'containsFlavors': containsFlavors})
    
    def generateGSDirectory(self, package):
        """Create genericsetup directory profiles/default.
        """
        profileDir = os.path.join(package.getFilePath(), 'profiles')
        self.makeDir(profileDir)
        profileDefaultDir = os.path.join(profileDir, 'default')
        self.makeDir(profileDefaultDir)
    
    def generateGSToolsetXML(self, package):
        """Generate the factorytool.xml.
        """
        tools = []
        klasses = self.getGeneratedTools(package)
        for klass in klasses:
            if utils.isTGVFalse(klass.getTaggedValue('autoinstall',1)):
                continue
            
            path = '.'.join([
                'Products',
                klass.getQualifiedModuleName(),
                klass.getCleanName(),
            ])
            toolname = klass.getTaggedValue('tool_instance_name', None)
            if toolname:
                tool_id = toolname
            else:
                tool_id = 'portal_%s' % klass.getCleanName().lower()
            tools.append(
                {
                    'klass': path,
                    'tool_id': tool_id,
                }
            )
        
        ppath = os.path.join(package.getFilePath(), 'profiles', 'default')
        handleSectionedFile(['templates', 'toolset.xml'],
                            os.path.join(ppath, 'toolset.xml'),
                            sectionnames=['toolset.xml'],
                            templateparams={ 'tools': tools })
    
    def generateGSFactoryTooXMLFile(self, package):
        """Generate the factorytool.xml.
        """
        klasses = self.getGeneratedClasses(package)
        factorytypes = []
        for klass in klasses:
            if klass.hasStereoType(['tool', 'portal_tool']):
                continue
            factoryopt = self.getOption('use_portal_factory', klass, True)
            if utils.isTGVTrue(factoryopt) \
              and not (klass.getPackage().hasStereoType('tests') \
              or klass.isAbstract() \
              or klass.hasStereoType(['widget', 'field', 'stub'])):
                klassname = klass.getTaggedValue('portal_type') \
                            or klass.getCleanName()
                factorytypes.append(klassname)
        
        ppath = os.path.join(package.getFilePath(), 'profiles', 'default')
        handleSectionedFile(['templates', 'factorytool.xml'],
                            os.path.join(ppath, 'factorytool.xml'),
                            templateparams={ 'factory_types': factorytypes })
    
    def generateGSStylesheetsXML(self, package):
        """Generate the cssregistry.xml file.
        """
        style = dict()
        style['title'] = ''
        style['cacheable'] = 'True'
        style['compression'] = 'save'
        style['cookable'] = 'True'
        style['enabled'] = '1'
        style['expression'] = ''
        style['id'] = 'myfancystyle.css'
        style['media'] = 'all'
        style['rel'] = 'stylesheet'
        style['rendering'] = 'import'
        
        ppath = os.path.join(package.getFilePath(), 'profiles', 'default')
        handleSectionedFile(['templates', 'cssregistry.xml'],
                            os.path.join(ppath, 'cssregistry.xml'),
                            sectionnames=['cssregistry.xml'],
                            templateparams={ 'css': [style] })
    
    def generateGSJavascriptsXML(self, package):
        """Generate the jsregistry.xml file.
        """
        script = dict()
        script['cacheable'] = 'True'
        script['compression'] = 'save'
        script['cookable'] = 'True'
        script['enabled'] = 'True'
        script['expression'] = ''
        script['id'] = 'myfancyscript.js'
        script['inline'] = 'False'
        
        ppath = os.path.join(package.getFilePath(), 'profiles', 'default')
        handleSectionedFile(['templates', 'jsregistry.xml'],
                            os.path.join(ppath, 'jsregistry.xml'),
                            sectionnames=['jsregistry.xml'],
                            templateparams={ 'scripts': [script] })
    
    def generateGSSkinsXMLFile(self, package):
        """Create the skins.xml file if skin_registrarion tagged value is set
        to genericsetup.
        
        Reads all directories from productname/skins and generates and uses
        them for xml file generation.
        """
        dirs = os.listdir(os.path.join(package.getFilePath(), 'skins'))
        pname = package.getProductName()
        skindirs = []
        for dir in dirs:
            if os.path.isdir(os.path.join(package.getFilePath(), 'skins', dir)):
                skindir = dict()
                skindir['name'] = dir
                skindir['directory'] = '%s/skins/%s' % (pname, dir)
                skindirs.append(skindir)
        
        ppath = os.path.join(package.getFilePath(), 'profiles', 'default')
        handleSectionedFile(['templates', 'skins.xml'],
                            os.path.join(ppath, 'skins.xml'),
                            templateparams={ 'skinDirs': skindirs })
        
    def generateGSTypesXMLFile(self, package):
        """Create the types.xml file if type_registrarion tagged value is set
        to genericsetup.
        """
        defs = list()
        self._getTypeDefinitions(defs, package, package.getProductName())
        
        ppath = os.path.join(package.getFilePath(), 'profiles', 'default')
        handleSectionedFile(['templates', 'types.xml'],
                            os.path.join(ppath, 'types.xml'),
                            templateparams={ 'portalTypes': defs })
    
    def generateGSTypesFolderAndXMLFiles(self, package):
        """Create the types folder and the corresponding xml files for the
        portal types inside it if type_registrarion tagged value is set
        to genericsetup.
        """
        profiledir = os.path.join(package.getFilePath(), 'profiles', 'default')
        typesdir = os.path.join(profiledir, 'types')
        
        if not 'types' in os.listdir(profiledir):
            os.mkdir(os.path.join(typesdir))
        
        if not os.path.isdir(typesdir):
            raise Exception('types is not a directory')
        
        defs = list()
        self._getTypeDefinitions(defs, package, package.getProductName())
        
        for typedef in defs:
            #print typedef
            filename = '%s.xml' % typedef['name']
            handleSectionedFile(['templates', 'type.xml'],
                                os.path.join(typesdir, filename),
                                templateparams={ 'ctype': typedef })
            
    def generateGSsetuphandlers(self, package):
        """generates setuphandlers.py and import_steps.xml"""
        # generate setuphandlers
        dependend_profiles = package.getTaggedValue('dependend_profiles', '')
        dependend_profiles = [dp.strip() for dp in dependend_profiles.split(',')\
                              if dp.strip()]
        alltools = self.getGeneratedTools(package)
        toolnames = [t.getTaggedValue('tool_instance_name') or \
                     'portal_%s' % t.getName().lower() for t in alltools]
        allclasses = self.getGeneratedClasses(package)
        catalogmultiplexed =  [klass for klass in allclasses \
                               if self.getOption('catalogmultiplex:white', 
                                                 klass, None) \
                               or self.getOption('catalogmultiplex:black', 
                                                 klass, None)]
        notsearchabletypes = [(klass.getTaggedValue('portal_type') or \
                              klass.getCleanName()) \
                              for klass in allclasses\
                              if utils.isTGVFalse(self.getOption('searchable_type', \
                                                                 klass, True))]
        hidemetatypes = [(klass.getTaggedValue('portal_type') or \
                          klass.getCleanName()) \
                          for klass in allclasses \
                          if utils.isTGVFalse(self.getOption('display_in_navigation', 
                                                             klass, True))]
        templateparams = {
            'generator': self,
            'package': package,
            'product_name': package.getProductModuleName(),
            'now': datetime.datetime.isoformat(datetime.datetime.now()),
            'dependend_profiles': dependend_profiles,
            'alltools': alltools,
            'toolnames': toolnames,
            'catalogmultiplexed': catalogmultiplexed,
            'hasrelations': package.num_generated_relations > 0,
            'hasvocabularies': package.getProductName() in self.vocabularymap.keys(),
            'notsearchabletypes': notsearchabletypes,
            'hidemetatypes': hidemetatypes,
            
        }        
        handleSectionedFile(['templates', 'setuphandlers.py'], 
                            os.path.join(package.getFilePath(),
                                         'setuphandlers.py'),
                            sectionnames=('HEAD', 'FOOT'),
                            templateparams=templateparams
                           )
        # generate import_steps.xml
        profiledir = os.path.join(package.getFilePath(), 'profiles', 'default')
        handleSectionedFile(['templates', 'import_steps.xml'], 
                            os.path.join(profiledir, 'import_steps.xml'),
                            sectionnames=('ADDITIONALSTEPS',),
                            templateparams=templateparams
                           )
    
    def generateGSMembraneToolXML(self, package):
        types = []
        self.getRememberTypes(types, package)
        profiledir = os.path.join(package.getFilePath(), 'profiles', 'default')
        handleSectionedFile(['templates', 'membrane_tool.xml'], 
                            os.path.join(profiledir, 'membrane_tool.xml'),
                            templateparams={'membrane_types': types}
                           )
    
    def getRememberTypes(self, types, package):
        # TODO: consider if there is an own workflow on a matched object.
        # then, this workflow has precedence and use_workflow and
        # active_workflow_states has to be ignored and the ones from the
        # set workflow must be used.
        klasses = package.getClasses()
        if not klasses:
            for package in package.getPackages():
                self.getRememberTypes(types, package)
        
        for klass in klasses:
            if klass.hasStereoType(['remember'], umlprofile=self.uml_profile):
                
                statemachine = klass.getStateMachine()
                
                if not statemachine:
                    workflow = klass.getTaggedValue('use_workflow', None)
                    if not workflow:
                        raise Exception('No workflow set for remember ' + \
                                        'type, aborting.')
                else:
                    workflow = statemachine.getCleanName()
                
                workflow_states = klass.getTaggedValue('active_workflow_states',
                                                      None)
                if not workflow_states:
                   raise Exception('No workflow states set for remember ' + \
                                   'type, aborting.')
                
                type = dict()
                type['portal_type'] = klass.getCleanName()
                type['workflow'] = workflow
                type['active_states'] = eval(workflow_states)
                types.append(type)
    

    def getGeneratedClasses(self,package):
        classes = package.getAnnotation('generatedClasses') or []
        for p in package.getPackages():
            if not p.isProduct():
                classes.extend(self.getGeneratedClasses(p))
        res=[]
        for c in classes:
            if c not in res:
                res.append(c)
        return res
    
    def generatePackage(self, package, recursive=1):
        log.debug("Generating package %s.",
                  package)
        if package.hasStereoType(self.stub_stereotypes, umlprofile=self.uml_profile):
            log.debug("It's a stub stereotyped package, skipping.")
            return
        package.generatedModules = []
        if package.getName().lower().startswith('java') or not package.getName():
            #to suppress these unneccesary implicit created java packages (ArgoUML and Poseidon)
            log.debug("Ignoring unneeded package '%s'.",
                      package.getName())
            return

        self.makeDir(package.getFilePath())

        for element in package.getClasses()+package.getInterfaces():
            if not self._isContentClass(element):
                continue

            module=element.getModuleName()
            package.generatedModules.append(element)
            outfilepath=os.path.join(package.getFilePath(), module+'.py')

            # below: utils.parsePythonModule?
            filename = os.path.join(self.targetRoot, outfilepath)
            log.debug("Filename (joined with targetroot) is "
                      "'%s'.", filename)
            try:
                mod=PyParser.PyModule(filename)
                log.debug("Existing sources found for element %s: %s.",
                          element.getName(), outfilepath)
                self.parsed_sources.append(mod)
                for c in mod.classes.values():
                    self.parsed_class_sources[package.getFilePath()+'/'+c.name]=c
            except IOError:
                log.debug("No source found at %s.",
                          filename)
                pass
            except:
                log.critical("Error while reparsing file '%s'.",
                             outfilepath)
                raise
            # ^^^ utils.parsePythonModule?

            try:
                outfile = StringIO()
                element.parsed_class = self.parsed_class_sources.get(element.getPackage().getFilePath()+'/'+element.name,None)
                if not element.isInterface():
                    outfile.write(self.generateModuleInfoHeader(element))
                    print >>outfile, self.dispatchXMIClass(element)
                    generated_classes = package.getAnnotation('generatedClasses') or []
                    generated_classes.append(element)
                    package.annotate('generatedClasses', generated_classes)
                else:
                    outfile = StringIO()
                    outfile.write(self.generateModuleInfoHeader(element))
                    print >>outfile, self.dispatchXMIInterface(element)
                    generated_interfaces = package.getAnnotation('generatedInterfaces') or []
                    generated_interfaces.append(element)
                    package.annotate('generatedInterfaces', generated_interfaces)

                buf = outfile.getvalue()

                log.debug("The outfile is ready to be written to disk now. "
                          "Loading it with the pyparser just to be sure we're "
                          "not writing broken files to disk.")
                try:
                    PyParser.PyModule(buf, mode='string')
                    log.debug("Nothing wrong with the outfile '%s'.",
                              outfilepath)
                except:
                    log.info(buf)
                    log.critical("There's something wrong with the python code we're about "
                                 "to write to disk. Perhaps a faulty tagged value or a "
                                 "genuine bug in parsing the previous version of the file. "
                                 "The filename is '%s'. For easy debugging, the file is "
                                 "printed above.",
                                 outfilepath)
                    raise
                classfile = self.makeFile(outfilepath)
                # TBD perhaps check if the file is parseable
                if type(buf) == types.UnicodeType:
                    buf = buf.encode('utf-8')
                print >> classfile, buf
                classfile.close()
            except:
                #roll back the changes
                # and dont swallow the exception
                raise

        #generate subpackages
        generatedPkg = package.getAnnotation('generatedPackages') or []
        for p in package.getPackages():
            if p.isProduct():
                self.infoind += 1
                self.generateProduct(p)
                self.infoind -= 1
            else:
                log.info("%sGenerating package '%s'.",
                         '    '*self.infoind,
                         p.getName())
                self.infoind += 1
                self.generatePackage(p,recursive=1)
                self.infoind -= 1
                generatedPkg.append(p)
                package.annotate('generatedPackages',generatedPkg)

        self.generateStdFiles(package)

    def generateRelation(self, doc, collection, relname, relid,
            allowed_source_types=[], allowed_target_types=[],
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
        if allowed_source_types or allowed_target_types:
            typeconst=doc.createElement('TypeConstraint')
            typeconst.setAttribute('id','type_constraint')
            ruleset.appendChild(typeconst)

        for sourcetype in allowed_source_types:
            el=doc.createElement('allowedSourceType')
            typeconst.appendChild(el)
            el.appendChild(doc.createTextNode(sourcetype))

        for targettype in allowed_target_types:
            el=doc.createElement('allowedTargetType')
            typeconst.appendChild(el)
            el.appendChild(doc.createTextNode(targettype))

        # I don't know if the same as the above goes for interfaces
        if sourceinterface or targetinterface:
            ifconst=doc.createElement('InterfaceConstraint')
            ifconst.setAttribute('id','interface_constraint')
            ruleset.appendChild(ifconst)

        if sourceinterface:
            el=doc.createElement('allowedSourceInterface')
            ifconst.appendChild(el)
            el.appendChild(doc.createTextNode(sourceinterface))

        if targetinterface:
            ifconst.setAttribute('id','interface_constraint')
            el=doc.createElement('allowedTargetInterface')
            ifconst.appendChild(el)
            el.appendChild(doc.createTextNode(targetinterface))


        #association constraint
        if assocclassname:
            contref = doc.createElement('ContentReference')
            ruleset.appendChild(contref)
            contref.setAttribute('id', 'content_reference')
            pt = doc.createElement('portalType')
            contref.appendChild(pt)
            pt.appendChild(doc.createTextNode(assocclassname))

            pt = doc.createElement('shareWithInverse')
            contref.appendChild(pt)
            pt.appendChild(doc.createTextNode('1'))

            el = doc.createElement('primary')
            el.appendChild(doc.createTextNode(str(primary)))
            contref.appendChild(el)

        #cardinality
        targetcardinality=list(targetcardinality)
        if targetcardinality[0] == -1:
            targetcardinality[0] = None
        if targetcardinality[1] == -1:
            targetcardinality[1] = None

        if targetcardinality != [None, None]:
            const = doc.createElement('CardinalityConstraint')
            ruleset.appendChild(const)
            const.setAttribute('id', 'cardinality')
            if targetcardinality[0]:
                el = doc.createElement('minTargetCardinality')
                const.appendChild(el)
                el.appendChild(doc.createTextNode(str(targetcardinality[0])))
            if targetcardinality[1]:
                el = doc.createElement('maxTargetCardinality')
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

    def generateRelations(self, package):
        # Initializing some stuff as I got an error report.
        sourcetype = None
        targettype = None
        sourceinterface = None
        targetinterface = None
        sourcecardinality = None
        targetcardinality = None
        assocclassname = None
        
        doc=minidom.Document()
        lib=doc.createElement('RelationsLibrary')
        doc.appendChild(lib)
        coll=doc.createElement('RulesetCollection')
        coll.setAttribute('id',package.getCleanName())
        lib.appendChild(coll)
        package.num_generated_relations=0
        assocs = package.getAssociations(recursive=1)
        processed = [] # xxx hack and workaround, not solution, avoids double
                       # generation of relations
        for assoc in assocs:
            if assoc in processed:
                continue
            processed.append(assoc)
            if self.getOption('relation_implementation',assoc,'basic') != 'relations':
                continue

            source=assoc.fromEnd.obj
            target=assoc.toEnd.obj

            targetcard=list(assoc.toEnd.mult)
            sourcecard=list(assoc.fromEnd.mult)
            sourcecard[0]=None #temporary pragmatic fix
            targetcard[0]=None #temporary pragmatic fix
            #print 'relation:',assoc.getName(),'target cardinality:',targetcard,'sourcecard:',sourcecard
            allowed_source_types=None
            allowed_target_types=None
            sourceinterface=None
            targetinterface=None

            def getAllowedTypes(obj):
                if obj.isAbstract():
                    allowed_types=tuple(obj.getGenChildrenNames())
                else:
                    allowed_types=(obj.getName(),) + tuple(obj.getGenChildrenNames())
                return allowed_types

            if source.isInterface():
                sourceinterface=source.getCleanName()
            else:
                allowed_source_types = getAllowedTypes(source)
                # sourcetype=source.getCleanName()

            if target.isInterface():
                targetinterface=target.getCleanName()
            else:
                allowed_target_types = getAllowedTypes(target)
                # targettype=target.getCleanName()

            inverse_relation_name = assoc.getTaggedValue('inverse_relation_name', None)
            if not inverse_relation_name and assoc.fromEnd.isNavigable:
                if self.getOption('old_inverse_relation_name', assoc, None):
                    # BBB
                    inverse_relation_name = '%s_inverse' % assoc.getCleanName()
                else:
                    fromEndName = assoc.fromEnd.getName(ignore_cardinality=1)
                    toEndName = assoc.toEnd.getName(ignore_cardinality=1)
                    if fromEndName == toEndName:
                        inverse_relation_name =  '%s_inv' % assoc.getCleanName()
                    else:
                        inverse_relation_name =  '%s_%s' % (toEndName.lower(), fromEndName.lower())

            assocclassname=getattr(assoc,'isAssociationClass',0) and assoc.getCleanName() or assoc.getTaggedValue('association_class') or self.getOption('association_class',assoc,None)
            self.generateRelation(doc, coll,
                assoc.getCleanName(),
                assoc.getId(),
                allowed_source_types=allowed_source_types,
                allowed_target_types=allowed_target_types,
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
                    allowed_source_types=allowed_target_types,
                    allowed_target_types=allowed_source_types,
                    sourceinterface=targetinterface,
                    targetinterface=sourceinterface,
                    sourcecardinality=targetcard,
                    targetcardinality=sourcecard,

                    assocclassname=assocclassname,
                    inverse_relation_id=assoc.getId()
                    )

            # ATVM integration - by jensens
            # very special case: create a vocabulary with the association name
            # this is needed for some use-cases, where a association class has
            # use an vocabulary with the name ofthe relation

            if utils.isTGVTrue(self.getOption('association_vocabulary', assoc, '0')):
                # remember this vocab-name and if set its portal_type
                currentproduct = package.getProductName()
                if not currentproduct in self.vocabularymap.keys():
                    self.vocabularymap[currentproduct] = {}
                type = self.getOption('association_vocabularytype', assoc, 'SimpleVocabulary')
                if not assoc.getCleanName() in self.vocabularymap[currentproduct].keys():
                    self.vocabularymap[currentproduct][assoc.getCleanName()] = (
                                                    type,
                                                    'SimpleVocabularyTerm'
                    )
                else:
                    print "warning: vocabulary with name %s defined more than once." % assoc.getCleanName()
                if inverse_relation_name and not inverse_relation_name in self.vocabularymap[currentproduct].keys():
                    self.vocabularymap[currentproduct][inverse_relation_name] = (
                                                    type,
                                                    'SimpleVocabularyTerm'
                    )                    
            package.num_generated_relations += 1

        if package.num_generated_relations:
            self.makeDir(os.path.join(package.getFilePath(), 'data', 
                                      'relations.xml'))
            of=self.makeFile(os.path.join(package.getFilePath(),'data',
                                          'relations.xml'))
            print >>of,doc.toprettyxml()
            of.close()

    def generateProduct(self, root):
        dirMode=0
        outfile=None

        if self.generate_packages and root.getCleanName() not in self.generate_packages:
            log.info("%sSkipping package '%s'.",
                     '    '*self.infoind,
                     root.getCleanName())
            return

        dirMode=1
        if root.hasStereoType(self.stub_stereotypes, umlprofile=self.uml_profile):
            log.debug("Skipping stub Product '%s'.",
                      root.getName())
            return

        log.info("Starting new Product: '%s'.",
                 root.getName())

        # increment indent of output
        self.infoind += 1

        # before generate a Product we need to push the current permissions on a
        # stack in orderto reinitialize the permissions
        self.creation_permission_stack.append(self.creation_permissions)
        self.creation_permissions = []

        #create the directories
        self.makeDir(root.getFilePath())
        self.makeDir(os.path.join(root.getFilePath(),'skins'))
        
        # create skins directories
        # in agx 1.6 we keep the oldschool single directory with Products name
        # if it already exists (bbb). if skins is empty we create by default the 
        # templates, images and styles directories prefixes with a lowercase 
        # product name and _. this can get an override by a tagged value
        # skin_directories, which is a comma separated list of alternatives
        # for templates, images and styles, but they will get prefixed too, to
        # not expose namesapce conflicts.
        # [jensens]
        
        skindirs = root.getTaggedValue('skin_directories', 
                                       'templates, styles, images')
        oldschooldir = os.path.join(root.getFilePath(),'skins',
                                    root.getProductModuleName())
        if not os.path.exists(oldschooldir):
            skindirs = [sd.strip() for sd in skindirs.split(',')]
            for skindir in skindirs:
                if not sd:
                    continue
                sd = "%s_%s" % (root.getName().lower(), skindir)
                sdpath = os.path.join(root.getFilePath(),'skins', sd)
                self.makeDir(sdpath)
                log.info("Keeping/ creating skinsdir at: %s" % sdpath)
        else:
            log.info("Keeping old school skindir at: '%s'.", oldschooldir)
        # prepare messagecatalog
        if has_i18ndude and self.build_msgcatalog:
            self.makeDir(os.path.join(root.getFilePath(), 'i18n'))
            filepath = os.path.join(root.getFilePath(), 'i18n', 'generated.pot')
            if not os.path.exists(filepath):
                PotTemplate = open(os.path.join(self.templateDir,
                                                'generated.pot')).read()
                authors, emails, authorline = self.getAuthors(root)
                PotTemplate = PotTemplate % {
                    'author':', '.join(authors) or 'unknown author',
                    'email':', '.join([email[1:-1] for email in emails]) or \
                            'unknown@email.address',
                    'year': str(time.localtime()[0]),
                    'datetime': time.ctime(),
                    'charset': 'UTF-8',
                    'package': root.getProductName(),
                }
                of = self.makeFile(filepath)
                of.write(PotTemplate)
                of.close()
            self.msgcatstack.append(msgcatalog.MessageCatalog(
                    filename=os.path.join(self.targetRoot, filepath)))

        package = root
        self.generateRelations(root)
        self.generatePackage(root)

        #start Workflow creation
        wfg = WorkflowGenerator(package, self)
        wfg.generateWorkflows()

        # write messagecatalog
        if has_i18ndude and self.build_msgcatalog:
            filepath = os.path.join(root.getFilePath(), 'i18n', 'generated.pot')
            of = self.makeFile(filepath) or open(filepath, 'w')
            pow = msgcatalog.POWriter(of, self.msgcatstack.pop())
            pow.write(sort=True, msgstrToComment=True)
            of.close()

        # post-creation
        self.infoind -= 1
        self.creation_permissions = self.creation_permission_stack.pop()

    def parseAndGenerate(self):

        # and now start off with the class files
        self.generatedModules=[]

        suff = os.path.splitext(self.xschemaFileName)[1].lower()
        log.info("Parsing...")
        if suff.lower() in ('.xmi','.xml', '.uml'):
            log.debug("Opening xmi...")
            self.root = root= XMIParser.parse(self.xschemaFileName,
                                              packages=self.generate_packages,
                                              generator=self,
                                              generate_datatypes=self.generate_datatypes)
            log.debug("Created a root XMI parser.")
        elif suff.lower() in ('.zargo','.zuml','.zip'):
            log.debug("Opening %s ..." % suff.lower())
            zf=ZipFile(self.xschemaFileName)
            xmis=[n for n in zf.namelist() if os.path.splitext(n)[1].lower()in ['.xmi','.xml']]
            assert(len(xmis)==1)
            buf=zf.read(xmis[0])
            self.root=root=XMIParser.parse(xschema=buf,
                packages=self.generate_packages, generator=self,
                generate_datatypes=self.generate_datatypes)
        else:
            raise TypeError,'input file not of type .xmi, .xml, .zargo, .zuml'

        if self.outfilename:
            log.debug("We've got an self.outfilename: %s.",
                      self.outfilename)
            lastPart = os.path.split(self.outfilename)[1]
            log.debug("We've split off the last directory name: %s.",
                      lastPart)
            # [Reinout 2006-11-05]: We're not setting the root's
            # name from the outfilename anymore. That prevents
            # (amongst others) Optilude from generating some
            # product into a directory named "trunk", for
            # instance.
            #root.setName(lastPart)
            #log.debug("Set the name of the root generator to that"
            #          " directory name.")
            existingName = root.getName()
            if not existingName == lastPart:
                log.warn("Not setting the product's name to '%s', "
                         "this was the old behaviour. Just name your "
                         "class diagram according to your product "
                         "name. ",
                         lastPart)
            root.setOutputDirectoryName(self.outfilename)
        else:
            log.debug("No outfilename present, not changing the "
                      "name of the root generator.")
        log.info("Directory in which we're generating the files: '%s'.",
                 self.outfilename)
        log.info('Generating...')
        if not has_enhanced_strip_support:
            log.warn("Can't build i18n message catalog. Needs 'python 2.3' or later.")
        if self.build_msgcatalog and not has_i18ndude:
            log.warn("Can't build i18n message catalog. Module 'i18ndude' not found.")
        if not XMIParser.has_stripogram:
            log.warn("Can't strip html from doc-strings. Module 'stripogram' not found.")
        self.generateProduct(root)
    
    def _getSubtypes(self, element):
        """extract the allowed subtypes
        """
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
        
        aggregatedClasses = element.getRefs() + \
                            element.getSubtypeNames(recursive=recursive,
                                                    filter=['class'])
        
        if element.getTaggedValue('allowed_content_types'):
            #aggregatedClasses = [e for e in aggregatedClasses] # hae?
            for e in element.getTaggedValue('allowed_content_types').split(','):
                e = e.strip()
                if e not in aggregatedClasses:
                    aggregatedClasses.append(e)
        
        # also check if the parent classes can have subobjects
        baseaggregatedClasses = []
        for b in element.getGenParents():
            baseaggregatedClasses.extend(b.getRefs())
            baseaggregatedClasses.extend(b.getSubtypeNames(recursive=1))
        
        #allowed_content_classes
        parentAggregates = []
        
        if utils.isTGVTrue(element.getTaggedValue('inherit_allowed_types', \
           True)) and element.getGenParents():
            for gp in element.getGenParents():
                if gp.hasStereoType(self.python_stereotype,
                                    umlprofile=self.uml_profile):
                    continue
                pt = gp.getTaggedValue('portal_type', None)
                if pt is not None:
                    parentAggregates.append(pt)
                else:
                    parentAggregates.append(gp.getCleanName())

        ret = {
            'parent_types': parentAggregates,
            'aggregated_classes': aggregatedClasses,
        }
        return ret
        
    def _getTypeDefinitions(self, defs, package, productname):
        """Iterate recursice through package and create class definitions
        """
        classes = package.getClasses()
        if not classes:
            for package in package.getPackages():
                self._getTypeDefinitions(defs, package, productname)
        
        for pclass in classes:
            if not self._isContentClass(pclass):
                continue
            
            if pclass.hasStereoType(['tool', 'portal_tool', 'flavor', 'interface']):
                continue
            
            fti = self._getFTI(pclass)
            typedef = dict()
            typedef.update(fti)
            typedef['name'] = pclass.getCleanName()
            
            #if utils.isTGVTrue(pclass.getTaggedValue('use_dynamic_view', '1')):
            #    typedef['meta_type'] = 'Factory-based Type Information ' + \
            #                           'with dynamic views'
            #else:
            #    typedef['meta_type'] = 'Factory-based Type Information'
            typedef['meta_type'] = 'Factory-based Type Information ' + \
                                   'with dynamic views'
            
            typedef['content_meta_type'] = pclass.getCleanName()
            typedef['product_name'] = productname
            typedef['factory'] = 'add%s' % pclass.getCleanName()
            
            allowed_types = self._getSubtypes(pclass)['aggregated_classes']
            typedef['allowed_content_types'] = allowed_types
            
            # check if allow_discussion has to be set to None as default
            # further check for boolean wrapper
            typedef['allow_discussion'] = pclass.getTaggedValue( \
                                              'allow_discussion', 'False')
            
            folderish = self.elementIsFolderish(pclass)
            if folderish:
                typedef['type_aliases'] = atmaps.DEFAULT_FOLDERISH_ALIASES
            else:
                typedef['type_aliases'] = atmaps.DEFAULT_ALIASES
            
            typedef['suppl_views'] = eval(typedef['suppl_views'])
            if not typedef['suppl_views']: #  and folderish:
                typedef['suppl_views'] = (typedef['immediate_view'],)
            
            if self.getOption('plone_target_version', pclass, '3.0') == '3.0':
                default_actions = atmaps.DEFAULT_ACTIONS_3_0
            else:
                default_actions = atmaps.DEFAULT_ACTIONS_2_5
                
            #actions = self.getMethodActionsDict(pclass)
            #for action in default_actions:
            #    for act in actions:
                    
            typedef['type_actions'] = default_actions
                
            defs.append(typedef)
    
    def _isContentClass(self, cclass):
        """Check if given class is content class
        """
        if cclass.isInternal() \
         or cclass.getName() in self.hide_classes \
         or cclass.getName().lower().startswith('java::'): # Enterprise Architect fix!
            log.debug("Ignoring unnecessary class '%s'.", cclass.getName())
            return False
        if cclass.hasStereoType(self.stub_stereotypes,
                                umlprofile=self.uml_profile):
            log.debug("Ignoring stub class '%s'.", cclass.getName())
            return False
        return True
    
    def _getFTI(self, cclass):
        """Return the FTI information of the content class
        """
        fti = dict()
        fti['immediate_view'] = self.getOption('immediate_view',
                                               cclass,
                                               default='base_view')        
        
        fti['default_view'] = self.getOption('default_view',
                                             cclass,
                                             default=fti['immediate_view'])
        
        fti['suppl_views'] = self.getOption('suppl_views',
                                            cclass,
                                            default='()')

        fti['global_allow'] = True
        if cclass.isDependent():
            # WARNING! isDependent() doesn't seem to work,
            # aggregates and compositions aren't detected.
            # 2005-05-11 reinout
            fti['global_allow'] = False
        
        # Or if it is a hidden element
        if cclass.hasStereoType('hidden', umlprofile=self.uml_profile):
            fti['global_allow'] = False
        
        # Or if it is a tool-like thingy
        if (cclass.hasStereoType(self.portal_tools,
                                 umlprofile=self.uml_profile) or \
            cclass.hasStereoType(self.vocabulary_item_stereotype,
                                 umlprofile=self.uml_profile) or \
            cclass.hasStereoType(self.remember_stereotype,
                                 umlprofile=self.uml_profile) or \
            cclass.isAbstract()):
            fti['global_allow'] = False
        
        # But the tagged value overwrites all
        tgvglobalallow = self.getOption('global_allow',
                                        cclass,
                                        default=None)
        if utils.isTGVFalse(tgvglobalallow):
            fti['global_allow'] = False
        if utils.isTGVTrue(tgvglobalallow):
            fti['global_allow'] = True

        has_content_icon=''
        content_icon = cclass.getTaggedValue('content_icon')
        if not content_icon:
            # If an icon file with the default name exists in the skin, do not
            # comment out the icon definition
            fti['content_icon'] = cclass.getCleanName()+'.gif'
            icon_filename = os.path.join(self.getSkinPath(cclass),
                                         content_icon)
        else:
            fti['content_icon'] = content_icon

        # If we are generating a tool, include the template which sets
        # a tool icon
        if cclass.hasStereoType(self.portal_tools,
                                umlprofile=self.uml_profile):
            fti['is_tool'] = True
        else:
            fti['is_tool'] = False

        toolicon = cclass.getTaggedValue('toolicon')
        if not toolicon:
            fti['toolicon'] = cclass.getCleanName()+'.gif'
        else:
            fti['toolicon'] = toolicon


        # Filter content types?
        # Filter by default if it's a folder-like thingy
        filter_default = self.elementIsFolderish(cclass)
        # But a tagged value overrides
        fti['filter_content_types'] = utils.isTGVTrue(cclass.getTaggedValue( \
                                                      'filter_content_types',
                                                      filter_default))
        # Set a type name and description.
        fti['type_name'] = cclass.getTaggedValue('archetype_name') or \
                           cclass.getTaggedValue('label') or \
                           cclass.getName ()
        fti['type_name_lc'] = fti['type_name'].lower()                        
        fti['type_description'] = utils.getExpression( \
                                      cclass.getTaggedValue('typeDescription',
                                                            fti['type_name']))        
        return fti
    