#!/usr/bin/env python
"""Registry for tagged values

Goal is to document them and to enforce the documentation somewhat.

Use it by importing 'tgvRegistry' and calling its 'isRegistered()'
method::

  from TaggedValueSupport import tgvRegistry

  def yourMethod():
      if not tgvRegistry.isRegistered(tagname, category):
          raise HorrificOmissionError()
      ....

That's the heavy-handed way. You can also just call
'tgvRegistry.isRegistered(tagname, category)' without checking the
return value, as the function prints a warning himself.
"""

#----------------------------------------------------------------
# Name:        TaggedValueSupport.py
# Purpose:     Tools and registry for tagged values. The registry
#              improves documentation of the TGVs.
#
# Author:      Reinout van Rees
#
# Created:     2005-07-04
# Copyright:   (c) Zest software/Reinout van Rees
# Licence:     GPL
#-----------------------------------------------------------------------------

# isTGVTrue() and isTGVFalse are originally copied from utils.py

import logging

class TaggedValueRegistry:
    """ Registry for all known tagged values (TGVs)

    The aim is to get them finally well-documented by providing a
    place to actually document them.
    """

    def __init__(self):
        """ Initialise an empty registry
        """

        self.log = logging.getLogger('TGVregistry')
        self._registry = {}
        self.categoryFromClassMap = {
            #'XMIParser.XMIElement': [],
            'XMIParser.XMIPackage': ['package'],
            'XMIParser.XMIModel': ['model'],
            'XMIParser.XMIClass': ['class', 'tool', 'portlet', 'field'],#, 'widget'],
            #'XMIParser.XMIInterface': [],
            #'XMIParser.XMIMethodParameter': [],
            'XMIParser.XMIMethod': ['method', 'action/form/view'],
            'XMIParser.XMIAttribute': ['attribute'],
            #'XMIParser.XMIAssocEnd': [],
            'XMIParser.XMIAssociation': ['association'],
            #'XMIParser.XMIAbstraction': [],
            #'XMIParser.XMIDependency': [],
            #'XMIParser.XMIStateContainer': [],
            #'XMIParser.XMIStateMachine': [],
            'XMIParser.XMIStateTransition': ['state transition'],
            #'XMIParser.XMIAction': [],
            #'XMIParser.XMIGuard': [],
            'XMIParser.XMIState': ['state'],
            #'XMIParser.XMICompositeState': [],
            #'XMIParser.XMIDiagram': [],
            }

    def addTaggedValue(self, category='', tagname='', explanation=''):
        """Adds a TGV to the registry.

        If the category doesn't exist yet, create it in
        '_registry'. Then add the tagged value to it.
        """
        if not category or not tagname:
            raise "Category and/or tagname for TGV needed"
        if not self._registry.has_key(category):
            self._registry[category] = {}
        self._registry[category][tagname] = explanation
        self.log.debug("Added tagged value '%s' to registry.", tagname)

    def isRegistered(self, tagname='', category='', silent=False):
        """Return True if the TGV is in te registry

        If category has been passed, check for that too. Otherwise, be
        a bit more loose. Needed for simple isTGVFalse/True support
        that cannot pass a category.
        """
        self.log.debug("Checking tag '%s' (category '%s') in the registry...",
                       tagname, category)
        original_category = category
        if category:
            # Look in 'categoryFromClassMap' for possible translations
            if category in self.categoryFromClassMap:
                categories = self.categoryFromClassMap[category]
            else:
                if not self._registry.has_key(category):
                    categories = self._registry.keys()
                else:
                    categories = [category]
        else:
            categories = self._registry.keys()
        for category in categories:
            if self._registry[category].has_key(tagname):
                self.log.debug("Tag '%s' (category '%s') exists in the "
                               "registry.", tagname, category)
                return True
        if 'attribute' in categories:
            if tagname.startswith('widget:'):
                self.log.debug("Special 'widget:' tagged value, leaving it be.")
                return True
        if 'class' in categories:
            if tagname in ('transient', 'volatile'):
                self.log.debug("Special 'transient' or 'volatile' tagged "
                               "value, leaving it be.")
                return True
        if silent:
            self.log.debug("Tag '%s' (category '%s') is not self-documented.",
                           tagname, original_category)
        else:
            self.log.warn("Tag '%s' (category '%s') is not self-documented.",
                          tagname, original_category)
        return False

    def documentation(self, indentation=0):
        """Return the documentation for all tagged values.

        The documentation is returned as a string. 'indentation' can
        be used to get it back indented 'indentation' spaces. Handy
        for (classic) structured text.

        """

        import StringIO
        import textwrap
        wrapper = textwrap.TextWrapper(replace_whitespace=True,
                                       initial_indent = ' ',
                                       subsequent_indent = '    ',
                                       width=72)
        out = StringIO.StringIO()
        categories = self._registry.keys()
        categories.sort()
        for category in categories:
            print >> out
            print >> out, category
            print >> out
            tagnames = self._registry[category].keys()
            tagnames.sort()
            for tagname in tagnames:
                explanation = self._registry[category][tagname]
                explanation_lines = explanation.split('\n')
                explanation_lines = [line.strip() for line in explanation_lines]
                explanation = '\n'.join(explanation_lines)
                outstring = "%s -- %s" % (tagname,
                                          explanation)
                outstring = wrapper.fill(outstring)
                print >> out, outstring
                print >> out
        spaces = ' ' * indentation
        lines = out.getvalue().split('\n')
        indentedLines = [(spaces + line) for line in lines]
        return '\n'.join(indentedLines)


