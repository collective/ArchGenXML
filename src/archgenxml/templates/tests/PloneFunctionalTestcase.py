<dtml-let assocs="klass.getFromAssociations(aggtypes=['none','aggregation','composite'])"
          atts="klass.getAttributeDefs()"
          dependentImports="generator.generateDependentImports(klass)"
          additionalImports="generator.generateAdditionalImports(klass)"
          taggedImports="generator.getImportsByTaggedValues(klass)"
          vars="atts+[a.toEnd for a in assocs]">
<dtml-var "generator.getProtectedSection(parsed_class, 'module-header')">
import os, sys, code
from Testing import ZopeTestCase
from Products.Five.testbrowser import Browser
from Products.PloneTestCase import PloneTestCase
<dtml-if taggedImports><dtml-var taggedImports></dtml-if>
<dtml-if dependentImports><dtml-var dependentImports></dtml-if>
<dtml-if additionalImports><dtml-var additionalImports></dtml-if>

##code-section module-before-plone-site-setup #fill in your manual code here
##/code-section module-before-plone-site-setup
PloneTestCase.installProduct('<dtml-var "klass.getPackage().getProductName()">')
PloneTestCase.setupPloneSite()

## Base FunctionalTestCase for <dtml-var "klass.getPackage().getProductName()">.
#
# This class serves as the parent for all browser based, functional test cases.
# It provides utility methods to ease writing and running tests.
<dtml-let base_class="klass.getTaggedValue('base_class') or ','.join([p.getCleanName() for p in klass.getGenParents()])">
class <dtml-var "klass.getCleanName()">(PloneTestCase.FunctionalTestCase):
</dtml-let>
    """<dtml-var "utils.indent(klass.getDocumentation(), 1, skipFirstRow=True, stripBlank=True)">
    """
<dtml-var "generator.generateImplements(klass,[p.getCleanName() for p in klass.getGenParents()])">
<dtml-var "generator.getProtectedSection(parsed_class,'class-header_'+klass.getCleanName(),1)">

<dtml-if "not parsed_class or '__init__' not in parsed_class.methods.keys()">
<dtml-if vars>
    def __init__(self,*args,**kwargs):
        PloneTestCase.FunctionalTestCase.__init__(self,*args,**kwargs)
<dtml-in "klass.getGenParents()">
        <dtml-var "_['sequence-item'].getCleanName()">.__init__(self,*args,**kwargs)
</dtml-in>
        self._init_attributes(*args,**kwargs)
</dtml-if>
<dtml-else>
<dtml-var "parsed_class.methods['__init__'].getSrc()">
</dtml-if>
<dtml-if vars>

    def _init_attributes(self,*args,**kwargs):
        #attributes
        self.browser = None
<dtml-in atts>
<dtml-if "_['sequence-item'].mult[1]==1">
        self.<dtml-var "_['sequence-item'].getCleanName()">=None
<dtml-else>
        self.<dtml-var "_['sequence-item'].getCleanName()">=<dtml-var "{None:'[]','dict':'{}','list':'[]','tuple':'()'}.get(_['sequence-item'].getStereoType(),str(_['sequence-item'].getStereoType())+'()')">
</dtml-if>
</dtml-in>
<dtml-if assocs>
        #associations
</dtml-if>
<dtml-in assocs>
<dtml-if "_['sequence-item'].toEnd.getUpperBound()==1">
        self.<dtml-var "_['sequence-item'].toEnd.getCleanName()">=None
<dtml-else>
        self.<dtml-var "_['sequence-item'].toEnd.getCleanName()">=<dtml-var "{None:'[]','dict':'{}','list':'[]','tuple':'()'}.get(_['sequence-item'].getStereoType(),str(_['sequence-item'].getStereoType())+'()')">
</dtml-if>
</dtml-in>
        # automatically set attributes where mutators exist
        for key in kwargs.keys():
            # camel case: variable -> setVariable
            mutatorName = 'set'+key[0].upper()+key[1:]
            mutator = getattr(self, mutatorName)
            if mutator is not None and callable(mutator):
                mutator(kwargs[key])
