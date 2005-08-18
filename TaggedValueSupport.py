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
            'XMIParser.XMIClass': ['class', 'tool', 'portlet'],
            #'XMIParser.XMIInterface': [],
            #'XMIParser.XMIMethodParameter': [],
            'XMIParser.XMIMethod': ['method', 'action'],
            'XMIParser.XMIAttribute': ['attribute'],
            #'XMIParser.XMIAssocEnd': [],
            #'XMIParser.XMIAssociation': [],
            #'XMIParser.XMIAssociation': [],
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
        self.log.debug("Added tagged value '%s' to registry.",
                       tagname)

    def isRegistered(self, tagname='', category=''):
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
                self.log.debug("Tag '%s' (category '%s') exists in the registry.",
                               tagname, category)
                return True
        self.log.warn("Tag '%s' (category '%s') is not self-documented.",
                      tagname, original_category)
        return False

    def documentation(self, indentation=1):
        """Return the documentation for all tagged values.

        The documentation is returned as a string. 'indentation' can
        be used to get it back indented 'indentation' spaces. Handy
        for (classic) structured text.
        
        """

        import StringIO
        out = StringIO.StringIO()
        for category in self._registry:
            print >> out
            print >> out, category
            print >> out
            tagnames = self._registry[category].keys()
            tagnames.sort()
            for tagname in tagnames:
                explanation = self._registry[category][tagname]
                print >> out, " %s -- %s" % (tagname,
                                             explanation)
                print >> out
        spaces = ' ' * indentation
        lines = out.getvalue().split('\n')
        indentedLines = [(spaces + line) for line in lines]
        return '\n'.join(indentedLines)
        

tgvRegistry = TaggedValueRegistry()

# Model level tagged values
category = 'model'

tagname = 'module'
explanation = """TODO."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'module_name'
explanation = """TODO."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Package level tagged values
category = 'package'

tagname = 'module_name'
explanation = """TODO."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'module'
explanation = """TODO."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Class level tagged values
category = 'class'

# The following tagged values can be set on classes to alter their behaviour:

tagname = 'module_name'
explanation = """TODO."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'policy'
explanation = """TODO."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'portal_type'
explanation = """TODO."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'use_workflow'
explanation = """Tie the class to the named workflow. A state diagram
(=workflow) attached to a class in the UML diagram is automatically
used as that class's workflow; this tagged value allows you to tie the
workflow to other classes."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'archetype_name'
explanation = """The name which will be shown in the "add new item" drop-down and other
user-interface elements. Defaults to the class name, but whilst the
class name must be valid and unique python identifier, the
archetype_name can be any string."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'content_icon'
explanation = """The name of an image file, which must be found in the skins directory of the product. This will be used to represent the content type in the user interface."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'typeDescription'
explanation = """A description of the type, a sentence or two in length. Used to describe the type to the user."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'base_class'
explanation = """Explicitly set the base class of a content type, overriding the automatic selection of BaseContent, BaseFolder or OrderedBaseFolder as well as any parent classes in the model. See also additional_parents."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'base_schema'
explanation = """Explicitly set the base schema for a content type, overriding the automatic selection of the parent's schema or BaseSchema, BaseFolderSchema or OrderedBaseFolderSchema. """
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'module'
explanation = """TODO."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'folder_base_class'
explanation = """Useful when using the '<<folder>>' stereotype in
order to set the folderish base class."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'global_allow'
explanation = """Overwrite the AGX-calculated 'global_allow'
setting. Setting it to '1' makes your content type addable everywhere (in principle),
setting it to '0' limits it to places where it's explicitly allowed as
content."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'hide_folder_tabs'
explanation = """Hides the folder tabs for this content type. (Mostly
the "Contents" tab)."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'import_from'
explanation = """If you wish to include a class in your model (as a base class or aggregated class, for example) which is actually defined in another product, add the class to your model and set the import_from tagged value to the class that should be imported in its place. You probably don't want the class to be generated, so add a stereotype <<stub>> as well."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'additional_parents'
explanation = """A comma-separated list of the names of classes which should be used as additional parents to this class, in addition to the Archetypes BaseContent, BaseFolder or OrderedBaseFolder. Usually used in conjunction with 'imports' to import the class before it is referenced."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'imports'
explanation = """A list of python import statements which will be placed at the top of the generated file. Use this to make new field and widget types available, for example. Note that in the generated code you will be able to enter additional import statements in a preserved code section near the top of the file. Prefer using the imports tagged value when it imports something that is directly used by another element in your model. You can have several import statements, one per line, or by adding several tagged values with the name 'imports'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'allow_discussion'
explanation = """Whether or not the content type should be discussable in the portal by default."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'filter_content_types'
explanation = """If set to true (1), explicitly turn on the filter_content_types factory type information value. If this is off, all globally addable content types will be addable inside a (folderish) type; if it is on, only those values in the allowed_content_types list will be enabled. Note that when aggregation or composition is used to define containment, filtered_content_types will be automatically turned on."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'allowed_content_types'
explanation = """A comma-separated list of allowed sub-types for a (folderish) content type. Note that allowed content types are automatically set when using aggregation and composition between classes to specify containment."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'inherit_allowed_types'
explanation = """By default, a child type will inherit the allowable
content types from its parents. Set this property to false (0) to turn this off."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'class_header'
explanation = """An arbitrary string which is injected into the header section of the class, before any methods are defined."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'default_actions'
explanation = """If set to true (1), generate explicitly the default 'view' and 'edit' actions. Usually, these are inherited from the Archetypes base classes, but if you have a funny base class, this may be necessary."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'hide_actions'
explanation = """A comma- or newline-separated list of action ids to hide on the class. For example, set to 'metadata, sharing' to turn off the metadata (properties) and sharing tabs."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'immediate_view'
explanation = """Set the immediate_view factory type information value. This should be the name of a page template, and defaults to 'base_view'. Note that Plone at this time does not make use of immediate_view, which in CMF core allows you to specify a different template to be used when an object is first created from when it is subsequently accessed."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'default_view'
explanation = """The TemplateMixin class in Archetypes allows your class to present several alternative view templates for a content type. The default_view value sets the default one. Defaults to 'base_view'. Only relevant if you use TemplateMixin."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'folderish'
explanation = """Explicitly specify that a class is folderish. It is usually better to the the '<<folder>>' stereotype instead."""
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

tagname = 'creation_permission'
explanation = """Sets the creation permission for the class. Example:
'Add portal content'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'creation_roles'
explanation = """TODO."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'disable_polymorphing'
explanation = """Normally, archgenxml looks at the parents of the
current class for content types that are allowed as items in a
folderish class. So: parent's allowed content is
also allowed in the child. Likewise, subclasses of classes allowed as
content are also allowed on this class. Classic polymorphing. In case
this isn't desired, set the tagged value 'disable_polymorphing' to 1.
"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)
# TBD: change this into 'polymorphic_allowed_types' with a default of True.
# Optilude is right on this one. It *does* need support for default values.

# Tool
category = 'tool' 

#   The following tagged values can be set on classes with the
#   '<<portal_tool>>' stereotype to alter their behaviour: 

tagname = 'toolicon'
explanation = """The name of an image file, which must be found in the skins directory of the product. This will be used to represent your tool in the Zope Management Interface."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'tool_instance_name'
explanation = """The id to use for the tool. Defaults to 'portal_<name>', where &lt;name&gt; is the class name in lowercase."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'autoinstall'
explanation = """Set to true (1) to automatically install the tool when your product is installed."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet'
explanation = """Set to true (1) to set up a configlet in the Plone control panel for your tool. """
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:view'
explanation = """The id of the view template to use when first opening the configlet. By default, the 'view' action of the object is used (which is usually base_view)"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:title'
explanation = """The name of the configlet."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:description'
explanation = """A description of the configlet."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:condition'
explanation = """A TALES expresson defining a condition which will be evaluated to determine whether the configlet should be displayed."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:permission'
explanation = """A permission which is required for the configlet to be displayed."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:section'
explanation = """The section of the control panel where the configlet should be displayed. One of 'Plone', 'Products' (default) or 'Members'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'configlet:icon'
explanation = """The name of an image file, which must be in your product's skin directory, used as the configlet icon."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)


# Methods

category = 'method'

# The following tagged values can be set on methods to alter their
# behaviour:

tagname = 'code'
explanation = """The actual python code of the method. Only use this for simple one-liners. Code filled into the generated file will be preserved when the model is re-generated."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'permission'
explanation = """For method with public visibility only, if a permission is set, declare the method to be protected by this permission. Methods with private or protected visiblity are always declared private since they are not intended for through-the-web unsafe code to access. Methods with package visibility use the class default security and do not get security declarations at all."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Actions/forms/views

category = 'action'

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
explanation = """A TALES expresson defining a condition which will be evaluated to determine whether the action should be displayed."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'category'
explanation = """The category for the action. Defaults to 'object'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

for tagname in ['action', 'view', 'form']:
    explanation = """For a stereotype '%s', this tagged value can be used to
    overwrite the default URL ('..../name_of_method') into '..../tagged_value'.""" % tagname
    tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'action_label'
explanation = """TODO."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Portlets