tgvRegistry = TaggedValueRegistry()

# Model level tagged values
category = 'model'

# Package level tagged values
category = 'package'

# Class level tagged values
category = 'class'

# The following tagged values can be set on classes to alter their behaviour:

tagname = 'policy'
explanation = """On a class with stereotype '<<plone_testcase>>', this
sets the customization policy used by the test case to setup the site
(e.g. 'CMFMember Site')."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'doctest_name'
explanation = """In a tests package, setting the stereotype '<<doc_testcase>>'
on a class turns it into a doctest. The doctest itself is placed in the doc/
subdirectory. The 'doctest_name' tagged value overwrites the default name for
the file (which is the name of the doctestcase class + '.txt'). ArchGenXML
appends the '.txt' extension automatically, so you don't need to specify it."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'quickinstall_dependencies'
explanation = """In a tests package, setting the stereotype '<<plone_testcase>>'
on a class turns it into a base testcase. The base testcase will install all
listed products to the test portal using CMFQuickInstallerTool. The list has
the form: '"ProductsA", "ProductB"."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'quickinstall_self'
explanation = """In a tests package, setting the stereotype '<<plone_testcase>>'
on a class turns it into a base testcase. The base testcase will install
the current Product (where the testcase resides in) using CMFQuickInstallerTool."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'portal_type'
explanation = """Sets the CMF portal-type this class will be registered with,
defaults to the class-name."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'archetype_name'
explanation = """The name which will be shown in the "add new item" drop-down
and other user-interface elements. Defaults to the class name, but whilst the
class name must be valid and unique python identifier, the archetype_name can
be any string."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'content_icon'
explanation = """The name of an image file, which must be found in the skins
directory of the product. This will be used to represent the content type in
the user interface."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'typeDescription'
explanation = """A description of the type, a sentence or two in length.
Used to describe the type to the user."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'base_class'
explanation = """Explicitly set the base class of a content type, overriding
the automatic selection of BaseContent, BaseFolder or OrderedBaseFolder as well
as any parent classes in the model. See also additional_parents."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'base_schema'
explanation = """Explicitly set the base schema for a content type, overriding
the automatic selection of the parent's schema or BaseSchema, BaseFolderSchema
or OrderedBaseFolderSchema."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'folder_base_class'
explanation = """Useful when using the '<<folder>>' stereotype in order to set
the folderish base class."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'global_allow'
explanation = """Overwrite the AGX-calculated 'global_allow'
setting. Setting it to '1' makes your content type addable everywhere (in
principle), setting it to '0' limits it to places where it's explicitly
allowed as content."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'hide_folder_tabs'
explanation = """Deprecated. If you want to hide the "contents" tab,
just set a tagged value 'use_folder_tabs=0', which just sets that
archetypes property. (The old hide_folder_tabs implementation was
                      horribly broken)."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'import_from'
explanation = """If you wish to include a class in your model (as a base
class or aggregated class, for example) which is actually defined in another
product, add the class to your model and set the import_from tagged value to
the class that should be imported in its place. You probably don't want the
class to be generated, so add a stereotype '<<stub>>' as well."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'additional_parents'
explanation = """A comma-separated list of the names of classes which should
be used as additional parents to this class, in addition to the Archetypes
BaseContent, BaseFolder or OrderedBaseFolder. Usually used in conjunction
with 'imports' to import the class before it is referenced."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'imports'
explanation = """A multiline list of python import statements which will be
placed at the top of the generated file. Use this to make new field and widget
types available, for example. Note that in the generated code you will be able
to enter additional import statements in a preserved code section near the top
of the file. Prefer using the imports tagged value when it imports something
that is directly used by another element in your model. You can have several
import statements, one per line, or by adding several tagged values with the
name 'imports'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'allow_discussion'
explanation = """Whether or not the content type should be discussable in the
portal by default."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'filter_content_types'
explanation = """If set to true (1), explicitly turn on the
filter_content_types factory type information value. If this is off, all
globally addable content types will be addable inside a (folderish) type;
if it is on, only those values in the allowed_content_types list will be
  enabled. Note that when aggregation or composition is used to define
  containment, filtered_content_types will be automatically turned on."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'allowed_content_types'
