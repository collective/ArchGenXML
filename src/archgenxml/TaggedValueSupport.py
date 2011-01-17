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
from atmaps import STATE_PERMISSION_MAPPING

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
            #'xmiparser.XMIElement': [],
            'xmiparser.xmiparser.XMIPackage': ['package'],
            'xmiparser.xmiparser.XMIModel': ['model'],
            'xmiparser.xmiparser.XMIClass': ['class', 'tool', 'field', 'widget'],
            #'xmiparser.XMIInterface': [],
            #'xmiparser.XMIMethodParameter': [],
            'xmiparser.xmiparser.XMIMethod': ['method', 'action'],
            'xmiparser.xmiparser.XMIAttribute': ['attribute'],
            #'xmiparser.XMIAssocEnd': [],
            'xmiparser.xmiparser.XMIAssociation': ['association'],
            #'xmiparser.XMIAbstraction': [],
            #'xmiparser.XMIDependency': [],
            #'xmiparser.XMIStateContainer': [],
            'xmiparser.xmiparser.XMIStateMachine': ['state machine'],
            'xmiparser.xmiparser.XMIStateTransition': ['state transition'],
            'xmiparser.xmiparser.XMIAction': ['state action'],
            #'xmiparser.XMIGuard': [],
            'xmiparser.xmiparser.XMIState': ['state'],
            #'xmiparser.XMICompositeState': [],
            #'xmiparser.XMIDiagram': [],
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
        """Return True if the TGV is in the registry

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

    def getCategories(self):
        """ return name for 
        """
        return self._registry.keys()
 
    def getCategoryElements(self, category):
        tagnames = self._registry[category].keys()
        tagnames.sort()
        return tagnames


tgvRegistry = TaggedValueRegistry()

# Model level tagged values
category = 'model'

tagname = 'plone_target_version'
explanation = """The target version of Plone. Defaults to 3.0 Possible values 
are 2.5 and 3.0"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'product_description'
explanation = """The description of the Product. This is placed as 
description tag in the metadata.xml file of the product's profile"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'default_interface_type'
explanation = """default type of interfaces (z2 or z3)."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'skin_directories'
explanation = """A comma separated list of subdirectories to be generated
inside the product skins directory. Each of this directories is prefixed with
productname in lowercase. The default value is "'templates', 'styles', 'images'".
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'dependend_profiles'
explanation = """GenericSetup profiles your product depends on. A list of 
profile names separated by commas. This list is used for the dependencies
tag inside the metadata.xml file of the product's profile
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'dependency_step_qi'
explanation = """Generate Quickinstaller dependency installation for your product.
Boolean (1 or 0), default 0 (off). Dependencies can be declared in AppConfig.py in a
variable DEPENDENCIES.
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'fixtools'
explanation = """Generate fixTools function in setuphandlers.py.
It calls initializeArchetypes for generated tools, thus reset existing data in the tools.
Boolean (1 or 0), default 0 (off).
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)


# Package level tagged values
category = 'package'

# Class level tagged values
category = 'class'

# The following tagged values can be set on classes to alter their behaviour:

tagname = 'doctest_name'
explanation = """In a tests package, setting the stereotype '<<doc_testcase>>'
on a class turns it into a doctest. The doctest itself is placed in the doc/
subdirectory. The 'doctest_name' tagged value overwrites the default name for
the file (which is the name of the doctestcase class + '.txt'). ArchGenXML
appends the '.txt' extension automatically, so you don't need to specify it."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'portal_type'
explanation = """Sets the CMF portal-type this class will be registered with,
defaults to the class-name."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'default_interface_type'
explanation = """default type of interfaces (z2 or z3)."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'strict'
explanation = """On a class with the <<interface_doctest>> stereotype:
check for inherited interfaces as well."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'archetype_name'
explanation = """The name which will be shown in the "add new item" drop-down
and other user-interface elements. Defaults to the class name, but whilst the
class name must be valid and unique python identifier, the archetype_name can
be any string."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'active_workflow_states'
explanation = """The active workflow states for a remember type. MUST be set
on <<remember>> types. Format is ['state', 'anotherstate']."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'content_icon'
explanation = """The name of an image file, which must be found in the skins
directory of the product. This will be used to represent the content type in
the user interface."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'typeDescription'
explanation = """DEPRECATED. Use 'description' instead. """
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'description'
explanation = """A description of the type, a sentence or two in length.
Used to describe the type to the user."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'base_class'
explanation = """Explicitly set the base class of a content type, overriding the
automatic selection of BaseContent, BaseFolder or OrderedBaseFolder as
well as any parent classes in the model. What you specify here ends up
as the first item (or items: comma-separate them) in the classes it
inherits from. So this is also a handy way to place one class
explicitly in front of the other. See also additional_parents."""
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

