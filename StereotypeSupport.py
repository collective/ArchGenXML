"""Registry for stereotypes

Goal is to document them and to enforce the documentation somewhat.

Use it by importing 'stereotypeRegistry' and calling its 'isRegistered()'
method::

  from StereotypeSupport import stereotypeRegistry

  def yourMethod():
      if not stereotypeRegistry.isRegistered(tagname, category):
          raise HorrificOmissionError()
      ....

That's the heavy-handed way. You can also just call
'stereotypeRegistry.isRegistered(tagname, category)' without checking the
return value, as the function prints a warning himself.

Also you can use stereotypesRegistry.types('stub') to get all 'stub'
stereotypes. 

"""

import logging
log.getLogger('stereoreg')

class StereotypeRegistry():
    """Provide registry for stereotypes.
    """

    def __init__(self):
        self._registry = {}
        self._types = {}
        self.categoryFromClassMap = {
            #'XMIParser.XMIElement': [],
            #'XMIParser.XMIPackage': ['package'],
            #'XMIParser.XMIModel': ['model'],
            #'XMIParser.XMIClass': ['class', 'tool', 'portlet'],
            #'XMIParser.XMIInterface': [],
            #'XMIParser.XMIMethodParameter': [],
            #'XMIParser.XMIMethod': ['method', 'action'],
            #'XMIParser.XMIAttribute': ['attribute'],
            #'XMIParser.XMIAssocEnd': [],
            #'XMIParser.XMIAssociation': [],
            #'XMIParser.XMIAssociation': [],
            #'XMIParser.XMIAbstraction': [],
            #'XMIParser.XMIDependency': [],
            #'XMIParser.XMIStateContainer': [],
            #'XMIParser.XMIStateMachine': [],
            #'XMIParser.XMIStateTransition': ['state transition'],
            #'XMIParser.XMIAction': [],
            #'XMIParser.XMIGuard': [],
            #'XMIParser.XMIState': ['state'],
            #'XMIParser.XMICompositeState': [],
            #'XMIParser.XMIDiagram': [],
            }

    def addStereotype(self,
                      category='',
                      stereotypename='',
                      explanation='',
                      type_=''):
        """Adds a stereotype to the registry.

        If the category doesn't exist yet, create it in
        '_registry'. Then add the tagged value to it.
        """

        if not category or not stereotypename:
            raise "Category and/or stereotypename for stereotype needed"
        if not self._registry.has_key(category):
            self._registry[category] = {}
        self._registry[category][stereotypename] = explanation
        if type_:
            if not self._types.has_key(type_):
                self._types[type_] = []
            self._types[type_].append(stereotype)
        self.log.debug("Added stereotype '%s' to registry.",
                       stereotypename)
    
    def isRegistered(self, stereotypename, category=None):
        """Return True if the TGV is in te registry

        If category has been passed, check for that too. Otherwise, be
        a bit more loose. Needed for simple isTGVFalse/True support
        that cannot pass a category.
        """

        self.log.debug("Checking stereotype '%s' (category '%s') in the registry...",
                       stereotypename, category)
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
            if self._registry[category].has_key(stereotypename):
                self.log.debug("Stereotype '%s' (category '%s') exists in the registry.",
                               stereotypename, category)
                return True
        self.log.warn("Stereotype '%s' (category '%s') is not self-documented.",
                      stereotypename, original_category)
        return False

    def types(self, type_):
        """Return list of stereotypes of type 'type_'.
        """

        if not self._types.has_key(type_):
            log.critical("Stereotype registry doesn't know anything "
                         "about a type of stereotype called '%s'.",
                         type_)
            raise "Unknown type of stereotype."
        results = self._types[type_]
        log.debug("Returning list of stereotypes of type '%s': %r.",
                  type_, results)
        return results

    def documentation(self, indentation=1)
        """Return the documentation for all stereotypes.

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
            stereotypenames = self._registry[category].keys()
            stereotypenames.sort()
            for stereotypename in stereotypenames:
                explanation = self._registry[category][stereotypename]
                print >> out, " %s -- %s" % (stereotypename,
                                             explanation)
                print >> out
        spaces = ' ' * indentation
        lines = out.getvalue().split('\n')
        indentedLines = [(spaces + line) for line in lines]
        return '\n'.join(indentedLines)

stereotypeRegistry = StereotypeRegistry()

category = 'class'

stereotypename = 'worklist:guard_permissions'
explanation = """Sets the permissions needed to be allowed to view the
worklist. Default value is 'Review portal content'."""
tgvRegistry.addStereotype(category=category,
                          stereotypename=stereotypename,
                          explanation=explanation)

# Add mechanism for category documentation

"""
Class stereotypes

  The following stereotypes may be applied to classes to alter their behaviour:

stub, odStub -- Don't generate this class. Stub classes may be used for clarity where the model refers to classes from other products, such as when these are used as composited objects or base classes. 

hidden -- Generate the class, but turn off global_allow, thereby making it unavailable in the portal by default. Note that if you use composition to specify that a type should be addable only inside another (folderish) type, then global_allow will be turned off automatically, and the type be made addable only inside the designated parent. (You can use aggregation instead of composition to make a type both globally addable and explicitly addable inside another folderish type) 

archetype -- Explicitly specify that a class represents an Archetypes type. This may be necessary if you are including a class as a base class for another class and ArchGenXML is unable to determine whether the parent class is an Archetype or not. Without knowing that the parent class in an Archetype, ArchGenXML cannot ensure that the parent's schema is available in the derived class.

folder -- Make the type folderish. Folderish types can contain other types. Note that if you use composition and aggregation to specify relationships between types, the container for the aggregation will automatically be made folderish.

ordered -- For folderish types, include folder ordering support. This will allow the user to re-order items in the folder manually.

CMFMember, member -- The class will be treated as a CMFMember member type. It will derive from CMFMember's Member class and be installed as a member data type.

portal_tool -- Install the type as a portal tool. A tool is a singleton which can be accessed with 'getToolByName' from 'Products.CMFCore.utils', typically used to hold shared state or configuration information, or methods which are not bound to a particular object.


variable_schema -- Include variable schema support in a content type by deriving from the VariableSchema mixin class. 

Method stereotypes

  The following stereotypes may be applied to methods to alter their behaviour:

action -- Generate a CMF action which will be available on the object. The tagged values 'action' (defaults to method name), 'id' (defaults to method name), 'category' (defaults to 'object'), 'label' (defaults to method name), 'condition' (defaults to empty), and 'permission' (defaults to empty) set on the method and mapped to the equivalent fields of any CMF action can be used to control the behaviour of the action. 

view -- Generate an action as above, but also copy an empty page template to the skins directory with the same name as the method and set this up as the target of the action. If the template exists, it is not overwritten.

form -- Generate an action as above, but also copy an empty controller page template to the skins directory with the same name as the method and set this up as the target of the action. If the template exists, it is not overwritten.

portlet_view, portlet -- Create a simple portlet page template with the same name as the method. You can override the name by setting the 'view' tagged value on the method. If you add a tagged value 'autoinstall' and set it to 'left' or 'right', the portlet will be automatically installed with your product in either the left or the right slot. If the page template already exists, it will not be overwritten.

Field stereotypes

  The following stereotypes may be applied to fields to alter their behaviour:

vocabulary -- TODO: Describe ATVocabularyManager support

vocabulary_item -- TODO: Describe ATVocabularyManager support

vocabulary: -- TODO: Describe ATVocbularyManager support


"""
