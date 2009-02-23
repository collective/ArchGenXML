# -*- coding: utf-8 -*-
#
# File: atumlprofile.py
#
# the uml profile for archetypes
#
# Created:     2007/09/09

from UMLProfile import UMLProfile
from BaseGenerator import BaseGenerator

at_uml_profile = UMLProfile(BaseGenerator.uml_profile)

at_uml_profile.addStereoType(
    'portal_tool', ['XMIClass'],
    description='Turns the class into a portal tool.')

at_uml_profile.addStereoType(
    'stub', ['XMIClass', 'XMIModel', 'XMIPackage', 'XMIInterface'],
    description='Prevents a class/package/model from being generated.')

at_uml_profile.addStereoType(
    'odStub', ['XMIClass', 'XMIModel', 'XMIPackage'],
    description='Prevents a class/package/model from being generated. '
    "Same as '<<stub>>'.")

at_uml_profile.addStereoType(
    'content_class', ['XMIClass'],
    dispatching=1,
    generator='generateArchetypesClass',
    description='TODO')

at_uml_profile.addStereoType(
    'flavor', ['XMIClass'],
    dispatching=1,
    generator='generateFlavor',
    description='Generates a ContentFlavors'' flavor from this class.')

at_uml_profile.addStereoType(
    'tests', ['XMIPackage'],
    description='Treats a package as test package. Inside such a test '
    "package, you need at a '<<plone_testcase>>' and a "
    "'<<setup_testcase>>'.")

at_uml_profile.addStereoType(
    'plone_testcase', ['XMIClass'],
    dispatching=1,
    template='tests/PloneTestcase.pydtml',
    generator='generateBaseTestcaseClass',
    description='Turns a class into the (needed) base class for all '
    "other '<<testcase>>' and '<<doc_testcase>>' classes "
    "inside a '<<test>>' package.")

at_uml_profile.addStereoType(
    'testcase', ['XMIClass'],
    dispatching=1,
    template='tests/GenericTestcase.pydtml',
    generator='generateTestcaseClass',
    description='Turns a class into a testcase. It must subclass a '
    "'<<plone_testcase>>'. Adding an interface arrow to "
                'another class automatically adds that class\'s '
                'methods to the testfile for testing.')

at_uml_profile.addStereoType(
    'plonefunctional_testcase', ['XMIClass'],
    dispatching=1,
    template='tests/PloneFunctionalTestcase.pydtml',
    generator='generateBaseFunctionalTestcaseClass',
    description='Turns a class into the base class for all '
    "other '<<functionaltestcase>>' classes inside a '<<test>>' package.")

at_uml_profile.addStereoType(
    'functional_testcase', ['XMIClass'],
    dispatching=1,
    template='tests/GenericFunctionalTestcase.pydtml',
    generator='generateFunctionalTestcaseClass',
    description='Turns a class into a functional testcase. It must subclass a '
    "'<<functional_testcase>>'. Adding an interface arrow to "
                'another class automatically adds that class\'s '
                'methods to the testfile for testing.')

at_uml_profile.addStereoType(
    'doc_testcase', ['XMIClass'],
    dispatching=1,
    template='tests/DocTestcase.pydtml',
    generator='generateDocTestcaseClass',
    description='Turns a class into a doctest class. It must subclass '
    "a '<<plone_testcase>>'.")

at_uml_profile.addStereoType(
    'functional_doc_testcase', ['XMIClass'],
    dispatching=1,
    template='tests/DocTestcase.pydtml',
    generator='generateDocTestcaseClass',
    description='Turns a class into a functional doctest class. It must subclass a '
    "'<<plone_testcase>>'.")

at_uml_profile.addStereoType(
    'setup_testcase', ['XMIClass'],
    dispatching=1,
    generator='generateTestcaseClass',
    template='tests/SetupTestcase.pydtml',
    description='Turns a class into a testcase for the setup, with '
                'pre-defined common checks.')

