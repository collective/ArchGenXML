#
# Setup tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase
from Products.<dtml-var "klass.getPackage().getProductName()">.<dtml-var "klass.getGenParents()[0].getQualifiedModuleName(klass.getPackage())"> import <dtml-var "klass.getGenParents()[0].getCleanName()">

class TestSetup(<dtml-var "klass.getGenParents()[0].getCleanName()">):

    def testTools(self):
        ids = self.portal.objectIds()
        self.failUnless('archetype_tool' in ids)
        #<dtml-var "[c.getName() for c in generator.getTools(klass.getPackage().getProduct(),autoinstallOnly=1)] ">
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