tagname = 'parentclasses_first'
explanation = """if this tgv is set to true generalization parents are used before the standard
base classes (e.g. BaseContent) this option is sometimes necessary when inheriting from some special
parents (e.g. 'remember' style classes)."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)
tgvRegistry.addTaggedValue(category=category, tagname='parentclass_first', explanation=explanation)

tagname = 'hide_folder_tabs'
explanation = """When you want to hide the folder tabs (mostly the
"contents" tab, just set this tagged value to 1."""
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

tagname = 'allowable_content_types'
explanation = """A comma-separated list of allowed test format for a textarea
widget."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'inherit_allowed_types'
explanation = """By default, a child type will inherit the allowable content
types from its parents. Set this property to false (0) to turn this off."""
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

tagname = 'register'
explanation = """'Remember' related. Set as default member type."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Portlet
category = 'portlet'

# for classes with the stereotype <<portlet_class>>

tagname = 'template_name'
explanation = """Specify a template for the portlet (without .pt).
Default is the class name. (on classes with the stereotype <<portlet_class>>)"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# View
category = 'view'

# for classes with the stereotype <<view_class>>

tagname = 'name'
explanation = """Specify a name for the zope3 view..
Default is the class name. (on classes with the stereotype <<view_class>>)"""
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
explanation = """Controls, wether the tool is automatically installed when
your product is installed. Boolean, default is True."""
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
explanation = """A TALES expression defining a condition which will be
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
explanation = """The actual python code of the method. Only use this for
simple one-liners. Code filled into the generated file will be preserved
when the model is re-generated."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'documentation'
explanation = """You can add documention via this tag; it's better to
use your UML tool's documentation field."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'label'
explanation = """Sets the readable name."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'permission'
explanation = """For method with public visibility only, if a
permission is set, declare the method to be protected by this
permission. Methods with private or protected visiblity are always
declared private since they are not intended for through-the-web
unsafe code to access. Methods with package visibility use the class
default security and do not get security declarations at all."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Actions

category = 'action'

# For methods with '<<action>>' stereotypes, the following tagged values can 
# be used to control the generated actions:

tagname = 'id'
explanation = """The id of the action. Use 'id', """
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'label'
explanation = """The label of the action - displayed to the user."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'condition'
explanation = """A TALES expression defining a condition which will be
evaluated to determine whether the action should be displayed."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'category'
explanation = """The category for the action. Defaults to 'object'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'visible'
explanation = """Sets the visible property, default to 'True'"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'permission'
explanation = """The permission used for the action, a string or comma 
separated list of strings, default to 'View'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'action'
explanation = """For a stereotype 'action', this tagged value can
be used to overwrite the default URL ('..../name_of_method')
into '..../tagged_value'.""" 
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

# Attributes

category = 'attribute'

# Tagged values on attributes are passed straight through to the
# Archetypes schema as field attributes. Therefore, you should consult
# the Archetypes documentation to find out which values you can set on
# each field. Some of the more common ones are:

tagname = 'expression'
explanation = """evaluation expression for computed fields."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'required'
explanation = """Set to true (1) to make the field required"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'index'
explanation = """DEPRECATED: Add an index to the attribute. Use catalog:index 
and the index:* tagged value instead."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'indexMethod'
explanation = """DEPRECATED: Declares method used for indexing. """
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'validators'
explanation = """TODO. Not supported for now."""
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
accept more than one value if multiValued is set to true (1)"""
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

tagname = 'vocabulary:term_type'
explanation = """For use with 'ATVocabularyManager'. Defaults to
'SimplevocabularyTerm'. Let you define the portal_type of the vocabularyterm
used for the default term that is created in Install.py."""
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

tagname = 'array:widget'
explanation = """specify which custom ArrayWidget should be used for a field
(only applies if the field has cardinality >1."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'allowed_types'
explanation = """Sets the types allowed for a ReferenceField. Default is []"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'index:attributes'
explanation = """The attributes to use for index or metadata (string or comma 
separated list of strings). This are the methods called at indexing time. 
Normally it is enough to provide one index method, but for some specific use 
cases you might need to provide alternatives. If you don not provide this 
tagged value, the name of the accessor of the field is the default."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'index:name'
explanation = """the name of the index used (string). Use this name in your 
queries. If you do not provide a name, the name of the accessor of the field 
is the default."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'index:extras'
explanation = """Some indexes are using so called 'extras' on installation as 
configuration. If the index need extras you'll need to declare them here. 
Provide a comma separated list."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'index:properties'
explanation = """Some indexes are using 'properties' on installation as 
configuration. If the index need properties you'll need to declare them here. 
Provide a comma separated list."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)
 
tagname = 'collection:criteria'
explanation = """Add the index to the Collection (aka Smart Folder) Indexes 
available for defining Criteria. Provide a comma separated list of criteria 
that will be available by default.
Available criterias are: ATBooleanCriterion, 
ATDateCriteria, ATDateRangeCriterion, ATListCriterion, ATPortalTypeCriterion, 
ATReferenceCriterion, ATSelectionCriterion, ATSimpleIntCriterion, 
ATSimpleStringCriterion, ATSortCriterion, ATCurrentAuthorCriterion, 
ATPathCriterion, ATRelativePathCriterion. You must provide an index:type as well.
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)        
    
tagname = 'collection:criteria_description'
explanation = """A help text (string), used for collection:criteria. 
Its added to the generated.pot as a literal. 
If not provided the widget:description is used.
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)        
    
