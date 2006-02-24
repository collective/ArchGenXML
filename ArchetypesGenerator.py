#----------------------------------------------------------------------------
# Name:        ArchetypesGenerator.py
# Purpose:     main class generating archetypes code out of an UML-model
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# Copyright:   (c) 2003-2005 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys
import time
import os.path
import logging

import utils
from odict import odict
from codesnippets import *

from xml.dom import minidom
from zipfile import ZipFile
from StringIO import StringIO

# AGX-specific imports
import PyParser
import XMIParser
from UMLProfile import UMLProfile

from BaseGenerator import BaseGenerator
from WorkflowGenerator import WorkflowGenerator

from documenttemplate.documenttemplate import HTML

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

    getCleanName = getName
    getFilePath = getName
    getModuleFilePath = getName
    getProductModuleName = getName
    getProductName = getName

    def hasStereoType(self, s, umlprofile=None):
        return True

    def getClasses(self, *a, **kw):
        return []

    getInterfaces = getClasses
    getPackages = getClasses
    getStateMachines = getClasses
    getAssociations = getClasses

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


class ArchetypesGenerator(BaseGenerator):

    generator_generator = 'archetypes'
    default_class_type = 'content_class'
    default_interface_type = 'z2'

    uml_profile = UMLProfile(BaseGenerator.uml_profile)

    uml_profile.addStereoType(
        'portal_tool', ['XMIClass'],
        description='Turns the class into a portal tool.')

    uml_profile.addStereoType(
        'stub', ['XMIClass', 'XMIModel', 'XMIPackage'],
        description='Prevents a class/package/model from being generated.')

    uml_profile.addStereoType(
        'odStub', ['XMIClass', 'XMIModel', 'XMIPackage'],
        description='Prevents a class/package/model from being generated. '
        "Same as '<<stub>>'.")

    uml_profile.addStereoType(
        'content_class', ['XMIClass'],
        dispatching=1,
        generator='generateArchetypesClass',
        description='TODO')

    uml_profile.addStereoType(
        'z2', ['XMIInterface'],
        dispatching=1,
        generator='generateZope2Interface',
        description='Generates a Zope 2 Interface inheriting from Zope.Interface.Base.')

    uml_profile.addStereoType(
        'tests', ['XMIPackage'],
        description='Treats a package as test package. Inside such a test '
        "package, you need at a '<<plone_testcase>>' and a "
        "'<<setup_testcase>>'.")

    uml_profile.addStereoType(
        'plone_testcase', ['XMIClass'],
        dispatching=1,
        template='tests/PloneTestcase.py',
        generator='generateBaseTestcaseClass',
        description='Turns a class into the (needed) base class for all '
        "other '<<testcase>>' and '<<doc_testcase>>' classes "
        "inside a '<<test>>' package.")

    uml_profile.addStereoType(
        'testcase', ['XMIClass'],
        dispatching=1,
        template='tests/GenericTestcase.py',
        generator='generateTestcaseClass',
        description='Turns a class into a testcase. It must subclass a '
        "'<<plone_testcase>>'. Adding an interface arrow to "
                    'another class automatically adds that class\'s '
                    'methods to the testfile for testing.')

    uml_profile.addStereoType(
        'doc_testcase', ['XMIClass'],
        dispatching=1,
        template='tests/DocTestcase.py',
        generator='generateDocTestcaseClass',
        description='Turns a class into a doctest class. It must subclass '
        "a '<<plone_testcase>>'.")

    uml_profile.addStereoType(
        'setup_testcase', ['XMIClass'],
        dispatching=1,
        generator='generateTestcaseClass',
        template='tests/SetupTestcase.py',
        description='Turns a class into a testcase for the setup, with '
                    'pre-defined common checks.')

    uml_profile.addStereoType(
        'interface_testcase', ['XMIClass'],
        dispatching=1,
        generator='generateTestcaseClass',
        template='tests/InterfaceTestcase.py',
        description='Turns a class into a testcase for the interfaces.')

    # This looks like a tagged value...
    #uml_profile.addStereoType(
    #    'relation_implementation',
    #    ['XMIClass', 'XMIAssociation', 'XMIPackage'],
    #    default='basic',
    #    description='specifies how relations should be implemented')

    uml_profile.addStereoType(
        'field', ['XMIClass'],
        dispatching=1,
        generator='generateFieldClass',
        template='field.py',
        description='TODO')

    uml_profile.addStereoType(
        'widget', ['XMIClass'],
        dispatching=1,
        generator='generateWidgetClass',
        template='widget.py',
        description='TODO')

    uml_profile.addStereoType(
        'value_class', ['XMIDependency'],
        description='Declares a class to be used as value class for a '
        "certain field class (see '<<field>>' stereotype).")

    uml_profile.addStereoType(
        'CMFMember', ['XMIClass'],
        description='The class will be treated as a CMFMember member '
                    'type. It will derive from CMFMember\'s Member '
                    'class and be installed as a member data type. '
        "Identical to '<<member>>'.")

    uml_profile.addStereoType(
        'member', ['XMIClass'],
        description='The class will be treated as a CMFMember member '
                    'type. It will derive from CMFMember\'s Member '
                    'class and be installed as a member data type. '
        "Identical to '<<CMFMember>>'.")

    uml_profile.addStereoType(
        'action', ['XMIMethod'],
        description='Generate a CMF action which will be available on the '
                    'object. The tagged values "action" (defaults to method '
                    'name), "id" (defaults to method name), "category" '
                    '(defaults to "object"), "label" (defaults to method '
                    'name), "condition" (defaults to empty), and "permission" '
                    '(defaults to empty) set on the method and mapped to '
                    'the equivalent fields of any CMF action can be used to '
                    'control the behaviour of the action.')

    uml_profile.addStereoType(
        'archetype', ['XMIClass'],
        description='Explicitly specify that a class represents an Archetypes '
                    'type. This may be necessary if you are including a class '
                    'as a base class for another class and ArchGenXML is unable '
                    'to determine whether the parent class is an Archetype '
                    'or not. Without knowing that the parent class in an '
                    'Archetype, ArchGenXML cannot ensure that the parent\'s '
                    'schema is available in the derived class.')

    uml_profile.addStereoType(
        'btree', ['XMIClass'],
        description="Like '<<folder>>', it generates a folderish object. "
                    'But it uses a BTree folder for support of large amounts '
        "of content. The same as '<<large>>'.")

    uml_profile.addStereoType(
        'large', ['XMIClass'],
        description="Like '<<folder>>', it generates a folderish object. "
                    'But it uses a BTree folder for support of large amounts '
        "of content. The same as '<<large>>'.")

    uml_profile.addStereoType(
        'folder', ['XMIClass'],
        description='Turns the class into a folderish object. When a UML '
                    'class contains or aggregates other classes, it is '
                    'automatically turned into a folder; this stereotype '
                    'can be used to turn normal classes into folders, too.')

    uml_profile.addStereoType(
        'ordered', ['XMIClass'],
        description='For folderish types, include folder ordering support. '
                    'This will allow the user to re-order items in the folder '
                    'manually.')

    uml_profile.addStereoType(
        'form', ['XMIMethod'],
        description="Generate an action like with the '<<action>>' stereotype, "
                    'but also copy an empty controller page template to the '
                    'skins directory with the same name as the method and set '
                    'this up as the target of the action. If the template '
                    'already exists, it is not overwritten.')

    uml_profile.addStereoType(
        'hidden', ['XMIClass'],
        description='Generate the class, but turn off "global_allow", thereby '
                    'making it unavailable in the portal by default. Note that '
                    'if you use composition to specify that a type should be '
                    'addable only inside another (folderish) type, then '
                    '"global_allow" will be turned off automatically, and the '
                    'type be made addable only inside the designated parent. '
                    '(You can use aggregation instead of composition to make a '
                    'type both globally addable and explicitly addable inside '
                    'another folderish type).')

    uml_profile.addStereoType(
        'mixin', ['XMIClass'],
        description='Don\'t inherit automatically from "BaseContent" and so. '
                    'This makes the class suitable as a mixin class. See also '
        "'<<archetype>>'.")

    uml_profile.addStereoType(
        'portlet', ['XMIMethod'],
        description='Create a simple portlet page template with the same '
                    'name as the method. You can override the name by setting '
                    'the "view" tagged value on the method. If you add a '
                    'tagged value "autoinstall" and set it to "left" or '
                    '"right", the portlet will be automatically installed '
                    'with your product in either the left or the right slot. '
                    'If the page template already exists, it will not be '
                    'overwritten.')

    uml_profile.addStereoType(
        'portlet_view', ['XMIMethod'],
        description='Create a simple portlet page template with the same '
                    'name as the method. You can override the name by setting '
                    'the "view" tagged value on the method. If you add a '
                    'tagged value "autoinstall" and set it to "left" or '
                    '"right", the portlet will be automatically installed '
                    'with your product in either the left or the right slot. '
                    'If the page template already exists, it will not be '
        "overwritten. Same as '<<portlet>>'.")

    uml_profile.addStereoType(
        'tool', ['XMIClass'],
        description='Turns the class into a portal tool. Similar to '
        "'<<portal_tool>>'.")

    uml_profile.addStereoType(
        'variable_schema', ['XMIClass'],
        description='Include variable schema support in a content type by '
                    'deriving from the VariableSchema mixin class.')

    uml_profile.addStereoType(
        'view', ['XMIMethod'],
        description="Generate an action like with the '<<action>>' stereotype, "
                    'but also copy an empty page template to the skins '
                    'directory with the same name as the method and set this '
                    'up as the target of the action. If the template exists, '
                    'it is not overwritten.')

    uml_profile.addStereoType(
        'vocabulary', ['XMIClass'],
        description='TODO')

    uml_profile.addStereoType(
        'vocabulary_term', ['XMIClass'],
        description='TODO')

    # The defaults here are already handled by OptionParser
    # (And we want only a single authorative source of information :-)

    # force = 1
    # unknownTypesAsString = 0
    # generateActions = 1
    # generateDefaultActions = 0
    # prefix = ''
    # parse_packages = [] # Packages to scan for classes
    # generate_packages = [] # Packages to be generated
    # noclass = 0 # If set no module is reverse engineered,
    #             # just an empty project + skin is created
    # ape_support = 0 # Generate APE config and serializers/gateways?
    # method_preservation = 1 # Should the method bodies be preserved?
    # i18n_content_support = 0

    build_msgcatalog = 1
    striphtml = 0

    reservedAtts = ['id']
    portal_tools = ['portal_tool', 'tool']
    variable_schema = 'variable_schema'

    stub_stereotypes = ['odStub','stub']
    archetype_stereotype = ['archetype']
    vocabulary_item_stereotype = ['vocabulary_term']
    vocabulary_container_stereotype = ['vocabulary']
    cmfmember_stereotype = ['CMFMember', 'member']
    python_stereotype = ['python', 'python_class']
    folder_stereotype = ['folder', 'ordered', 'large', 'btree']

    i18n_at = ['i18n-archetypes', 'i18n', 'i18n-at']
    generate_datatypes = ['field', 'compound_field']

    left_slots = []
    right_slots = []

    # Should be 'Products.' be prepended to all absolute paths?
    force_plugin_root = 1

    customization_policy = 0
    backreferences_support = 0

    # Contains the parsed sources by class names (for preserving method codes)
    parsed_class_sources = {}

    # Contains the parsed sources (for preserving method codes)
    parsed_sources = []

    # TaggedValues that are not strings, e.g. widget or vocabulary
    nonstring_tgvs = ['widget', 'vocabulary', 'required', 'precision',
                      'storage', 'enforceVocabulary', 'multiValued',
                      'visible', 'validators', 'validation_expression',
                      'sizes', 'original_size', 'max_size', 'searchable',
                      'show_hm']

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
        log.debug("Initializing ArchetypesGenerator. "
                  "We're being passed a file '%s' and keyword "
                  "arguments %r.", xschemaFileName, kwargs)
        self.infoind = 0
        self.xschemaFileName = xschemaFileName
        self.__dict__.update(kwargs)
        log.debug("After copying over the keyword arguments (read: "
                  "OptionParser's options), outfilename is '%s'.",
                  self.outfilename)
        if self.outfilename:
            # Remove trailing delimiters on purpose
            if self.outfilename[-1] in ('/','\\'):
                self.outfilename = self.outfilename[:-1]
            log.debug("Stripped off the eventual trailing slashes: '%s'.",
                      self.outfilename)

            # Split off the parent directory part so that
            # we can call ArchgenXML.py -o /tmp/prod prod.xmi
            path = os.path.split(self.outfilename)
            self.targetRoot = path[0]
            log.debug("Targetroot is set to everything except the last "
                      "directory in the outfilename: %s.", self.targetRoot)
        else:
            log.debug("Outfilename hasn't been set. Setting "
                      "targetroot to the current directory.")
            self.targetRoot = '.'
        log.debug("Initialization finished.")

    def makeFile(self, fn, force=1, binary=0):
        log.debug("Calling makeFile to create '%s'.", fn)
        ffn = os.path.join(self.targetRoot, fn)
        log.debug("Together with the targetroot that means '%s'.", ffn)
        return utils.makeFile(ffn, force=force, binary=binary)

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
        generate_expression_validator = False

        for att in element.getAttributeDefs():
            if att.getTaggedValue('validation_expression'):
                generate_expression_validator = True

        if generate_expression_validator:
            print >> out, 'from Products.validation.validators import ExpressionValidator'

        # Check for necessity to import ArrayField
        import_array_field = False
        for att in element.getAttributeDefs():
            if att.getUpperBound() != 1:
                import_array_field = True
                break

        if import_array_field:
            print >>out, 'from Products.CompoundField.ArrayField import ArrayField'

        start_marker = True
        for iface in self.getAggregatedInterfaces(element):
            if start_marker:
                print >>out, 'from Products.Archetypes.AllowedTypesByIface import AllowedTypesByIfaceMixin'
                start_marker = False
            print >>out, 'from %s import %s' % (iface.getQualifiedModuleName(forcePluginRoot=True),iface.getCleanName())

        return out.getvalue()

    def addMsgid(self, msgid, msgstr, element, fieldname):
        """Adds a msgid to the catalog if it not exists.

        If it exists and not listed in occurrences, then add its occurence.
        """
        if has_i18ndude and self.build_msgcatalog and len(self.msgcatstack):
            msgcat = self.msgcatstack[len(self.msgcatstack)-1]
            package = element.getPackage()
            module_id = os.path.join(element.getPackage().getFilePath(includeRoot=0),
                                     element.getName()+'.py')
            if isinstance(msgstr, unicode):
                msgstr = msgstr.encode('utf8')
            try:
                #i18ndude 2.0
                msgcat.add(msgid, msgstr=msgstr, references=[module_id])
            except:
                # old i18ndude
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

    def generateMethodActions(self, element):
        log.debug("Generating method actions...")
        outfile=StringIO()
        print >> outfile
        log.debug("First finding our methods.")
        for m in element.getMethodDefs():
            method_name = m.getName()
            code = utils.indent(m.getTaggedValue('code', ''), 1)
            if m.hasStereoType(['action', 'view', 'form'], umlprofile=self.uml_profile):
                log.debug("Method has stereotype action/view/form.")
                action_name = m.getTaggedValue('action','').strip()
                if not action_name:
                    log.debug("No tagged value 'action', trying '%s' with a "
                              "default to the methodname.",
                              m.getStereoType())
                    action_name=m.getTaggedValue(m.getStereoType(), method_name).strip()
                log.debug("Ok, generating %s for %s.",
                          m.getStereoType(), action_name)
                dict={}

                if not action_name.startswith('string:') and not action_name.startswith('python:'):
                    action_target='string:${object_url}/'+action_name
                else:
                    action_target=action_name

                dict['action']=utils.getExpression(action_target)
                dict['action_category']=utils.getExpression(m.getTaggedValue('category','object'))
                dict['action_id']=m.getTaggedValue('id',method_name)
                dict['action_label'] = m.getTaggedValue('action_label') or \
                                       m.getTaggedValue('label',method_name)
                # action_label is deprecated and for backward compability only!
                dict['permission']=utils.getExpression(m.getTaggedValue('permission','View'))

                condition=m.getTaggedValue('condition') or '1'
                dict['condition']='python:'+condition

                if not (m.hasTaggedValue('create_action') and utils.isTGVFalse(m.getTaggedValue('create_action'))):
                    print >>outfile, ACT_TEMPL % dict

            if m.hasStereoType('view', umlprofile=self.uml_profile):
                f=self.makeFile(os.path.join(self.getSkinPath(element),action_name+'.pt'),0)
                if f:
                    templdir=os.path.join(sys.path[0],'templates')
                    viewTemplate=open(os.path.join(templdir,'action_view.pt')).read()
                    f.write(viewTemplate % code)

            elif m.hasStereoType('form', umlprofile=self.uml_profile):
                f=self.makeFile(os.path.join(self.getSkinPath(element),action_name+'.cpt'),0)
                if f:
                    templdir=os.path.join(sys.path[0],'templates')
                    viewTemplate=open(os.path.join(templdir,'action_view.pt')).read()
                    f.write(viewTemplate % code)

            elif m.hasStereoType(['portlet_view','portlet'], umlprofile=self.uml_profile):
                view_name=m.getTaggedValue('view').strip() or method_name
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
                    f.write(viewTemplate % {'method_name':method_name})

        res=outfile.getvalue()
        return res


    def generateAdditionalImports(self, element):
        outfile = StringIO()

        if element.hasAssocClass:
            print >> outfile,'from Products.Archetypes.ReferenceEngine import ContentReferenceCreator'

        useRelations = 0

        #check wether we have to import Relation's Relation Field
        for rel in element.getFromAssociations():
            if self.getOption('relation_implementation',rel,'basic') == 'relations':
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
        if element.hasAttributeWithTaggedValue('vocabulary:type','ATVocabularyManager'):
            print >> outfile, 'from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary'

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
        suppl_views = element.getTaggedValue('suppl_views') or '()'

        # In principle, allow globally
        global_allow = True
        # Unless it is only contained by another element
        if element.isDependent():
            # WARNING! isDependent() doesn't seem to work,
            # aggregates and compositions aren't detected.
            # 2005-05-11 reinout
            global_allow = False
        # Or if it is a hidden element
        if element.hasStereoType('hidden', umlprofile=self.uml_profile):
            global_allow = False
        # Or if it is a tool-like thingy
        if (element.hasStereoType(self.portal_tools, umlprofile=self.uml_profile) or
            element.hasStereoType(self.vocabulary_item_stereotype, umlprofile=self.uml_profile) or
            element.hasStereoType(self.cmfmember_stereotype, umlprofile=self.uml_profile) or
            element.isAbstract()):
            global_allow = False
        # But the tagged value overwrites all
        if utils.isTGVFalse(element.getTaggedValue('global_allow')):
            global_allow = False
        if utils.isTGVTrue(element.getTaggedValue('global_allow')):
            global_allow = True


        has_content_icon=''
        content_icon=element.getTaggedValue('content_icon')
        if not content_icon:
            # If an icon file with the default name exists in the skin, do not 
            # comment out the icon definition
            content_icon = element.getCleanName()+'.gif'
            icon_filename = os.path.join(self.getSkinPath(element), content_icon)
            if not os.path.isfile(icon_filename):
                has_content_icon='#'

        # If we are generating a tool, include the template which sets
        # a tool icon
        if element.hasStereoType(self.portal_tools, umlprofile=self.uml_profile):
            ftiTempl += TOOL_FTI_TEMPL

        has_toolicon=''
        toolicon = element.getTaggedValue('toolicon')
        if not toolicon:
            has_toolicon='#'
            toolicon = element.getCleanName()+'.gif'

        # Allow discussion?
        allow_discussion = element.getTaggedValue('allow_discussion', False)

        # Filter content types?
        # Filter by default if it's a folder-like thingy
        filter_default = self.elementIsFolderish(element)
        # But a tagged value overrides
        filter_content_types = utils.isTGVTrue(element.getTaggedValue('filter_content_types',
                                                                filter_default))
        # Set a type description.

        typeName = element.getTaggedValue('archetype_name') or \
                    element.getTaggedValue('label') or \
                    element.getName ()

        typeDescription = utils.getExpression(element.getTaggedValue('typeDescription', typeName))

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
            'suppl_views'          : suppl_views,
            'filter_content_types' : filter_content_types,
            'typeDescription'      : typeDescription,
            'type_name_lc'         : element.getName().lower()}

        return res

    # TypeMap for Fields, format is
    #   type: {field: 'Y',
    #          lines: [key1=value1,key2=value2, ...]
    #   ...
    #   }
    typeMap= {
        'string': {'field': 'StringField',
                   'map': {},
                   },
        'text':  {'field': 'TextField',
                  'map': {},
                  },
        'richtext': {'field': 'TextField',
                     'map': {'default_output_type':"'text/html'",
                             'allowable_content_types': "('text/plain', 'text/structured', 'text/html', 'application/msword',)",
                             },
                     },
        'selection': {'field': 'StringField',
                      'map': {},
                      },
        'multiselection': {'field': 'LinesField',
                           'map': {'multiValued': '1',
                                   },
                           },
        'integer': {'field': 'IntegerField',
                    'map': {},
                    },
        'float': {'field': 'FloatField',
                  'map': {},
                  },
        'fixedpoint': {'field': 'FixedPointField',
                       'map': {},
                       },
        'lines': {'field': 'LinesField',
                  'map': {},
                  },
        'date': {'field': 'DateTimeField',
                 'map': {},
                 },
        'image': {'field': 'ImageField',
                  'map': {'storage': 'AttributeStorage()',
                          },
                  },
        'file': {'field': 'FileField',
                 'map': {'storage': 'AttributeStorage()',
                         },
                 },
        'reference': {'field': 'ReferenceField',
                      'map': {},
                      },
        'relation': {'field': 'RelationField',
                     'map': {},
                     },
        'backreference': {'field': 'BackReferenceField',
                          'map': {},
                          },
        'boolean': {'field': 'BooleanField',
                    'map': {},
                    },
        'computed': {'field': 'ComputedField',
                     'map': {},
                     },
        'photo': {'field': 'PhotoField',
                  'map': {},
                  },
        'generic': {'field': '%(type)sField',
                    'map': {},
                    },
        }

    widgetMap={
        'fixedpoint': 'DecimalWidget' ,
        'float': 'DecimalWidget',
        'text': 'TextAreaWidget',
        'richtext': 'RichWidget',
        'file': 'FileWidget',
        'date' : 'CalendarWidget',
        'selection' : 'SelectionWidget',
        'multiselection' : 'MultiSelectionWidget',
    }

    coerceMap={
        'xs:string': 'string',
        'xs:int': 'integer',
        'xs:integer': 'integer',
        'xs:byte': 'integer',
        'xs:double': 'float',
        'xs:float': 'float',
        'xs:boolean': 'boolean',
        'ofs.image': 'image',
        'ofs.file': 'file',
        'xs:date': 'date',
        'datetime': 'date',
        'list': 'lines',
        'liste': 'lines',
        'image': 'image',
        'int': 'integer',
        'bool': 'boolean',
        'dict': 'string',
        'String': 'string',
        '': 'string',     #
        None:'string',
    }

    hide_classes=['EARootClass','int','float','boolean','long','bool',
        'void','string', 'dict','tuple','list','object','integer',
        'java::lang::int','java::lang::string','java::lang::long',
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
                    log.warn("Empty tagged value for tag '%s' in field '%s'.",
                             k, element.getName())
                    continue

                if k not in self.nonstring_tgvs:
                    v=utils.getExpression(v)
                # [optilude] Permit python: if people forget they
                # don't have to (I often do!)
                else:
                    if v.startswith('python:'):
                        v = v[7:]

                map.update({k: v})
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
        check_map['description_msgid']  = "'%s_help_%s'" % (modulename,fieldname)
        check_map['i18n_domain']        = "'%s'" % modulename

        wt={} # helper
        if tgv.has_key('widget'):
            # Custom widget defined in attributes
            custom = True
            formatted=''
            for line in tgv['widget'].split('\n'):
                if formatted:
                    line = utils.indent(line.strip(), 1)
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
                    val=utils.getExpression(val)
                # [optilude] Permit python: if people forget they don't have to (I often do!)
                else:
                    if val.startswith ('python:'):
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
            if 'description' not in widgetmap.keys() and 'description_msgid' in widgetmap.keys() \
                and not self.default_description_generation:
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

            widgetcode += utils.indent( \
                ',\n'.join(['%s=%s' % (key,widgetmap[key]) for key in widgetmap]),
                1,
                skipFirstRow=0) \
                + ',\n'
            widgetcode +=')'

        return widgetcode

    def getFieldFormatted(self,name,fieldtype,map={},doc=None, indent_level=0, rawType='String'):
        """Return the formatted field definitions for the schema.
        """

        log.debug("Trying to get formatted field. name='%s', fieldtype='%s', "
                  "doc='%s', rawType='%s'.", name, fieldtype, doc, rawType)
        res = ''

        # Capitalize only first letter of fields class name, keep camelcase
        a = rawType[0].upper()
        rawType = a + rawType[1:]

        # Add comment
        if doc:
            res += utils.indent(doc, indent_level, '#') + '\n' + res

        # If this is a generic field and the user entered MySpecialField,
        # then don't suffix it with 'field''
        if rawType.endswith('Field'):
            rawType = rawType[:-5]

        res += utils.indent("%s(\n    name='%s',\n" % (
                   fieldtype % {'type': rawType}, name), indent_level)
        if map:
            prepend = utils.indent('', indent_level)
            for key in map:
                if key.find(':')>=0:
                    continue
                lines = map[key]
                if isinstance(lines, (str, unicode)):
                    linebreak = lines.find('\n')

                    if linebreak < 0:
                        linebreak = len(lines)
                    firstline = lines[:linebreak]
                else:
                    firstline = lines

                res += '%s%s=%s' % (prepend, key, firstline)
                if isinstance(lines, (str, unicode)) and linebreak < len(lines):
                    for line in lines[linebreak+1:].split('\n'):
                        res += "\n%s" % utils.indent(line, indent_level+1)

                prepend = ',\n%s' % utils.indent('', indent_level+1)

        res += '\n%s' % utils.indent('),', indent_level) + '\n'

        return res

    def getFieldString(self, element, classelement, indent_level=0):
        ''' gets the schema field code '''
        typename=str(element.type)

        ctype=self.coerceType(typename)

        map = typeMap[ctype]['map'].copy()

        res=self.getFieldFormatted(element.getCleanName(),
            self.typeMap[ctype]['field'].copy(),
            map, indent_level )

        return res

    def addVocabulary(self, element, attr, map):
        # ATVocabularyManager: Add NamedVocabulary to field.
        vocaboptions = {}
        for t in attr.getTaggedValues().items():
            if t[0].startswith('vocabulary:'):
                vocaboptions[t[0][11:]]=t[1]
        if vocaboptions:
            if not 'name' in vocaboptions.keys():
                vocaboptions['name'] = '%s_%s' % (element.getCleanName(), \
                                                  attr.getName())
            if not 'term_type' in vocaboptions.keys():
                vocaboptions['term_type'] = 'SimpleVocabularyTerm'

            if not 'vocabulary_type' in vocaboptions.keys():
                vocaboptions['vocabulary_type'] = 'SimpleVocabulary'

            map.update( {
                'vocabulary':'NamedVocabulary("""%s""")' % vocaboptions['name']
            } )

            # remember this vocab-name and if set its portal_type
            package = element.getPackage()
            currentproduct = package.getProductName()
            if not currentproduct in self.vocabularymap.keys():
                self.vocabularymap[currentproduct] = {}

            if not vocaboptions['name'] in self.vocabularymap[currentproduct].keys():
                self.vocabularymap[currentproduct][vocaboptions['name']] = (
                                                vocaboptions['vocabulary_type'],
                                                vocaboptions['term_type']
                )
            else:
                log.warn("Vocabulary with name '%s' defined more than once.",
                         vocaboptions['name'])

        # end ATVM

    def getFieldStringFromAttribute(self, attr, classelement, indent_level=0):
        ''' gets the schema field code '''
        #print 'typename:%s:'%attr.getName(),attr.type,

        if not hasattr(attr,'type') or attr.type=='NoneType':
            ctype='string'
        else:
            ctype=self.coerceType(str(attr.type))

        if ctype=='copy':
            name = getattr(attr,'rename_to',attr.getName())
            field = utils.indent("copied_fields['%s'],\n" % name, indent_level)
            return field


        map=self.typeMap[ctype]['map'].copy()
        if attr.hasDefault():
            map.update( {'default':utils.getExpression(attr.getDefault())} )
        map.update(self.getFieldAttributes(attr))
        widget=self.getWidget( \
                ctype,
                attr,
                attr.getName(),
                classelement )

        if not widget.startswith ('GenericWidget'):
            map.update( {
                'widget': widget })

        self.addVocabulary(classelement, attr, map)

        atype=self.typeMap[ctype]['field']

        if ctype != 'generic' and self.i18n_content_support in self.i18n_at and attr.isI18N():
            atype='I18N'+atype

        doc=attr.getDocumentation(striphtml=self.striphtml)

        if attr.hasTaggedValue('validators'):
            #make validators to a list in order to append the ExpressionValidator
            val=str(attr.getTaggedValue('validators'))
            try:
                map['validators']=tuple(eval(val))
            except:
                map['validators']=tuple(val.split(','))


        if map.has_key('validation_expression'):
            #append the validation_expression to the validators
            expressions = attr.getTaggedValue('validation_expression').split('\n')
            errormsgs = attr.getTaggedValue('validation_expression_errormsg').split('\n')
            if errormsgs and errormsgs != [''] and len(errormsgs) != len(expressions):
                log.critical('validation_expression and validation_expression_errormsg tagged value must have the same size (%s, %s)' %(expressions,errormsgs))
            def corresponding_error(errormsgs, ind):
                if errormsgs and errormsgs != ['']:
                    return ", '"+errormsgs[ind]+"'"
                return ""
            expval = ["""ExpressionValidator('''python:%s'''%s)""" %(expression,corresponding_error(errormsgs,exp_index)) for exp_index,expression in enumerate(expressions)]

            if map.has_key('validators'):
                map['validators']=repr(map.get('validators',()))+'+('+','.join(expval)+',)'
            else:
                map['validators'] = '(' + ','.join(expval) + ',)'

            del map['validation_expression']
            if map.has_key('validation_expression_errormsg'):
                del map['validation_expression_errormsg']


        res=self.getFieldFormatted(attr.getName(),
            atype,
            map,
            doc,
            rawType=attr.getType(),
            indent_level=indent_level
            )

        if attr.getUpperBound() != 1:
            utils.indent(res, 1)
            res="""ArrayField(%s),""" % utils.indent(res,1)

        return res


    def getFieldStringFromAssociation(self, rel, classelement, indent_level=0):
        """Return the schema field code.
        """

        log.debug("Getting the field string from an association.")
        multiValued = 0
        obj = rel.toEnd.obj
        name = rel.toEnd.getName()
        relname = rel.getName()
        log.debug("Endpoint name: '%s'.",
                  name)
        log.debug("Relationship name: '%s'.",
                  relname)
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
            log.debug("Using the 'relations' relation implementation.")
            field=rel.getTaggedValue('reference_field') or \
                  rel.toEnd.getTaggedValue('reference_field') or \
                  self.typeMap['relation']['field'] #the relation can override the field
            # TBD: poseidon reference-as-field handling or so...
            if not field:
                message = "Somehow we couldn't get at the fieldname. Use normal drawn associations instead of a named reference."
                log.critical(message)
                raise message

            map=self.typeMap['relation']['map'].copy()
            map.update({
                'multiValued':   multiValued,
                'relationship':  "'%s'" % relname,
                }
            )
            map.update(self.getFieldAttributes(rel.toEnd))
            map.update( {'widget':self.getWidget('Reference', rel.toEnd, name, classelement)} )
        else:
            log.debug("Using the standard relation implementation.")
            field=rel.getTaggedValue('reference_field') or \
                  rel.toEnd.getTaggedValue('reference_field') or \
                  self.typeMap['reference']['field'] #the relation can override the field
            # TBD: poseidon reference-as-field handling or so...
            if not field:
                message = "Somehow we couldn't get at the fieldname. Use normal drawn associations instead of a named reference."
                log.critical(message)
                raise message
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

                if rel.hasStereoType(self.stub_stereotypes, umlprofile=self.uml_profile) :
                    map.update({'referenceClass':"%s" % rel.getName()})
                    # do not forget the import!!!

                else:
                    map.update({'referenceClass':"ContentReferenceCreator('%s')" % rel.getName()})


        doc=rel.getDocumentation(striphtml=self.striphtml)
        res=self.getFieldFormatted(name, field, map, doc, indent_level)
        return res

    def getFieldStringFromBackAssociation(self, rel, classelement, indent_level=0):
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
        res=self.getFieldFormatted(name, field, map, doc, indent_level)
        return res

    # Generate get/set/add member functions.
    def generateArcheSchema(self, element, base_schema, indent_level=0):
        """ generates the Schema """
        # first copy fields from other schemas if neccessary.
        outfile = StringIO()
        startmarker = True
        for attr in element.getAttributeDefs():
            if str(attr.type.lower())=='copy':
                if startmarker:
                    startmarker=False
                    print >>outfile, 'copied_fields = {}'
                if element.hasStereoType(self.cmfmember_stereotype, umlprofile=self.uml_profile):
                    copybase_schema = "BaseMember.content_schema"
                else:
                    copybase_schema = base_schema
                copyfrom = attr.getTaggedValue('copy_from', copybase_schema)
                name = attr.getTaggedValue('source_name',attr.getName())
                print >>outfile, "copied_fields['%s'] = %s['%s'].copy(%s)" % \
                        (attr.getName(), copyfrom, name, name!=attr.getName() and ("name='%s'" % attr.getName()) or '')
                map = self.getFieldAttributes(attr)
                for key in map:
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
                        tgv.has_key('widget:label') and tgv['widget:label'].strip("'").strip('"') or fieldname,
                        element,
                        fieldname
                        )
                    if widgetkey=='description_msgid':
                        self.addMsgid(widgetvalue.strip("'").strip('"'),
                        tgv.has_key('widget:description') and tgv['widget:description'].strip("'").strip('"') or fieldname,
                        element,
                        fieldname
                        )

        print >> outfile, SCHEMA_START
        aggregatedClasses = []

        for attrDef in element.getAttributeDefs():
            name = attrDef.getName()
            #if name in self.reservedAtts:
            #    continue
            mappedName = utils.mapName(name)

            print >> outfile, self.getFieldStringFromAttribute(attrDef, element,
                                                    indent_level=indent_level+1)

        for child in element.getChildren():
            name = child.getCleanName()
            if name in self.reservedAtts:
                continue
            unmappedName = child.getUnmappedCleanName()
            if child.getRef():
                aggregatedClasses.append(str(child.getRef()))

            if child.isIntrinsicType():
                print >> outfile, self.getFieldString(child, element,
                                                    indent_level=indent_level+1)

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
                print >> outfile
                print >> outfile, self.getFieldStringFromAssociation(rel,
                                                    element,
                                                    indent_level=indent_level+1)

            #Back References
            for rel in element.getToAssociations():
                name = rel.fromEnd.getName()

                #print "backreference"
                if name in self.reservedAtts:
                    continue
                fc=self.getFieldStringFromBackAssociation(rel,
                                                    element,
                                                    indent_level=indent_level+1)
                if fc:
                    print >> outfile
                    print >> outfile, fc

        print >> outfile,'),'
        marshaller=element.getTaggedValue('marshaller') or element.getTaggedValue('marshall')
        if marshaller:
            print >> outfile, 'marshall='+marshaller

        print >> outfile,')'

        return outfile.getvalue()

    def generateMethods(self, outfile, element, mode='class'):
        print >> outfile,'    # Methods'

        generatedMethods = []
        allmethnames = [m.getName() for m in element.getMethodDefs(recursive=1)]

        for m in element.getMethodDefs():
            self.generateMethod(outfile, m, element, mode=mode)
            allmethnames.append(m.getName())
            generatedMethods.append(m)
    
        for interface in element.getRealizationParents():
            meths = [m for m in interface.getMethodDefs(recursive=1) if m.getName() not in allmethnames]
            # We don't want to extra generate methods that are already defined in the class
            if meths:
                print >> outfile, '\n    # Methods from Interface %s' % interface.getName()
                for m in meths:
                    self.generateMethod(outfile, m, element, mode=mode)
                    generatedMethods.append(m)
                    allmethnames.append(m.getName())

        # Contains _all_ generated method names
        method_names = [m.getName() for m in generatedMethods]

        #if __init__ has to be generated for tools i want _not_ __init__ to be preserved
        #if it is added to method_names it wont be recognized as a manual method (hacky but works)
        if element.hasStereoType(self.portal_tools, umlprofile=self.uml_profile) and '__init__' not in method_names:
            method_names.append('__init__')

        if self.method_preservation:
            log.debug("We are to preserve methods, so we're looking for manual methods.")
            cl = self.parsed_class_sources.get(element.getPackage().getFilePath()+'/'+element.name, None)
            if cl:
                log.debug("The class has the following methods: %r.", cl.methods.keys())
                manual_methods = [mt for mt in cl.methods.values() if mt.name not in method_names]
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
        if m.hasStereoType(['action','view','form','portlet_view', 'portlet'], umlprofile=self.uml_profile):
            return

        wrt = outfile.write
        paramstr = ''
        params = m.getParamExpressions()
        if params:
            paramstr = ',' + ','.join(params)

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
                rawPerm = m.getTaggedValue('permission',None)
                permission = utils.getExpression(rawPerm)
                if rawPerm:
                    print >> outfile, utils.indent("security.declareProtected(%s, '%s')" % (permission, m.getName()), 1)
                else:
                    print >> outfile, utils.indent("security.declarePublic('%s')" % m.getName(), 1)
            # A private method is always declarePrivate()'d
            elif permissionMode == 'private':
                print >> outfile, utils.indent("security.declarePrivate('%s')" % m.getName(), 1)

            # A protected method is also declarePrivate()'d. The semantic
            # meaning of 'protected' is that is hidden from the outside world,
            # but accessible to subclasses. The model may wish to be explicit
            # about this intention (even though python has no concept of
            # such protection). In this case, it's still a privately declared
            # method as far as TTW code is concerned.
            elif permissionMode == 'protected':
                print >> outfile, utils.indent("security.declarePrivate('%s')" % m.getName(), 1)

            # A package-level method should be without security declarartion -
            # it is accessible to other methods in the same module, and will
            # use the class/module defaults as far as TTW code is concerned.
            elif permissionMode == 'package':
                # No declaration
                print >> outfile,utils.indent("# Use class/module security defaults",1)
            else:
                log.warn("Method visibility should be 'public', 'private', 'protected' or 'package', got '%s'.",
                         permissionMode)
        else:
            print >> outfile

        cls = self.parsed_class_sources.get(klass.getPackage().getFilePath()+'/'+klass.getName(), None)

        if cls:
            method_code = cls.methods.get(m.getName())
        else:
            #print 'method not found:',m.getName()
            method_code = None

        if self.method_preservation and method_code:
            #print 'preserve method:',method_code.name
            wrt(method_code.src)
        else:
            if mode=='class':
                print >> outfile, '    def %s(self%s):' % (m.getName(), paramstr)
            elif mode=='interface':
                print >> outfile, '    def %s(%s):' % (m.getName(), paramstr[1:])

            code = m.taggedValues.get('code', '')
            doc = m.getDocumentation(striphtml=self.striphtml)
            if doc is not None:
                print >> outfile, utils.indent('"""\n%s\n"""' % doc, 2)
            if code and mode == 'class':
                print >> outfile, utils.indent('\n'+code, 2)
            else:
                print >> outfile, utils.indent('pass', 2)

	if m.isStatic():
            print >> outfile, '    %s = staticmethod(%s)\n' % (m.getName(),m.getName())

    def generateBaseTestcaseClass(self,element,template):
        log.debug('write runalltests.py and framework.py')
        runalltests=utils.readTemplate('tests/runalltests.py')
        framework=utils.readTemplate('tests/framework.py')

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
        testdoc_t=utils.readTemplate('tests/testdoc.txt')
        testdoc=HTML(testdoc_t,{'klass':element })()


        testname=element.getTaggedValue('doctest_name') or element.getCleanName()
        self.makeDir(os.path.join(element.getPackage().getProduct().getFilePath(),'doc'))
        docfile=os.path.join(element.getPackage().getProduct().getFilePath(),'doc','%s.txt' % testname)
        if not self.readFile(docfile):
            of=self.makeFile(docfile)
            of.write(testdoc)
            of.close()

        init='#'
        of=self.makeFile(os.path.join(element.getPackage().getProduct().getFilePath(),'doc','__init__.py' ))

        of.write(init)
        of.close()


        return self.generateTestcaseClass(element,template,testname=testname)

    def generateTestcaseClass(self,element,template,**kw):
        from XMIParser import XMIClass

        log.info("%sGenerating testcase '%s'.",
                 '    '*self.infoind,
                 element.getName())

        assert element.hasStereoType('plone_testcase', umlprofile=self.uml_profile) or element.getCleanName().startswith('test'), \
            "names of test classes _must_ start with 'test', but this class is named '%s'" % element.getCleanName()

        assert element.getPackage().getCleanName() == 'tests', \
            "testcase classes only make sense inside a package called 'tests' \
                 but this class is named '%s' and located in package '%s'" % (element.getCleanName(),element.getPackage().getCleanName())

        if element.getGenParents():
            parent=element.getGenParents()[0]
        else:
            parent=None

        return BaseGenerator.generatePythonClass(self, element, template, parent=parent, **kw)

    def generateWidgetClass(self, element, template, zptname='widget.pt'):
        log.info("Generating widget '%s'.",
                  element.getName())

        #generate the template
        macroname = '%s.pt' % element.getTaggedValue('macro', element.getCleanName())
        templpath=os.path.join(self.getSkinPath(element), macroname)
        fieldpt=self.readFile(templpath)
        if not fieldpt:
            templ=utils.readTemplate(zptname)
            d={ 'klass':        element,
                'generator':    self,
                'parsed_class': element.parsed_class,
                'builtins':     __builtins__,
                'utils':        utils,

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
        log.info("%sGenerating field: '%s'.",
                 '    '*self.infoind,
                 element.getName())

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
            widgetname=None

        return BaseGenerator.generatePythonClass(self, element, template,
            parent=parent,parentname=parentname,
            widget=widget,widgetname=widgetname)

    def elementIsFolderish(self, element):
        log.debug("Determining whether the element '%s' is folderish...",
                  element.name)
        # This entire method hould probably be moved off to the element classes.
        # Copy-pasted from generateArchetypesClass()...
        aggregatedClasses = element.getRefs() + element.getSubtypeNames(recursive=0,filter=['class'])
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
        isFolderish = aggregatedInterfaces or aggregatedClasses or baseaggregatedClasses or \
                      utils.isTGVTrue(element.getTaggedValue('folderish')) or \
                      element.hasStereoType(self.folder_stereotype, umlprofile=self.uml_profile)
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
            elif element.hasStereoType(['large','btree'], umlprofile=self.uml_profile):
                baseclass ='BaseBTreeFolder'
                baseschema ='BaseBTreeFolderSchema'
            else:
                baseclass ='BaseFolder'
                baseschema ='BaseFolderSchema'

            # XXX: How should <<ordered>> affect this?
            if self.i18n_content_support in self.i18n_at and element.isI18N():
                baseclass = 'I18NBaseFolder'
                baseschema = 'I18NBaseFolderSchema'

            if element.getTaggedValue('folder_base_class'):
                raise ValueError, "DEPRECATED: Usage of Tagged Value "\
                      "folder_base_class' in class %s" % element.getCleanName
        else:
            # contentish
            baseclass = 'BaseContent'
            baseschema = 'BaseSchema'
            if self.i18n_content_support in self.i18n_at and element.isI18N():
                baseclass ='I18NBaseContent'
                baseschema ='I18NBaseSchema'

        # if a parent is already an archetype we dont need a baseschema!
        if parent_is_archetype:
            baseclass = None

        # CMFMember support
        if element.hasStereoType(self.cmfmember_stereotype, umlprofile=self.uml_profile):
            baseclass = 'BaseMember.Member'
            baseschema = 'BaseMember.id_schema'

        ## however: tagged values have priority
        # tagged values for base-class overrule
        if element.getTaggedValue('base_class'):
            baseclass = element.getTaggedValue('base_class')

        # tagged values for base-schema overrule
        if element.getTaggedValue('base_schema'):
            baseschema = element.getTaggedValue('base_schema')

        # [optilude] Ignore the standard class if this is an mixin
        # [jensens] An abstract class might have an base_class!
        if baseclass and not utils.isTGVFalse(element.getTaggedValue('base_class',1)) \
           and not element.hasStereoType('mixin', umlprofile=self.uml_profile):
              baseclasses = baseclass.split(',')
              parentnames += baseclasses
        parentnames = [klass.strip() for klass in parentnames]
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
        if self.detailed_created_permissions:
            creation_permission = ("'Add %s Content'" %
                                   element.getCleanName())
            # TODO: looks a bit shitty, ^^^^^. 'Add Event Content'...
            # 'Add MyProduct Content' is ok, but the prefixed way
            # 'Myproduct: Add Event' is preferrable to the above
            # version.
            # As luck would have it, there was a typo
            # --detailed-created-permissions, so I fixed the non-typo
            # --detailed-creation-permissions up with the new
            # generated syntax.
        elif self.detailed_creation_permissions:
            creation_permission =("'%s: Add %s'" %
                                  (element.getPackage().getProduct().getCleanName(),
                                   element.getCleanName()))
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

        # imports needed for CMFMember subclassing
        if element.hasStereoType(self.cmfmember_stereotype, umlprofile=self.uml_profile):
            wrt(CMFMEMBER_IMPORTS)
            # and set the add content permission to what CMFMember needs
            creation_permission = 'ADD_MEMBER_PERMISSION'
            creation_roles = None

        # imports needed for optional support of SQLStorage
        if utils.isTGVTrue(self.getOption('sql_storage_support',element,0)):
            wrt('from Products.Archetypes.SQLStorage import *\n')

        # import Product config.py
        wrt(TEMPLATE_CONFIG_IMPORT % {'module': element.getRootPackage().getProductModuleName()})

        # imports by tagged values
        additionalImports = self.getImportsByTaggedValues(element)
        if additionalImports:
            wrt("# additional imports from tagged value 'import'\n")
            wrt(additionalImports)
            wrt('\n')

        # CMFMember needs a special factory method
        if element.hasStereoType(self.cmfmember_stereotype, umlprofile=self.uml_profile):
            wrt(CMFMEMBER_ADD % {'module': element.getRootPackage().getProductModuleName(),
                                 'prefix': self.prefix,
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
                e = str(e).strip()
                if e not in aggregatedClasses:
                    aggregatedClasses.append(e)

        # if it's a derived class check if parent has stereotype 'archetype'
        parent_is_archetype = False
        for p in element.getGenParents():
            parent_is_archetype = parent_is_archetype or \
                                  p.hasStereoType(self.archetype_stereotype, umlprofile=self.uml_profile)

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

        # Remark: CMFMember support includes VariableSchema support
        # Remark Reinout: since cmfmember 1.1, there's no more
        # variableschema support.
        if element.hasStereoType(self.variable_schema,
                                 umlprofile=self.uml_profile):
            if element.hasStereoType(self.cmfmember_stereotype,
                                     umlprofile=self.uml_profile):
                log.warn("Adding VariableSchema to cmfmember, be careful "
                         "as cmfmember 1.0 already includes it.")
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

        # generate local Schema
        print >> outfile, self.generateArcheSchema(element, baseschema)

        # protected section
        self.generateProtectedSection(outfile, element, 'after-local-schema')

        # generate complete Schmema
        # prepare schema as class attribute
        parent_schema=["getattr(%s, 'schema', Schema(()))" % p.getCleanName() \
                       for p in element.getGenParents()]

        if parent_is_archetype and \
           not element.hasStereoType(self.cmfmember_stereotype, umlprofile=self.uml_profile):
            schema = parent_schema
        else:
            # [optilude] Ignore baseschema in abstract mixin classes
            if element.isAbstract():
                schema = parent_schema
            else:
                schema = [baseschema] + parent_schema

        # own schema overrules base and parents
        schema += ['schema']

        if element.hasStereoType(self.cmfmember_stereotype, umlprofile=self.uml_profile):
            for addschema in ['contact_schema', 'plone_schema', 'plone_2_1_schema',
                              'security_schema', 'login_info_schema',]:
                if utils.isTGVTrue(element.getTaggedValue(addschema, '1')):
                    schema.append('BaseMember.%s' % addschema)
            if utils.isTGVTrue(element.getTaggedValue(addschema, '1')):
                schema.append('ExtensibleMetadata.schema')
        schemaName = '%s_schema' % name
        print >> outfile, utils.indent(schemaName + ' = ' + ' + \\\n    '.join(['%s.copy()' % s for s in schema]), 0)
        print >> outfile

        # protected section
        self.generateProtectedSection(outfile, element, 'after-schema')

        if not element.isComplex():
            print "I: stop complex: ", element.getName()
            return outfile.getvalue()
        if element.getType() in AlreadyGenerated:
            print "I: stop already generated:", element.getName()
            return outfile.getvalue()
        AlreadyGenerated.append(element.getType())

        if self.ape_support:
            print >>outfile,TEMPL_APE_HEADER % {'class_name': name}

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
            print >> outfile,utils.indent('"""\n%s\n"""' % doc, 1)
        elif parsedDoc:
            # Bit tricky, parsedDoc is already indented...
            print >> outfile, '    """%s"""' % parsedDoc

        print >> outfile,utils.indent('security = ClassSecurityInfo()',1)

        print >> outfile,self.generateImplements(element,parentnames)

        header = element.getTaggedValue('class_header')
        if header:
            print >> outfile,utils.indent(header, 1)

        archetype_name=element.getTaggedValue('archetype_name') or element.getTaggedValue('label')
        if not archetype_name:
            archetype_name = name
        portaltype_name = element.getTaggedValue('portal_type') or name

        # [optilude] Only output portal type and AT name if it's not an abstract
        # mixin
        if not element.isAbstract():
            print >> outfile, CLASS_ARCHETYPE_NAME % archetype_name
            print >> outfile, CLASS_META_TYPE % name
            print >> outfile, CLASS_PORTAL_TYPE % portaltype_name

        # Let's see if we have to set use_folder_tabs to 0.
        if utils.isTGVTrue(element.getTaggedValue('hide_folder_tabs', False)):
            print >> outfile, CLASS_FOLDER_TABS % 0

        #allowed_content_classes
        parentAggregates = ''

        if utils.isTGVTrue(element.getTaggedValue('inherit_allowed_types', True)) and element.getGenParents():
            act = []
            for gp in element.getGenParents():
                pt = gp.getTaggedValue('portal_type', None)
                if pt is not None:
                    act.append(pt)
                else:
                    act.append(gp.getCleanName())
            act = ["list(getattr(%s, 'allowed_content_types', []))" % i for i in act]
            if act:
                parentAggregates = ' + ' + ' + '.join(act)
        print >> outfile, CLASS_ALLOWED_CONTENT_TYPES % (repr(aggregatedClasses),parentAggregates)

        #allowed_interfaces
        parentAggregatedInterfaces=''
        if utils.isTGVTrue(element.getTaggedValue('inherit_allowed_types', True)) and element.getGenParents():
            parentAggregatedInterfaces = '+ ' + ' + '.join(tuple(['getattr('+p.getCleanName()+",'allowed_interfaces',[])" for p in element.getGenParents()]))

        if aggregatedInterfaces or baseaggregatedInterfaces:
            print >> outfile, CLASS_ALLOWED_CONTENT_INTERFACES % \
                  (','.join(aggregatedInterfaces),parentAggregatedInterfaces)

        # FTI as attributes on class
        # [optilude] Don't generate FTI for abstract mixins
        if not element.isAbstract ():
            fti=self.generateFti(element,aggregatedClasses)
            print >> outfile,fti

        # _at_rename_after_creation
        rename_after_creation = self.getOption('rename_after_creation', element, default=False)
        if rename_after_creation:
            print >>outfile, CLASS_RENAME_AFTER_CREATION % (utils.isTGVTrue(rename_after_creation) and 'True' or 'False')

        # schema attribute
        wrt(utils.indent('schema = %s' % schemaName, 1) + '\n\n')

        self.generateProtectedSection(outfile,element,'class-header', 1)

        # tool __init__
        if element.hasStereoType(self.portal_tools, umlprofile=self.uml_profile):
            tool_instance_name=element.getTaggedValue('tool_instance_name') or 'portal_%s' % element.getName().lower()
            print >> outfile,TEMPL_CONSTR_TOOL % (baseclass,tool_instance_name)
            self.generateProtectedSection(outfile,element,'constructor-footer',2)
            print >> outfile

        self.generateMethods(outfile, element)

        # [optilude] Don't do modify FTI for abstract mixins
        if not element.isAbstract ():
            print >> outfile, self.generateModifyFti(element)

        # [optilude] Don't register type for abstract classes or tools
        if not (element.isAbstract() or element.hasStereoType('mixin', umlprofile=self.uml_profile)):
            wrt( REGISTER_ARCHTYPE % name)

        # ATVocabularyManager: registration of class
        if element.hasStereoType(self.vocabulary_item_stereotype, umlprofile=self.uml_profile) and \
           not element.isAbstract ():
            # XXX TODO: fetch container_class - needs to be refined:
            # check if parent has vocabulary_container_stereotype and use its
            # name as container
            # else check for TGV vocabulary_container
            # fallback: use SimpleVocabulary
            container = element.getTaggedValue('vocabulary:portal_type','SimpleVocabulary')
            wrt( REGISTER_VOCABULARY_ITEM % (name, container) )
        if element.hasStereoType(self.vocabulary_container_stereotype, umlprofile=self.uml_profile):
            wrt( REGISTER_VOCABULARY_CONTAINER % name )

        wrt('# end of class %s\n\n' % name)

        self.generateProtectedSection(outfile, element, 'module-footer')

        ## handle add content permissions
        if not element.hasStereoType(self.portal_tools, umlprofile=self.uml_profile):
            # tgv overrules
            cpfromtgv = element.getTaggedValue('creation_permission', None)
            if cpfromtgv:
                creation_permission= self.processExpression(cpfromtgv)
            crfromtgv = element.getTaggedValue('creation_roles', None)
            if crfromtgv:
                creation_roles= self.processExpression(crfromtgv)
            ## abstract classes does not need an Add permission
            if creation_permission and not element.isAbstract():
                self.creation_permissions.append( [element.getCleanName(), creation_permission, creation_roles] )

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
            parentnames = list(parentnames) + additionalParents.split(',')

        if not [c for c in element.getGenParents() if c.isInterface()]:
            parentnames.insert(0, 'Base')
        parents = ', '.join(parentnames)

        s1 = 'class %s%s(%s):\n' % (self.prefix, name, parents)

        wrt(s1)
        doc = element.getDocumentation(striphtml=self.striphtml)
        print >> outfile, utils.indent('"""\n%s\n"""' % doc, 1)

        header = element.getTaggedValue('class_header')
        if header:
            print >> outfile, utils.indent(header, 1)

        wrt('\n')
        self.generateMethods(outfile, element, mode='interface')
        wrt('\n\n# end of class %s' % name)

        return outfile.getvalue()


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

        genparentsstereotype = element.getRealizationParents()
        hasz3parent = False
        for gpst in genparentsstereotype:
            if gpst.hasStereoType('z3'):
                hasz3parent = True
                break
        if hasz3parent or element.hasStereoType('z3'):
            outfile.write('import zope')

        return outfile.getvalue()

    def getTools(self,package,autoinstallOnly=0):
        """ returns a list of  generated tools """
        res=[c for c in package.getClasses(recursive=1) if
                    c.hasStereoType(self.portal_tools, umlprofile=self.uml_profile)]

        if autoinstallOnly:
            res=[c for c in res if utils.isTGVTrue(c.getTaggedValue('autoinstall')) ]

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

        templ=utils.readTemplate('Install.py')
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
        creation_permission = self.getOption('creation_permission', package, None)

        if creation_permission:
            default_creation_permission = creation_permission
        else:
            default_creation_permission = self.default_creation_permission

        roles = []
        creation_roles = []
        for perm in self.creation_permissions:
            if not perm[1] in roles and perm[2] is not None:
                roles.append(perm[1])
                creation_roles.append( (perm[1], perm[2]) )

        # prepare (d)TML varibles
        d={'package'                    : package,
           'generator'                  : self,
           'builtins'                   : __builtins__,
           'utils'                      : utils,
           'default_creation_permission': default_creation_permission,
           'creation_permissions'       : self.creation_permissions,
           'creation_roles'             : creation_roles,
           'parsed_config'              : parsed_config,
        }
        d.update(__builtins__)

        templ=utils.readTemplate('config.py')
        dtml=HTML(templ,d)
        res=dtml()

        of=self.makeFile(configpath)
        of.write(res)
        of.close()

        return

    def generateProductInitPy(self, package):
        """ Generate __init__.py at product root from the DTML template"""

        # Get the names of packages and classes to import
        packageImports = [m.getModuleName() for m in package.getAnnotation('generatedPackages') or []
                          if not (m.hasStereoType('tests', umlprofile=self.uml_profile) or
                                  m.hasStereoType('stub', umlprofile=self.uml_profile))]
        classImports   = [m.getModuleName() for m in package.generatedModules if not m.hasStereoType('tests', umlprofile=self.uml_profile)]

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

        templ=utils.readTemplate('__init__.py')
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

        templ=utils.readTemplate('__init_package__.py')
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
            toolgif = open(os.path.join(templdir,'tool.gif'),'rb').read()
            of=self.makeFile(os.path.join(package.getFilePath(),'tool.gif'), self.force, 1)
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

        # Create a customisation policy if required
        if self.customization_policy:
            of=self.makeFile(os.path.join(package.getFilePath(),'CustomizationPolicy.py'),0)
            if of:
                cpTemplate=utils.readTemplate('CustomizationPolicy.py')
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
            if el.isInternal() or el.hasStereoType(self.stub_stereotypes, umlprofile=self.uml_profile):
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
            #skip stub and internal classes
            if element.isInternal() or element.getName() in self.hide_classes \
               or element.getName().lower().startswith('java::'): # Enterprise Architect fix!
                log.debug("Ignoring unnecessary class '%s'.",
                          element.getName())
                continue
            if element.hasStereoType(self.stub_stereotypes, umlprofile=self.uml_profile):
                log.debug("Ignoring stub class '%s'.",
                          element.getName())
                continue

            module=element.getModuleName()
            package.generatedModules.append(element)
            outfilepath=os.path.join(package.getFilePath(), module+'.py')

            if self.method_preservation:
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
                if isinstance(buf, unicode):
                    buf = buf.encode('utf8')

                log.debug("The outfile is ready to be written to disk now. "
                          "Loading it with the pyparser just to be sure we're "
                          "not writing broken files to disk.")
                try:
                    PyParser.PyModule(buf, mode='string')
                    log.debug("Nothing wrong with the outfile '%s'.",
                              outfilepath)
                except:
                    log.critical("There's something wrong with the python code we're about "
                                 "to write to disk. Perhaps a faulty tagged value or a "
                                 "genuine bug in parsing the previous version of the file. "
                                 "The filename is '%s'.",
                                 outfilepath)
                    raise
                classfile = self.makeFile(outfilepath)
                # TBD perhaps check if the file is parseable
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
            #print 'relation:',assoc.getName(),'target cardinality:',targetcard,'sourcecard:',sourcecard
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

            assocclassname=getattr(assoc,'isAssociationClass',0) and assoc.getCleanName() or assoc.getTaggedValue('association_class') or self.getOption('association_class',assoc,None)
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

            # ATVM integration - by jensens
            # very special case: create a vocabulary with the association name
            # this is needed for some use-cases, where a association class has
            # use an vocabulary with the name ofthe relation

            if utils.isTGVTrue(self.getOption('association_vocabulary', assoc, '0')):
                # remember this vocab-name and if set its portal_type
                currentproduct = package.getProductName()
                if not currentproduct in self.vocabularymap.keys():
                    self.vocabularymap[currentproduct] = {}
                if not assoc.getId() in self.vocabularymap[currentproduct].keys():
                    self.vocabularymap[currentproduct][assoc.getCleanName()] = (
                                                    'SimpleVocabulary',
                                                    'SimpleVocabularyTerm'
                    )
                else:
                    print "warning: vocabulary with name %s defined more than once." % vocaboptions['name']

            #/ATVM

            package.num_generated_relations += 1

        if package.num_generated_relations:
            of=self.makeFile(os.path.join(package.getFilePath(),'relations.xml'))
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
        self.makeDir(os.path.join(root.getFilePath(),'skins',
            root.getProductModuleName()))
        self.makeDir(os.path.join(root.getFilePath(),'skins',
            root.getProductModuleName()+'_public'))

        of = self.makeFile(os.path.join(root.getFilePath(), 'skins',
                           root.getProductModuleName()+'_public', 'readme.txt'))
        print >> of, READMEHIGHEST % root.getProductName()
        of.close()

        of = self.makeFile(os.path.join(root.getFilePath(), 'skins',
                           root.getProductModuleName(), 'readme.txt'))
        print >> of, READMELOWEST % root.getProductName()
        of.close()

        # prepare messagecatalog
        if has_i18ndude and self.build_msgcatalog:
            self.makeDir(os.path.join(root.getFilePath(), 'i18n'))
            filepath = os.path.join(root.getFilePath(), 'i18n', 'generated.pot')
            if not os.path.exists(filepath):
                templdir = os.path.join(sys.path[0], 'templates')
                PotTemplate = open(os.path.join(sys.path[0], 'templates', 'generated.pot')).read()
                authors, emails, authorline = self.getAuthors(root)
                PotTemplate = PotTemplate % {
                    'author':', '.join(authors) or 'unknown author',
                    'email':', '.join([email[1:-1] for email in emails]) or 'unknown@email.address',
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
        if self.noclass:
            # skip the other generation steps
            return
        self.generateRelations(root)
        self.generatePackage(root)

        if self.ape_support:
            self.generateApeConf(root.getFilePath(),root)

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
        if not self.noclass:
            if suff.lower() in ('.xmi','.xml'):
                log.debug("Opening xmi...")
                self.root = root= XMIParser.parse(self.xschemaFileName,
                                                  packages=self.parse_packages,
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
                    packages=self.parse_packages, generator=self,
                    generate_datatypes=self.generate_datatypes)
            else:
                raise TypeError,'input file not of type .xmi, .xml, .zargo, .zuml'

            if self.outfilename:
                log.debug("We've got an self.outfilename: %s.",
                          self.outfilename)
                lastPart = os.path.split(self.outfilename)[1]
                log.debug("We've split off the last directory name: %s.",
                          lastPart)
                root.setName(lastPart)
                log.debug("Set the name of the root generator to that"
                          " directory name.")
            else:
                log.debug("No outfilename present, not changing the "
                          "name of the root generator.")
            log.info("Directory in which we're generating the files: '%s'.",
                     self.outfilename)
        else:
            self.root=root=DummyModel(self.outfilename)
        log.info('Generating...')
        if self.method_preservation:
            log.debug('Method bodies will be preserved')
        else:
            log.debug('Method bodies will be overwritten')
        if not has_enhanced_strip_support:
            log.warn("Can't build i18n message catalog. Needs 'python 2.3' or later.")
        if self.build_msgcatalog and not has_i18ndude:
            log.warn("Can't build i18n message catalog. Module 'i18ndude' not found.")
        if not XMIParser.has_stripogram:
            log.warn("Can't strip html from doc-strings. Module 'stripogram' not found.")
        self.generateProduct(root)
