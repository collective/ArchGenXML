<dtml-var "generator.getProtectedSection(parsed_class, 'module-header')">
<dtml-let allmethodnames="['test%s%s' % (m.getParent().getCleanName().capitalize(), m.getCleanName().capitalize()) for m in generator.getMethodsToGenerate(klass)[0]]">
#
# Setup tests
#
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase
from Products.<dtml-var "klass.getPackage().getProductName()">.<dtml-var "klass.getGenParents()[0].getQualifiedModuleName(klass.getPackage())"> import <dtml-var "klass.getGenParents()[0].getCleanName()">

class TestSetup(<dtml-var "klass.getGenParents()[0].getCleanName()">):

<dtml-var "generator.getProtectedSection(parsed_class, 'class-header_'+klass.getCleanName(), 1)">

<dtml-in "generator.getMethodsToGenerate(klass)[0]">
<dtml-let m="_['sequence-item']" mn="'test%s%s'%(m.getParent().getCleanName().capitalize(), m.getCleanName().capitalize())">
<dtml-if "m.getParent() != klass"> 
    # from class <dtml-var "m.getParent().getName()">:
</dtml-if>
<dtml-if "parsed_class and mn in parsed_class.methods.keys()">
<dtml-var "parsed_class.methods[mn].getSrc()">
 
<dtml-else>
    def <dtml-var "mn">(self):
<dtml-let name="'temp_'+m.getParent().getCleanName()">
        ''' '''
        #Uncomment one of the followng lines as needed
        ##self.loginAsPortalOwner()
        <dtml-if "m.getParent() != klass">
        
        ##o=<dtml-var "m.getParent().getCleanName()">('<dtml-var name>')
        ##self.folder._setObject('<dtml-var name>', o)
        </dtml-if>
        
        pass
        
</dtml-let>
</dtml-if>
</dtml-let>
</dtml-in>
    
    # Manually created methods
<dtml-if parsed_class>
<dtml-in "parsed_class.methods.values()">
<dtml-if "_['sequence-item'].getName() not in allmethodnames+['afterSetUp']">
<dtml-var "_['sequence-item'].getSrc()">
        
</dtml-if>
</dtml-in>
</dtml-if>
    # Auto-added by testcase generation - probably bug
    def testTools(self):
        ids = self.portal.objectIds()
        self.failUnless('archetype_tool' in ids)
        #<dtml-var "[c.getName() for c in generator.getTools(klass.getPackage().getProduct(), autoinstallOnly=1)] ">
        # ...

    def testTypes(self):
        ids = self.portal.portal_types.objectIds()
        self.failUnless('Document' in ids)
        # ...

    def testSkins(self):
        ids = self.portal.portal_skins.objectIds()
        self.failUnless('plone_templates' in ids)
        # ...

    def testWorkflows(self):
        ids = self.portal.portal_workflow.objectIds()
        self.failUnless('plone_workflow' in ids)
        # ...

    def testWorkflowChains(self):
        getChain = self.portal.portal_workflow.getChainForPortalType
        self.failUnless('plone_workflow' in getChain('Document'))
        # ...


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite

if __name__ == '__main__':
    framework()

</dtml-let>
<dtml-var "generator.getProtectedSection(parsed_class, 'module-footer')">