tagname = 'collection:criteria_label'
explanation = """The display name of the collection:criteria, called 
friendly name (string). Its added to the generated.pot as a literal. 
If not given the widget:label is taken if provided.
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)        
    
tagname = 'collection:metadata'
explanation = """register the catalog:metadata as an available column in a 
Collection. Can be used as an alternative for catalog:metadata. 
catalog:metadata_accessor is used if given.
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)   

tagname = 'collection:metadata_description'
explanation = """A help text (string), used for collection:criteria. Its added to the 
generated.pot as a literal. If not provided the collection:criteria_help 
or - if not provided - widget:description is used.
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)   

tagname = 'collection:metadata_label'
explanation = """the display name of the collection:metadata, 
called friendly name (string), used for index:criteria. 
Its added to the generated.pot as a literal. 
If not given the widget:label is taken if provided.
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)   

tagname = 'move:pos'
explanation = """Move the current field at the given position (an int).
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)   

tagname = 'move:top'
explanation = """Move the current field to the top (put 1 for the value).
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)   

tagname = 'move:bottom'
explanation = """Move the current field to the bottom (put 1 for the value).
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)   

tagname = 'move:after'
explanation = """Move the current field after the given field (put the field name between quote).
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)   

tagname = 'move:before'
explanation = """Move the current field before the given field (put the field name between quote).
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)   

for category in ['model', 'package', 'class', 'attribute']:
    tagname = 'catalog:metadata'
    explanation = """Adds the field to the metadata record on the query result. 
    Boolean, 1 or 0. If you do not provide 'index:attributes', the name of the 
    accessor of the field is the default. If 'catalog:attributes' is given for 
    each attribute one field at the record will be created."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'catalog:index'
    explanation = """Add the field (or all fields of a class, package, model) 
    to the index. Boolean, 1 or 0. Default is 0. If set, you may need to provide 
    'index:*' tagged values too."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)
    
    tagname = 'catalog:name'
    explanation = """Sometimes you need to add an index to a other catalog than 
    'portal_catalog' and its XML-File 'catalog.xml'. Provide a tuple of comma 
    separated strings, id of the catalog and the filename of its configuration 
    file. default is "portal_catalog, Plone Catalog Tool'."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'index:type'
    explanation = """the type of index used as (string), for example 
    'FieldIndex', 'KeywordIndex', 'DateIndex' or any available index in your 
    portal. For known types a default is guessed, such as FieldIndex for 
    StringFields or DateIndex for DateFields. If no guess is possible, we 
    assume a FieldIndex."""
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

