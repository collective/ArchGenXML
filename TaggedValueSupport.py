# WARNING: work-in-progress. Don't touch for a day or three.


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

"""
Tagged values come in two variants. Boolean tagged values and
string-like tagged values that just set a certain value.

Getting our hands on the boolean ones is easy, as they get used
through the isTGVTrue/isTGVFalse methods. For the string-like ones we
need to think of an additional evil scheme... Perhaps look if we can
build a "just handle all other TGVs" method?

updatedKeysFromTGV

"""

def isTGVTrue(tgv):
    """ Return True if the TGV is true
    """
    if type(tgv) in (type(''),type(u'')):
        tgv=tgv.lower()
    return tgv in (1,'1','true')

def isTGVFalse(tgv):
    """ Return True if the TGV is explicitly false

    Checks if a tgv is _explicitly_ false, a 'None' value is undefined
    and _not_ false, so it is something different than (not
    toBoolean(tgv))
    """
    if type(tgv) in (type(''),type(u'')):
        tgv=tgv.lower()
    return tgv in (0,'0','false')


class TaggedValueRegistry:
    """ Registry for all known tagged values (TGVs)

    The aim is to get them finally well-documented by providing a
    place to actually document them.
    """

    def __init__(self):
        """ Initialise an empty registry
        """
        self._registry = {}

    def addTaggedValue(self, category='', name='', explanation=''):
        """ Adds a TGV to the registry

        If the category doesn't exist yet, create it in
        '_registry'. Then add the tagged value to it.
        """
        if not category or not name:
            raise "Category and/or name for TGV needed"
        if not self._registry.has_key(category):
            self._registry[category] = {}
        self._registry[category][name] = explanation

    def isRegisteredTaggedValue(self, category='', name=''):
        """
        """
        #import pdb; pdb.set_trace()
        if not self._registry.has_key(category):
            return False
        if not self._registry[category].has_key(name):
            return False
        return True


tgvRegistry = TaggedValueRegistry()
# Class level tagged values
category = 'class'

name = 'archetype_name'
explanation = """The name which will be shown in the "add new item" drop-down and other
user-interface elements. Defaults to the class name, but whilst the
class name must be valid and unique python identifier, the
archetype_name can be any string."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'content_icon'
explanation = """The name of an image file, which must be found in the skins directory of the product. This will be used to represent the content type in the user interface."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'typeDescription'
explanation = """A description of the type, a sentence or two in length. Used to describe the type to the user."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'base_class'
explanation = """Explicitly set the base class of a content type, overriding the automatic selection of BaseContent, BaseFolder or OrderedBaseFolder as well as any parent classes in the model. See also additional_parents."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'base_schema'
explanation = """Explicitly set the base schema for a content type, overriding the automatic selection of the parent's schema or BaseSchema, BaseFolderSchema or OrderedBaseFolderSchema. """
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'import_from'
explanation = """If you wish to include a class in your model (as a base class or aggregated class, for example) which is actually defined in another product, add the class to your model and set the import_from tagged value to the class that should be imported in its place. You probably don't want the class to be generated, so add a stereotype <<stub>> as well."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'additional_parents'
explanation = """A comma-separated list of the names of classes which should be used as additional parents to this class, in addition to the Archetypes BaseContent, BaseFolder or OrderedBaseFolder. Usually used in conjunction with 'imports' to import the class before it is referenced."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'imports'
explanation = """A list of python import statements which will be placed at the top of the generated file. Use this to make new field and widget types available, for example. Note that in the generated code you will be able to enter additional import statements in a preserved code section near the top of the file. Prefer using the imports tagged value when it imports something that is directly used by another element in your model. You can have several import statements, one per line, or by adding several tagged values with the name 'imports'."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'allow_discussion'
explanation = """Whether or not the content type should be discussable in the portal by default."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'filter_content_types'
explanation = """If set to true (1), explicitly turn on the filter_content_types factory type information value. If this is off, all globally addable content types will be addable inside a (folderish) type; if it is on, only those values in the allowed_content_types list will be enabled. Note that when aggregation or composition is used to define containment, filtered_content_types will be automatically turned on."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'allowed_content_types'
explanation = """A comma-separated list of allowed sub-types for a (folderish) content type. Note that allowed content types are automatically set when using aggregation and composition between classes to specify containment."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'inherit_allowed_types'
explanation = """By default, a child type will inherit the allowable
content types from its parents. Set this property to false (0) to turn this off."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'class_header'
explanation = """An arbitrary string which is injected into the header section of the class, before any methods are defined."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'default_actions'
explanation = """If set to true (1), generate explicitly the default 'view' and 'edit' actions. Usually, these are inherited from the Archetypes base classes, but if you have a funny base class, this may be necessary."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'hide_actions'
explanation = """A comma- or newline-separated list of action ids to hide on the class. For example, set to 'metadata, sharing' to turn off the metadata (properties) and sharing tabs."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'immediate_view'
explanation = """Set the immediate_view factory type information value. This should be the name of a page template, and defaults to 'base_view'. Note that Plone at this time does not make use of immediate_view, which in CMF core allows you to specify a different template to be used when an object is first created from when it is subsequently accessed."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'default_view'
explanation = """The TemplateMixin class in Archetypes allows your class to present several alternative view templates for a content type. The default_view value sets the default one. Defaults to 'base_view'. Only relevant if you use TemplateMixin."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'folderish'
explanation = """Explicitly specify that a class is folderish. It is usually better to the the '<<folder>>' stereotype instead."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'marshall'
explanation ="""Specify a marshaller to use for the class' schema."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'marshaller'
explanation ="""Specify a marshaller to use for the class' schema."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

# Tool
category = 'tool'

name = 'toolicon'
explanation = """The name of an image file, which must be found in the skins directory of the product. This will be used to represent your tool in the Zope Management Interface."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'tool_instance_name'
explanation = """The id to use for the tool. Defaults to 'portal_<name>', where &lt;name&gt; is the class name in lowercase."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'autoinstall'
explanation = """Set to true (1) to automatically install the tool when your product is installed."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'configlet'
explanation = """Set to true (1) to set up a configlet in the Plone control panel for your tool. """
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'configlet:view'
explanation = """The id of the view template to use when first opening the configlet. By default, the 'view' action of the object is used (which is usually base_view)"""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'configlet:title'
explanation = """The name of the configlet."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'configlet:description'
explanation = """A description of the configlet."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'configlet:condition'
explanation = """A TALES expresson defining a condition which will be evaluated to determine whether the configlet should be displayed."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'configlet:permission'
explanation = """A permission which is required for the configlet to be displayed."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'configlet:section'
explanation = """The section of the control panel where the configlet should be displayed. One of 'Plone', 'Products' (default) or 'Members'."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'configlet:icon'
explanation = """The name of an image file, which must be in your product's skin directory, used as the configlet icon."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)