explanation = """A comma-separated list of allowed sub-types for a (folderish)
content type. Note that allowed content types are automatically set when using
aggregation and composition between classes to specify containment."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'inherit_allowed_types'
explanation = """By default, a child type will inherit the allowable content
types from its parents. Set this property to false (0) to turn this off."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'class_header'
explanation = """An arbitrary string which is injected into the header section
of the class, before any methods are defined."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'default_actions'
explanation = """If set to true (1), generate explicitly the default 'view'
and 'edit' actions. Usually, these are inherited from the Archetypes base
classes, but if you have a funny base class, this may be necessary."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'hide_actions'
explanation = """A comma- or newline-separated list of action ids to hide on
the class. For example, set to 'metadata, sharing' to turn off the metadata
(properties) and sharing tabs."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'immediate_view'
explanation = """Set the immediate_view factory type information value. This
should be the name of a page template, and defaults to 'base_view'. Note that
Plone at this time does not make use of immediate_view, which in CMF core
allows you to specify a different template to be used when an object is first
created from when it is subsequently accessed."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'default_view'
explanation = """The TemplateMixin class in Archetypes allows your class to
present several alternative view templates for a content type. The default_view
value sets the default one. Defaults to 'base_view'. Only relevant if you use
TemplateMixin."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'suppl_views'
explanation = """The TemplateMixin class in Archetypes allows your class to
present several alternative view templates for a content type. The suppl_views
value sets the available views. Example: '("my_view", "myother_view")'.
Defaults to '()'. Only relevant if you use TemplateMixin."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'folderish'
explanation = """Explicitly specify that a class is folderish. It is usually
better to the the '<<folder>>' stereotype instead."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'marshall'
explanation ="""Specify a marshaller to use for the class' schema."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'marshaller'
explanation ="""Specify a marshaller to use for the class' schema."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'base_actions'
explanation = """Sets the base actions in the class's factory type
information (FTI)."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'disable_polymorphing'
explanation = """Normally, archgenxml looks at the parents of the current
class for content types that are allowed as items in a folderish class.
So: parent's allowed content is also allowed in the child. Likewise,
subclasses of classes allowed as content are also allowed on this class.
Classic polymorphing. In case this isn't desired, set the tagged value
'disable_polymorphing' to 1.
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)
# TBD: change this into 'polymorphic_allowed_types' with a default of True.
# Optilude is right on this one. It *does* need support for default values.

#The following are needed for CMFMember classes
tagname = 'contact_schema'
explanation = """TODO. CMFMember related."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'plone_schema'
explanation = """TODO. CMFMember related."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'security_schema'
explanation = """TODO. CMFMember related."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'login_info_schema'
explanation = """TODO. CMFMember related."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Tool
category = 'tool'

#   The following tagged values can be set on classes with the
#   '<<portal_tool>>' stereotype to alter their behaviour:

tagname = 'toolicon'
explanation = """The name of an image file, which must be found in the skins
directory of the product. This will be used to represent your tool in the
Zope Management Interface."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'tool_instance_name'
explanation = """The id to use for the tool. Defaults to 'portal_<name>',
where &lt;name&gt; is the class name in lowercase."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'autoinstall'
explanation = """Set to true (1) to automatically install the tool when
your product is installed."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet'
explanation = """Set to true (1) to set up a configlet in the Plone control
panel for your tool."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:view'
explanation = """The id of the view template to use when first opening the
configlet. By default, the 'view' action of the object is used (which is
usually base_view)"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:title'
explanation = """The name of the configlet."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:description'
explanation = """A description of the configlet."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:condition'
explanation = """A TALES expresson defining a condition which will be
evaluated to determine whether the configlet should be displayed."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:permission'
explanation = """A permission which is required for the configlet
to be displayed."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:section'
explanation = """The section of the control panel where the configlet
should be displayed. One of 'Plone', 'Products' (default) or 'Member'.
**warning**: older documentation versions mentioned 'Members' here."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:icon'
explanation = """The name of an image file, which must be in your product's
skin directory, used as the configlet icon."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)


