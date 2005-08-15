"""
Copy-paste stuff in other files that needs to be handled.

From XMIParser:

    def isRoot(self):
        # TBD Handle this through the stereotype registry
        return self.isroot or self.hasStereoType(['product', 'zopeproduct', 'Product', 'ZopeProduct'])

    def setStereoType(self, st):
        # TBD: stereotypesupport integration
        self.stereoTypes = [st]

    def getStereoType(self):
        # TBD: stereotypesupport integration
        if self.stereoTypes:
            return self.stereoTypes[0]
        else:
            return None

    def addStereoType(self, st):
        # TBD: stereotypesupport integration
        log.debug("Adding stereotype '%s' to this element's internal list.",
                  st)
        self.stereoTypes.append(st)

    def getClientDependencies(self, includeParents=False, dependencyStereotypes=None):
                                                          ^^^^^^^^^^^^^^^^^^^^^
    def isInterface(self):
        #print 'interface:', self.getName(), self.getStereoType()
        return self.isinterface  or self.getStereoType() == 'interface'

    def isI18N(self):
        ' with a stereotype 'i18N' or the taggedValue i18n == '1' an attribute is treated as i18n'
        return self.getStereoType() == 'i18n' or self.getTaggedValue('i18n')  == '1'


From ArchetypesGenerator.py:

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
    uml_profile.addStereoType('doc_testcase',['XMIClass'],dispatching=1,
        generator='generateDocTestcaseClass',template='tests/DocTestcase.py')
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

    stub_stereotypes=['odStub','stub']
    archetype_stereotype = ['archetype']
    vocabulary_item_stereotype = ['vocabulary_term']
    vocabulary_container_stereotype = ['vocabulary']
    cmfmember_stereotype = ['CMFMember', 'member']
    python_stereotype = ['python', 'python_class']

    i18n_at=['i18n-archetypes','i18n', 'i18n-at']
    generate_datatypes=['field','compound_field']

    def generateMethodActions(self,element):
        outfile=StringIO()
        print >> outfile
        for m in element.getMethodDefs():
            code=indent(m.getTaggedValue('code',''),1)
            if m.hasStereoType( ['action','view','form']):
                [.......]
            if m.hasStereoType('view'):
            elif m.hasStereoType('form'):
            elif m.hasStereoType(['portlet_view','portlet']):


        if element.hasStereoType(self.variable_schema):
        # ATVocabularyManager imports
        if element.hasStereoType(self.vocabulary_item_stereotype):
            print >> outfile, 'from Products.ATVocabularyManager.tools import registerVocabularyTerm'
        if element.hasStereoType(self.vocabulary_container_stereotype):
            print >> outfile, 'from Products.ATVocabularyManager.tools import registerVocabulary'
        if element.hasAttributeWithTaggedValue('vocabulary:type','ATVocabularyManager'):
            print >> outfile, 'from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary'

        if element.hasStereoType('hidden'):

        # Or if it is a tool-like thingy
        if (element.hasStereoType(self.portal_tools) or 
            element.hasStereoType(self.vocabulary_item_stereotype) or
            element.hasStereoType(self.cmfmember_stereotype) or 
            element.isAbstract()):

        # If we are generating a tool, include the template which sets
        # a tool icon
        if element.hasStereoType(self.portal_tools):

                if rel.hasStereoType(self.stub_stereotypes) :

                if element.hasStereoType(self.cmfmember_stereotype):

        if element.hasStereoType(self.portal_tools) and '__init__' not in method_names:

    def generateMethod(self, outfile, m, klass, mode='class'):
        #ignore actions and views here because they are
        #generated separately
        if m.hasStereoType(['action','view','form','portlet_view']):

    def generateTestcaseClass(self,element,template,**kw):
        from XMIParser import XMIClass
        
        log.info("Generating testcase '%s'.",
                 element.getName())
        
        assert element.hasStereoType('plone_testcase') or element.getCleanName().startswith('test'), \
            "names of test classes _must_ start with 'test', but this class is named '%s'" % element.getCleanName()

        assert element.getPackage().getCleanName() == 'tests', \

        widgets=element.getClientDependencyClasses(targetStereotypes=['widget'])

                      element.hasStereoType(['folder','ordered'])

                                  p.hasStereoType(self.archetype_stereotype)

            if element.hasStereoType('ordered'):
                baseclass ='OrderedBaseFolder'
                baseschema='OrderedBaseFolderSchema'
            elif element.hasStereoType(['large','btree']):

           and not element.hasStereoType('mixin'):

        packageImports = [m.getModuleName() for m in package.getAnnotation('generatedPackages') if not m.hasStereoType('tests') or []]
        classImports   = [m.getModuleName() for m in package.generatedModules if not m.hasStereoType('tests')]


DESIGN
======

So we need, per stereotype:

* name
* xmi element it s valid for
* documentation

We need to integrate with:

* getStereoType
* addStereoType

And we need to support the .hasStereoType(self.stub_stereotypes) kind
of handling, so:

* add category (like 'stub') to stereotype.
* should be multi-category enabled.

"""'''

class StereotypeRegistry():
    pass