at_uml_profile.addStereoType(
    'interface_testcase', ['XMIClass'],
    dispatching=1,
    generator='generateTestcaseClass',
    template='tests/InterfaceTestcase.pydtml',
    description='Turns a class into a testcase for the interfaces.')

at_uml_profile.addStereoType(
    'field', ['XMIClass'],
    dispatching=1,
    generator='generateFieldClass',
    template='field.pydtml',
    description='Class will target in a ObjectField or CompoundField '
                '(latter if Attributes are provided)')

at_uml_profile.addStereoType(
    'widget', ['XMIClass'],
    dispatching=1,
    generator='generateWidgetClass',
    template='widget.pydtml',
    description='A simple stub archetypes-widget class will be created.')

at_uml_profile.addStereoType(
    'value_class', ['XMIDependency'],
    description='Declares a class to be used as value class for a '
    "certain field class (see '<<field>>' stereotype).")

at_uml_profile.addStereoType(
    'remember', ['XMIClass'],
    description='The class will be treated as a remember member '
    'type. It will derive from remember\'s Member '
    'class and be installed as a member data type. '
    'Note that you need to install the separate remember product. ')

at_uml_profile.addStereoType(
    'action', ['XMIMethod', 'XMIOperation'],
    description='Generate a CMF action which will be available on the '
                'object. The tagged values "action" (defaults to method '
                'name), "id" (defaults to method name), "category" '
                '(defaults to "object"), "label" (defaults to method '
                'name), "condition" (defaults to empty), and "permission" '
                '(defaults to empty) set on the method and mapped to '
                'the equivalent fields of any CMF action can be used to '
                'control the behaviour of the action.')

at_uml_profile.addStereoType(
    'noaction', ['XMIMethod', 'XMIOperation'],
    description="Disables standard actions, applied to a method out of 'view', "
                "'edit', 'metadata', 'references.")

at_uml_profile.addStereoType(
    'archetype', ['XMIClass'],
    description='Explicitly specify that a class represents an Archetypes '
                'type. This may be necessary if you are including a class '
                'as a base class for another class and ArchGenXML is unable '
                'to determine whether the parent class is an Archetype '
                'or not. Without knowing that the parent class in an '
                'Archetype, ArchGenXML cannot ensure that the parent\'s '
                'schema is available in the derived class.')

at_uml_profile.addStereoType(
    'btree', ['XMIClass'],
    description="Like '<<folder>>', it generates a folderish object. "
                'But it uses a BTree folder for support of large amounts '
    "of content. The same as '<<large>>'.")

at_uml_profile.addStereoType(
    'large', ['XMIClass'],
    description="Like '<<folder>>', it generates a folderish object. "
                'But it uses a BTree folder for support of large amounts '
    "of content. The same as '<<large>>'.")

at_uml_profile.addStereoType(
    'folder', ['XMIClass'],
    description='Turns the class into a folderish object. When a UML '
                'class contains or aggregates other classes, it is '
                'automatically turned into a folder; this stereotype '
                'can be used to turn normal classes into folders, too.')

at_uml_profile.addStereoType(
    'atfolder', ['XMIClass'],
    description='Turns the class into an ATFolder subclass.',
    imports=['from Products.ATContentTypes.content.folder import ATFolder',
             'from Products.ATContentTypes.content.folder ' + \
             'import ATFolderSchema',]
    )

at_uml_profile.addStereoType(
    'atfile', ['XMIClass'],
    description='Turns the class into an ATFile subclass.',
    imports=['from Products.ATContentTypes.content.file import ATFile',
             'from Products.ATContentTypes.content.file import ATFileSchema',]
    )

at_uml_profile.addStereoType(
    'atevent', ['XMIClass'],
    description='Turns the class into an ATEvent subclass.',
    imports=['from Products.ATContentTypes.content.event import ATEvent',
             'from Products.ATContentTypes.content.event import ATEventSchema',]
    )