# Methods

category = 'method'

# The following tagged values can be set on methods to alter their
# behaviour:

tagname = 'code'
explanation = """The actual python code of the method. Only use this
for simple one-liners. Code filled into the generated file will be
preserved when the model is re-generated."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname,
explanation=explanation)

tagname = 'autoinstall'
explanation = """Set this to 'right' or 'left' on a method with a
stereotype'<<portlet>>', this adds the portlet to 'left_slots' or
'right_slots'. See the documentation for the stereotype."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname,
explanation=explanation)

tagname = 'permission'
explanation = """For method with public visibility only, if a
permission is set, declare the method to be protected by this
permission. Methods with private or protected visiblity are always
declared private since they are not intended for through-the-web
unsafe code to access. Methods with package visibility use the class
default security and do not get security declarations at all."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname,
explanation=explanation)

# Actions/forms/views

category = 'action/form/view'

# For methods with either of the '<<action>>'', '<<form>>' or
# '<<view>>' stereotypes, the following tagged values can be used to
# control the generated actions:

tagname = 'id'
explanation = """The id of the action. Use 'id', """
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'label'
explanation = """The label of the action - displayed to the user."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'condition'
explanation = """A TALES expresson defining a condition which will be
evaluated to determine whether the action should be displayed."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'category'
explanation = """The category for the action. Defaults to 'object'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

for tagname in ['action', 'view', 'form']:
    explanation = """For a stereotype '%s', this tagged value can
    be used to overwrite the default URL ('..../name_of_method')
    into '..../tagged_value'.""" % tagname
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'action_label'
explanation = """TODO."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Portlets

category = 'portlet'

#  For methods with the '<<portlet>>' or '<<portlet_view>>'
#  stereotypes, the following tagged values can be used:

tagname = 'autoinstall'
explanation = """Set to 'left' or 'right' to automatically install the
portlet (a class with the stereotype '<<portlet>>') with the product
in the left or right slots, respectively. If it already exists in the
slot it won't get overwritten."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'view'
explanation = """Set the name of the portlet. Defaults to the method
name. This will be used as the name of the auto-created page template
for the portlet."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Field classes
category = 'field'

# for classes with the stereotype <<field>>

tagname = 'validation_expression'
explanation = """Use an ExpressionValidator and sets the by value given
expression."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'validation_expression_errormsg'
explanation = """Sets the error message to the ExpressionValidator (use with
validation_expression to define the validation expression to which this error
message applies)."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'description'
explanation = """Sets a description for this field. It's used for
field documentation while registering inside Archetypes."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Widget classes
category = 'widget'