tagname = 'widget:i18n_domain'
explanation = """Set the i18n domain. Defaults to the product name."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'widget:macro'
explanation = """Set an alternate macro for the widget"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Package level tagged values
category = 'state'

tagname = 'initial_state'
explanation = """Sets this state to be the initial state. This allows
you to use a normal state in your UML diagram instead of the special
round starting-state symbol."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'description'
explanation = """Sets the state description."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'worklist'
explanation = """Attach objects in this state to the named
worklist. An example of a worklist is the to-review list."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'worklist:guard_permissions'
explanation = """Sets the permissions needed to be allowed to view the
worklist. Default value is 'Review portal content'. Set to 'False' for no
guard_permission."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'worklist:guard_roles'
explanation = """Sets the roles needed to be allowed to view the
worklist. No default value"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'worklist:guard_expressions'
explanation = """Sets the expressions needed to be allowed to view the
worklist. No default value."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

for (tagname, permissionname) in STATE_PERMISSION_MAPPING.items():
    explanation = "Shortcut for '%s'." % permissionname
    tgvRegistry.addTaggedValue(category=category, tagname=tagname,
                               explanation=explanation)
    
# State transition tagged values
category = 'state transition'

tagname = 'trigger_type'
explanation = """Sets the trigger type, following what is defined by DCWorkflow:

            automatic
            user action (default)
            workflow method
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Statemascine tagged values
category = 'state machine'

tagname = 'bindings'
explanation = """List of portal-types this workflow should be bound to. 
Comma-separated, i.e. 'Document, Image, File'.
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'default'
explanation = """A workflow id to be set as the default workflow."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'state_var'
explanation = """The workflow state variable to use, the default is "review_state".
This can be used when you use a second workflow with collective.subtractiveworkflow."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'meta_type'
explanation = """The workflow meta_type. The default is "Workflow". You can
change it to "Subtractive Workflow" to use it with collective.subtractiveworkflow."""
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

tagname = 'field'
explanation = """Synonymous with either reference_field or
relation_field, depending on whether you use it on the *from* end or the
*to* end of a relation. Works only together with 'Relations' Product and
relation_implementation set to 'relations'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'relationship'
explanation = """Standard relationship for ReferenceField"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Tagged values for more than one category

for category in ['model', 'package', 'class']:
    # Default "on" is ok. You *can* modify it in the code.
    #tagname = 'rename_after_creation'
    #explanation = """Setting this boolean value enables or disables explicit
    #the after creation rename feature using '_at_rename_after_creation'
    #class-attribute."""
    #tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)
    
    tagname = 'alias'
    explanation = """FTI Alias definition in the form
    alias=fromvalue,tovalue"""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)
    
    tagname = 'use_portal_factory'
    explanation = """This boolean value controls the registration
    of the type for use with portal_factory. Default: True."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'display_in_navigation'
    explanation = """Setting this boolean value adds the type to
    'Displayed content types' in the portals navigation settings. Default is True"""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'searchable_type'
    explanation = """Setting this boolean value adds the type to 'types to be
    searched' in the portals search settings. Default is True"""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'version_info'
    explanation = """Add ArchGenXML version information to the generated
    file (default is 1)."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'use_dynamic_view'
    explanation = """Controles wether CMFDynamicViewFTI is used for a type/class.
    Boolean, default is True."""
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

    tagname = 'global_allow'
    explanation = """Overwrite the AGX-calculated 'global_allow'
    setting of class. Setting it to '1' makes your content type addable everywhere (in
    principle), setting it to '0' limits it to places where it's explicitly
    allowed as content."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)        
    
    tagname = 'detailed_creation_permissions'
    explanation = """Give the content-type (types in the package, model) own 
    creation permissions, named automagically 'ProductName: Add ClassName'."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)    

    tagname = 'vocabulary:vocabulary_type'
    explanation = """For use with 'ATVocabularyManager'. Defaults to
    'Simplevocabulary'. Let you define the portal_type of the vocabulary used
    as initial vocabulary at Product install time. If VdexVocabulary is used,
    the install-script tries to install a vocabulary from a vdex file names
    'Products/PRODUCTNAME/data/VOCABULARYNAME.vdex'."""
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

    tagname = 'vocabulary:type'
    explanation = """Enables support for Products 'ATVocabularyManager' by setting
    value to 'ATVocabularyManager'."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

    tagname = 'i18ncontent'
    explanation = """Enables the content type(s) for LinguaPlone. Only allowed 
    value is 'linguaplone'."""
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