</dtml-if>

<dtml-if "not parsed_class or 'afterSetUp' not in parsed_class.methods.keys()">
    def afterSetUp(self):
        """
        Setup utility method.
        
        This method is run after the test instance as been setup, but
        before any tests have been run.  Any product specific setup
        that need to occur before testing should go here.
        @param self The object pointer.
        """
        # setup the browser
        self.browser = Browser()
        
        # Things you may want here include (copy into protected section):
        #     self.browser.handleErrors = False
        #     self.portal.error_log._ignored_exceptions = ()
        #     self.portal.left_slots = self.portal.right_slots = []
        # Other things might include setting up users, security, etc.
<dtml-var "generator.getProtectedSection(parsed_class,'afterSetUp', 2)">
<dtml-else><dtml-var "parsed_class.methods['afterSetUp'].getSrc()">
</dtml-if>

<dtml-if "not parsed_class or 'getError' not in parsed_class.methods.keys()">
    def getError(self, error_index=0):
        """
        Error access utility method.
        
        Get the error msg as text, by default the last one.
        @param self The object pointer.
        @param error_index The index of the error of interest.  If not passed in, 
            an index of 0 is used.
        """
        error_log = self.portal.error_log
        try:
            id = error_log.getLogEntries()[0]['id']
        except IndexError:
            # no errors
            return ''
        else:
            return error_log.getLogEntryAsText(id)
<dtml-else><dtml-var "parsed_class.methods['getError'].getSrc()"></dtml-if>

<dtml-if "not parsed_class or 'printError' not in parsed_class.methods.keys()">
    def printError(self, error_index=0):
        """
        Error printing utility method.
        
        Prints an error. Useful for debugging sessions.  By default, the
        last error is printed.
        
        @param self The object pointer.
        @param error_index The index of the error of interest.  If not passed in, 
             an index of 0 is used.
        """
        print '='*70
        print self.get_error(error_index)
        print '-'*70
<dtml-else><dtml-var "parsed_class.methods['printError'].getSrc()"></dtml-if>

<dtml-if "not parsed_class or 'Session' not in parsed_class.methods.keys()">
    class Session(dict):
        def set(self, key, value):
            self[key] = value

<dtml-else><dtml-var "parsed_class.methods['Session'].getSrc()"></dtml-if>

<dtml-if "not parsed_class or '_setup' not in parsed_class.methods.keys()">
    def _setup(self):
        PloneTestCase.FunctionalTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()
<dtml-else><dtml-var "parsed_class.methods['_setup'].getSrc()"></dtml-if>

<dtml-in "generator.getMethodsToGenerate(klass)[0]">

<dtml-let m="_['sequence-item']" mn="m.getCleanName()">
<dtml-if "m.getParent() != klass">
    # from class <dtml-var "m.getParent().getName()">:
</dtml-if>
<dtml-if "parsed_class and mn in parsed_class.methods.keys()">
<dtml-var "parsed_class.methods[mn].getSrc()"><dtml-else>
    def <dtml-var "mn">(self):
<dtml-let name="'temp_'+m.getParent().getCleanName()">
        pass
</dtml-let>
</dtml-if>
</dtml-let>
</dtml-in>

    # Manually created methods
<dtml-if parsed_class>
<dtml-let allmethodnames="[m.getCleanName() for m in generator.getMethodsToGenerate(klass)[0]]">
<dtml-in "parsed_class.methods.values()">
<dtml-if "_['sequence-item'].getName() not in allmethodnames+['afterSetUp', 'getError', 'printError', '_setup', '__init__', '_init_attributes', 'Session']">

<dtml-var "_['sequence-item'].getSrc()"></dtml-if>
</dtml-in>
</dtml-let>
</dtml-if>

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(<dtml-var "klass.getCleanName()">))
    return suite

<dtml-var "generator.getProtectedSection(parsed_class,'module-footer')"></dtml-let>