# for classes with the stereotype <<widget>>

tagname = 'title'
explanation = """Sets the widget title. It's used for widget documentation
while registering inside Archetypes."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'description'
explanation = """Sets a description for this widget. It's used for widget
documentation while registering inside Archetypes."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'used_for'
explanation = """Sets the possible fields which can use this widget. It's
used for widget documentation while registering inside Archetypes. The list
has the form: '"Products.Archetypes.Field.Field1Name",
"Products.Archetypes.Field.FieldName2"'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'macro'
explanation = """Sets the macro used by the widget. This will be used as
the name of the auto-created page template for the widget."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'show_hm'
explanation = """Setting this boolean value to False will show only the date entry."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Attributes

category = 'attribute'

# Tagged values on attributes are passed straight through to the
# Archetypes schema as field attributes. Therefore, you should consult
# the Archetypes documentation to find out which values you can set on
# each field. Some of the more common ones are:

tagname = 'required'
explanation = """Set to true (1) to make the field required"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'validators'
explanation = """TODO."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'widget'
explanation = """Allows you to set the widget to be used for this attribute."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'copy_from'
explanation = """To copy an attribute from another schema, give it the
type 'copy'. The tagged value 'copy_from' is then used to specify which
schema to copy it from (for instance, 'BaseSchema' when copying Description
from the base schema). For copying your own schemas, add an 'imports' tagged
value to import your class (say 'MyClass') and then put 'MyClass.schema' in
your 'copy_from' value."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'source_name'
explanation = """With attribute type 'copy' sometimes schema-recycling is fun,
together with copy_from you can specify the source name of the field in the
schema given by copy_from."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'schemata'
explanation = """If you want to split your form with many, many attibutes
in multiple schemata ("sub-forms"), add a tagged value 'schemata' to the
attributes you want in a different schemata with the name of that schemata (for
instance "personal data"). The default schemata is called "default", btw."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'validation_expression'
explanation = """Sets the expression used for run-time validation of the attribute."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'write_permission'
explanation = """Sets the permission that determines if you're allowed
to write to the field."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'sizes'
explanation = """Sets the allowed sizes for an ImageField widget."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'original_size'
explanation = """Sets the maximum size for the original for an ImageField widget."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'default'
explanation = """Set a value to use as the default value of the field."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'default_method'
explanation = """Set the name of a method on the object which will be called
to determine the default value of the field."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'vocabulary'
explanation = """Set to a python list, a DisplayList or a method name (quoted)
which provides the vocabulary for a selection widget."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'enforceVocabulary'
explanation = """Set to true (1) to ensure that only items from the vocabulary
are permitted."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'multiValued'
explanation = """Certain fields, such as reference fields, can optionally
accept morethan one value if multiValued is set to true (1)"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'accessor'
explanation = """Set the name of the accessor (getter) method. If you are
overriding one of the DC metadata fields such as 'title' or 'description' be
sure to set the correct accessor names such as 'Title' and 'Description'; by
default these accessors would be generated as getTitle() or getDescription()."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'mutator'
explanation = """Similarly, set the name of the mutator (setter) method."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'searchable'
explanation = """Whether or not the field should be searchable when performing
a search in the portal."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'index'
explanation = """Add an index to the attribute. The value of the tagged value
should be the same that archetypes expects, so something like 'FieldIndex' or
'FieldIndex:brains'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'vocabulary:type'
explanation = """Enables support for Products 'ATVocabularyManager' by setting
value to 'ATVocabularyManager'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'vocabulary:term_type'
explanation = """For use with 'ATVocabularyManager'. Defaults to
'SimplevocabularyTerm'. Let you define the portal_type of the vocabularyterm
used for the default term that is created in Install.py."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'vocabulary:vocabulary_type'
explanation = """For use with 'ATVocabularyManager'. Defaults to
'Simplevocabulary'. Let you define the portal_type of the vocabulary used
as initial vocabulary at Product install time. If VdexVocabulary is used,
the install-script tries to install a vocabulary from a vdex file names
'Products/PRODUCTNAME/data/VOCABULARYNAME.vdex'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'vocabulary:name'
explanation = """Togther with Products 'ATVocabularyManager' this sets the
name of the vocabulary."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'validation_expression'
explanation = """Use an ExpressionValidator and sets the by value given
expression."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'validation_expression_errormsg'
explanation = """Sets the error message to the ExpressionValidator (use with
validation_expression to define the validation expression to which this error
message applies)."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# widgets (not a separate category!)