for category in ['model', 'package', 'class', 'tool']:
    for tagname in ['author', 'email', 'copyright', 'license']:
        explanation = """You can set the %s project-wide with the '--%s'
        commandline parameter (or in the config file). This TGV allows
        you to use/ overwrite it on a %s level.""" % (tagname, tagname, category)
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

# Workflow
category = 'state transition'
tagname = 'url'
explanation = """Action URL, need 'PloneWorkflowTransitions'
to see it in Plone."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

category = 'state action'
tagname = 'before:binding'
explanation = """Interface to bind the before effect to."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

category = 'state action'
tagname = 'after:binding'
explanation = """Interface to bind the after effect to."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Tagged values occurring everywhere
for category in tgvRegistry._registry:

    tagname = 'label'
    explanation = """Sets the readable name."""
    if not tgvRegistry._registry[category].has_key(tagname):
        # Making sure we don't overwrite specialised stuff :-)
        tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

undocumented_tags = [
    # unknown tags
    'Modify', 'access', 'i18ncontent', 'default_page_type',
    # class tags
    'rename_after_creation', 'storage',
    'index_method',
    # field tags
    'languageIndependent', 'default_content_type', 'default_output_type', 'mode',
    # image field tags
    'max_size', 'pil_resize_algo', 'pil_quality', 'swallowResizeExceptions',
    # widget tags
    'default:widget:Reference',
    'widget:size', 'widget:maxlength', 'widget:rows', 'widget:cols',
    'widget:divider', 'widget:append_only', 'widget:format',
    'widget:future_years', 'widget:starting_year', 'widget:ending_year',
    'widget:show_ymd', 'widget:show_hm', 'widget:thousands_commas',
    'widget:whole_dollars', 'widget:dollars_and_cents', 'widget:addable',
    'widget:allow_file_upload', 'widget:visible', 'columns', 'allow_empty_rows',
    'widget:auto_insert', 'widget:columns', 'widget:provideNullValue',
    'widget:nullValueTitle', 'widget:omitCountries', 'widget:allow_brightness',
    ## tags for ReferenceWidget
    'widget:checkbox_bound',
    'widget:destination_types',
    'widget:destination',
    ## tags for ReferenceBrowserWidget
    'widget:default_search_index',
    'widget:show_indexes',
    'widget:available_indexes',
    'widget:allow_search',
    'widget:allow_browse',
    'widget:startup_directory',
    'widget:base_query',
    'widget:force_close_on_insert',
    'widget:search_catalog',
    'widget:allow_sorting',
    'widget:show_review_state',
    'widget:show_path',
    'widget:only_for_review_states',
    'widget:image_portal_types',
    'widget:image_method',
    'widget:history_length',
    'widget:restrict_browsing_to_startup_directory',
    ## tags for DynatreeWidget
    'widget:selectMode',
    'widget:rootVisible',
    'widget:minExpandLevel',
    'widget:leafsOnly',
    'widget:showKey',
]
category = 'unknown'
explanation = ''
for tagname in undocumented_tags:
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)


def main():
    print tgvRegistry.documentation()

if __name__ == '__main__':
    main()