at_uml_profile.addStereoType(
    'atnewsitem', ['XMIClass'],
    description='Turns the class into an ATNewsItem subclass.',
    imports=['from Products.ATContentTypes.content.newsitem import ATNewsItem',
             'from Products.ATContentTypes.content.newsitem import ATNewsItemSchema',]
    )

at_uml_profile.addStereoType(
    'atimage', ['XMIClass'],
    description='Turns the class into an ATImage subclass.',
    imports=['from Products.ATContentTypes.content.image import ATImage',
             'from Products.ATContentTypes.content.image import ATImageSchema',]
    )

at_uml_profile.addStereoType(
    'atlink', ['XMIClass'],
    description='Turns the class into an ATLink subclass.',
    imports=['from Products.ATContentTypes.content.link import ATLink',
             'from Products.ATContentTypes.content.link import ATLinkSchema',]
    )

at_uml_profile.addStereoType(
    'atblob', ['XMIClass'],
    description='Turns the class into an plone.app.blob.content.ATBlob subclass.',
    imports=['from plone.app.blob.content import ATBlob',
             'from plone.app.blob.content import ATBlobSchema',]
    )

at_uml_profile.addStereoType(
    'atdocument', ['XMIClass'],
    description='Turns the class into an Atdocument subclass.',
    imports=['from Products.ATContentTypes.content.document import ATDocument',
             'from Products.ATContentTypes.content.document ' + \
             'import ATDocumentSchema',]
    )

at_uml_profile.addStereoType(
    'ordered', ['XMIClass'],
    description='For folderish types, include folder ordering support. '
                'This will allow the user to re-order items in the folder '
                'manually.')

at_uml_profile.addStereoType(
    'form', ['XMIMethod', 'XMIOperation'],
    description="Generate an action like with the '<<action>>' stereotype, "
                'but also copy an empty controller page template to the '
                'skins directory with the same name as the method and set '
                'this up as the target of the action. If the template '
                'already exists, it is not overwritten.')

at_uml_profile.addStereoType(
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

at_uml_profile.addStereoType(
    'mixin', ['XMIClass'],
    description='Don\'t inherit automatically from "BaseContent" and so. '
                'This makes the class suitable as a mixin class. See also '
    "'<<archetype>>'.")

at_uml_profile.addStereoType(
    'tool', ['XMIClass'],
    description='Turns the class into a portal tool. Similar to '
    "'<<portal_tool>>'.")

at_uml_profile.addStereoType(
    'variable_schema', ['XMIClass'],
    description='Include variable schema support in a content type by '
                'deriving from the VariableSchema mixin class.')

at_uml_profile.addStereoType(
    'extender', ['XMIClass'],
    description='Is a schema extender supported by archetypes.schemaextender.')

at_uml_profile.addStereoType(
    'adapts', ['XMIAbstraction'],
    description='On a realization, specify a class (<<adapter>>, <<named_adapter>>, <<extender>>) adapts another class (<<stub>>, <<interface>>).')

at_uml_profile.addStereoType(
    'interface', ['XMIClass'],
    description='Is an interface.')

at_uml_profile.addStereoType(
    'named_adapter', ['XMIClass'],
    description='Is a named adapter.')

at_uml_profile.addStereoType(
    'adapter', ['XMIClass'],
    description='Is a (non-named) adapter.')

at_uml_profile.addStereoType(
    'view', ['XMIMethod', 'XMIOperation'],
    description="Generate an action like with the '<<action>>' stereotype, "
                'but also copy an empty page template to the skins '
                'directory with the same name as the method and set this '
                'up as the target of the action. If the template exists, '
                'it is not overwritten.')

at_uml_profile.addStereoType(
    'vocabulary', ['XMIClass'],
    description='TODO')

at_uml_profile.addStereoType(
    'vocabulary_term', ['XMIClass'],
    description='TODO')