# Similarly, tagged values with the prefix 'widget:' will be passed
# through as widget parameters. Consult the Archetypes documentation
# for details. The most common widget parameters are:

tagname = 'widget:type'
explanation = """Set the name of the widget to use. Each field has an
associated default widget, but if you need a different one (e.g. a
SelectionWidget for a string field), use this value to override."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'widget:label'
explanation = """Set the widget's label."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'widget:description'
explanation = """Set the widget's description."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'widget:label_msgid'
explanation = """Set the label i18n message id. Defaults to a name
generated from the field name."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'widget:description_msgid'
explanation = """ Set the description i18n message id. Defaults to
a name generated from the field name."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'widget:i18n_domain'
explanation = """Set the i18n domain. Defaults to the product name."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Package level tagged values
category = 'state'

tagname = 'initial_state'
explanation = """Sets this state to be the initial state. This allows
you to use a normal state in your UML diagram instead of the special
round starting-state symbol."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'worklist'
explanation = """Attach objects in this state to the named
worklist. An example of a worklist is the to-review list."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'worklist:guard_permissions'
explanation = """Sets the permissions needed to be allowed to view the
worklist. Default value is 'Review portal content'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'worklist:guard_roles'
explanation = """Sets the roles needed to be allowed to view the
worklist. No default value"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)


# State transition tagged values
category = 'state transition'