# Methods

category = 'method'

name = 'code'
explanation = """The actual python code of the method. Only use this for simple one-liners. Code filled into the generated file will be preserved when the model is re-generated."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'permission'
explanation = """For method with public visibility only, if a permission is set, declare the method to be protected by this permission. Methods with private or protected visiblity are always declared private since they are not intended for through-the-web unsafe code to access. Methods with package visibility use the class default security and do not get security declarations at all."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

# Actions/views

category = 'action'

name = 'id'
explanation = """The id of the action. Use 'id', """
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'label'
explanation = """The label of the action - displayed to the user."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'condition'
explanation = """A TALES expresson defining a condition which will be evaluated to determine whether the action should be displayed."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'category'
explanation = """The category for the action. Defaults to 'object'."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

# Portlets

category = 'portlet'

name = 'autoinstall'
explanation = """Set to 'left' or 'right' to automatically install the portlet with the product in the left or right slots, respectively."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'view'
explanation = """Set the name of the portlet. Defaults to the method name. This will be used as the name of the auto-created page template for the portlet."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)


# Attributes

category = 'attribute'

name = 'required'
explanation = """Set to true (1) to make the field required"""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'default'
explanation = """Set a value to use as the default value of the field."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'default_method'
explanation = """Set the name of a method on the object which will be called to determine the default value of the field."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'vocabulary'
explanation = """Set to a python list, a DisplayList or a method name (quoted) which provides the vocabulary for a selection widget."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'enforceVocabulary'
explanation = """Set to true (1) to ensure that only items from the vocabulary are permitted."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'multiValued'
explanation = """Certain fields, such as reference fields, can optionally accept morethan one value if multiValued is set to true (1)"""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'accessor'
explanation = """Set the name of the accessor (getter) method. If you are overriding one of the DC metadata fields such as 'title' or 'description' be sure to set the correct accessor names such as 'Title' and 'Description'; by default these accessors would be generated as getTitle() or getDescription()."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'mutator'
explanation = """Similarly, set the name of the mutator (setter) method."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'searchable'
explanation = """Whether or not the field should be searchable when performing a search in the portal. """
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)


# widgets (not a separate category!)

name = 'widget:type'
explanation = """Set the name of the widget to use. Each field has an associated default widget, but if you need a different one (e.g. a SelectionWidget for a string field), use this value to override."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'widget:label'
explanation = """Set the widget's label"""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'widget:description'
explanation = """Set the widget's description"""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'widget:label_msgid'
explanation = """Set the label i18n message id. Defaults to a name generated from the field name."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'widget:description_msgid'
explanation = """ Set the description i18n message id. Defaults to a name generated from the field name."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

name = 'widget:i18n_domain'
explanation = """Set the i18n domain. Defaults to the product name."""
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)