category = 'portlet'

#  For methods with the '<<portlet>>' or '<<portlet_view>>'
#  stereotypes, the following tagged values can be used: 

tagname = 'autoinstall'
explanation = """Set to 'left' or 'right' to automatically install the portlet with the product in the left or right slots, respectively."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'view'
explanation = """Set the name of the portlet. Defaults to the method name. This will be used as the name of the auto-created page template for the portlet."""
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

tagname = 'validation_expression'
explanation = """Sets the expression used for run-time validation of the attribute."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'write_permission'
explanation = """Sets the permission that determines if you're allowed
to write to the field."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'default'
explanation = """Set a value to use as the default value of the field."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'default_method'
explanation = """Set the name of a method on the object which will be called to determine the default value of the field."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'vocabulary'
explanation = """Set to a python list, a DisplayList or a method name (quoted) which provides the vocabulary for a selection widget."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'enforceVocabulary'
explanation = """Set to true (1) to ensure that only items from the vocabulary are permitted."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'multiValued'
explanation = """Certain fields, such as reference fields, can optionally accept morethan one value if multiValued is set to true (1)"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'accessor'
explanation = """Set the name of the accessor (getter) method. If you are overriding one of the DC metadata fields such as 'title' or 'description' be sure to set the correct accessor names such as 'Title' and 'Description'; by default these accessors would be generated as getTitle() or getDescription()."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'mutator'
explanation = """Similarly, set the name of the mutator (setter) method."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'searchable'
explanation = """Whether or not the field should be searchable when performing a search in the portal. """
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)


# widgets (not a separate category!)

# Similarly, tagged values with the prefix 'widget:' will be passed
# through as widget parameters. Consult the Archetypes documentation
# for details. The most common widget parameters are: 

tagname = 'widget:type'
explanation = """Set the name of the widget to use. Each field has an associated default widget, but if you need a different one (e.g. a SelectionWidget for a string field), use this value to override."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'widget:label'
explanation = """Set the widget's label"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'widget:description'
explanation = """Set the widget's description"""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'widget:label_msgid'
explanation = """Set the label i18n message id. Defaults to a name generated from the field name."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'widget:description_msgid'
explanation = """ Set the description i18n message id. Defaults to a name generated from the field name."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'widget:i18n_domain'
explanation = """Set the i18n domain. Defaults to the product name."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# Package level tagged values
category = 'state'

tagname = 'worklist'
explanation = """Attach objects in this state to the named
worklist. An example of a worklist is the to-review list."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

tagname = 'worklist:guard_permissions'
explanation = """Sets the permissions needed to be allowed to view the
worklist. Default value is 'Review portal content'."""
tgvRegistry.addTaggedValue(category=category, tagname=tagname, explanation=explanation)

# State transition tagged values
category = 'state transition'

tagname = 'trigger_type'
explanation = """TODO."""
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

for category in ['model', 'package', 'class', 'tool', 'portlet']:
    for tagname in ['author', 'email', 'copyright']:
        explanation = """You can set the %s project-wide with the
        '--%s' commandline parameter (or in the config file). This tag
        allows you to overwrite it on a %s level.""" % (tagname,
                                                        tagname,
                                                        category)
        tgvRegistry.addTaggedValue(category=category,
                                   tagname=tagname,
                                   explanation=explanation)


if __name__ == '__main__':
    print tgvRegistry.documentation()