tagname = 'trigger_type'
explanation = """Sets the trigger type, following what is defined by DCWorkflow:

            0 : Automatic
            1 : User Action (default)
            2 : Workflow Method
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Category 'associations'
category = 'association'

tagname = 'inverse_relation_name'
explanation = """Together with 'Relations' Product you have inverse relations.
the name default to 'name_of_your_relation_inverse', but you can overrrule it
using this tagged value."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'reference_field'
explanation = """Use a custom field instead of ReferenceField."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'back_reference_field'
explanation = """Use a custom field instead of ReferenceField."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'relation_field'
explanation = """Use a custom field instead of RelationField. Works
only together with 'Relations' Product and relation_implementation
set to 'relations'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Tagged values for more than one category

for category in ['model', 'package', 'class']:
    tagname = 'rename_after_creation'
    explanation = """Setting this boolean value enables or disables explicit
    the after creation rename feature using '_at_rename_after_creation'
    class-attribute."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'use_portal_factory'
    explanation = """Setting this boolean value enables the registration
    of the type for use with portal_factory."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'version_info'
    explanation = """Add ArchGenXML version information to the generated
    file (default is 1)."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'migrate_dynamic_view_fti'
    explanation = """Migrates FTI of a type/class to CMFDynamicViewFTI. This
    works only if the class derives from an ATContentType, from ATCTMixIn or
    direct from CMFDynamicViewFTI.browserdefault.BrowserDefaultMixin."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'cmf_target_version'
    explanation = """Controls CMF Version specific behaviour, primary to
    avoid 'Deprecation warnings.' Defaults to '1.4'."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'use_workflow'
    explanation = """Tie the class to the named workflow. A state diagram
    (=workflow) attached to a class in the UML diagram is automatically
    used as that class's workflow; this tagged value allows you to tie the
    workflow to other classes."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'searchable'
    explanation = """Per default a fields 'searchable' property is set to
    False. Sometimes you want it for all fields True. This TGV let you
    define the default for a class, package or model."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'generate_reference_fields'
    explanation = """Per default (True) navigable reference (or relation)
    ends are resulting in a ReferenceField (or RelationField). Setting
    this value to False results in not generating ReferenceFields
    automagically."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'catalogmultiplex:white'
    explanation = """Add an archetypes class (identified by meta_type) to one or 
    more catalogs to be cataloged in. Comma-separated list of catalogs.
    Example-value: 'myfancy_catalog, another_catalog'. 
    Explaination: Additionally to the default 'portal_catalog' the instances of
    this class will be catalogged in the two given catalogs."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'catalogmultiplex:black'
    explanation = """Remove an archetypes class (identified by meta_type) 
    from one or more catalogs to be cataloged in. Comma-separated list of 
    catalogs. Example-value: 'portal_catalog, another_catalog'. Explaination: 
    Instances of the class wont be catalogged in portal_catalog anymore."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

for category in ['model', 'package', 'class', 'attribute']:
    tagname = 'read_permission'
    explanation = """Defines archetypes fields read-permission. Use it
    together with workflow to control ability to view fields based on
    roles/permissions."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'write_permission'
    explanation = """Defines archetypes fields write-permission. Use it
    together with workflow to control ability to write data to a field
    based on roles/permissions."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

for category in ['model', 'package', 'class', 'tool', 'portlet']:
    for tagname in ['author', 'email', 'copyright', 'license']:
        explanation = """You can set the %s project-wide with the '--%s'
        commandline parameter (or in the config file). This TGV allows
        you to overwrite it on a %s level.""" % (tagname, tagname, category)
        tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'imports'
    explanation = """A list of python import statements which will be placed
    at the top of the generated file. Use this to make new field and widget
    types available, for example. Note that in the generated code you will
    be able to enter additional import statements in a preserved code section
    near the top of the file. Prefer using the imports tagged value when it
    imports something that is directly used by another element in your model.
    You can have several import statements, one per line, or by adding several
    tagged values with the name 'imports'."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'creation_permission'
    explanation = """Sets the creation permission for the class. Example:
    'Add portal content'."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'creation_roles'
    explanation = """You can set an own role who should be able to add
    a type. Use an Tuple of Strings. Default and example for this value:
    '("Manager", "Owner", "Member")'."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'module'
    explanation = """Like 'module_name', it overwrites the name of the
    directory it'd be normally placed in."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'module_name'
    explanation = """Like 'module', it overwrites the name of the
    directory it'd be normally placed in."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

for category in ['model', 'package', 'association']:

    tagname = 'relation_implementation'
    explanation = """Sets the type of implementation is used for an
    association: 'basic' (used as default) for classic style archetypes
    references or 'relations' for use of the 'Relations' Product."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'association_class'
    explanation = """You can use associations classes to store content on
    the association itself. The class used is specified by this setting.
    Don't forget to import the used class properly."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'association_vocabulary'
    explanation = """Switch, defaults to False. Needs Product
    'ATVocabularyManager'. Generates an empty vocabulary with
    the name of the relation."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Tagged values occurring everywhere
for category in tgvRegistry._registry:

    tagname = 'label'
    explanation = """Sets the readable name."""
    if not tgvRegistry._registry[category].has_key(tagname):
        # Making sure we don't overwrite specialised stuff :-)
        tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'documentation'
    explanation = """You can add documention via this tag; it's better to
    use  your UML tool's documentation field."""
    if not tgvRegistry._registry[category].has_key(tagname):
        # Making sure we don't overwrite specialised stuff :-)
        tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

if __name__ == '__main__':
    print tgvRegistry.documentation()
