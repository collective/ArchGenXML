import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

<dtml-var "generator.getProtectedSection(parsed_class, 'module-header')">
#
# Setup tests
#

import os, sys
from Testing import ZopeTestCase
<dtml-if "parent is not None">
from <dtml-var "parent.getQualifiedModuleName(None,forcePluginRoot=1)"> import <dtml-var "parent.getCleanName()">
</dtml-if>

class <dtml-var "klass.getCleanName()"><dtml-if parent>(<dtml-var "parent.getCleanName()">)</dtml-if>:
<dtml-if "parsed_class and parsed_class.getDocumentation()">    """<dtml-var "parsed_class.getDocumentation()">"""
<dtml-else>    """Test cases for the generic setup of the product."""
</dtml-if>

<dtml-var "generator.getProtectedSection(parsed_class, 'class-header_'+klass.getCleanName(), 1)">
<dtml-if "not parsed_class or 'afterSetUp' not in parsed_class.methods.keys()">
    def afterSetUp(self):
        ids = self.portal.objectIds()
<dtml-else><dtml-var "parsed_class.methods['afterSetUp'].getSrc()"></dtml-if>

<dtml-if "not parsed_class or 'test_tools' not in parsed_class.methods.keys()">
    def test_tools(self):
        ids = self.portal.objectIds()
        self.failUnless('archetype_tool' in ids)
<dtml-call "generator.getTools(klass.getPackage().getProduct())">
<dtml-else><dtml-var "parsed_class.methods['test_tools'].getSrc()"></dtml-if>

<dtml-if "not parsed_class or 'test_types' not in parsed_class.methods.keys()">
    def test_types(self):
        ids = self.portal.portal_types.objectIds()
        self.failUnless('Document' in ids)
<dtml-else><dtml-var "parsed_class.methods['test_types'].getSrc()"></dtml-if>

<dtml-if "not parsed_class or 'test_skins' not in parsed_class.methods.keys()">
    def test_skins(self):
        ids = self.portal.portal_skins.objectIds()
        self.failUnless('plone_templates' in ids)
<dtml-else><dtml-var "parsed_class.methods['test_skins'].getSrc()"></dtml-if>

<dtml-if "not parsed_class or 'test_workflows' not in parsed_class.methods.keys()">
    def test_workflows(self):
        ids = self.portal.portal_workflow.objectIds()
        self.failUnless('plone_workflow' in ids)
<dtml-else><dtml-var "parsed_class.methods['test_workflows'].getSrc()"></dtml-if>

<dtml-if "not parsed_class or 'test_workflowChains' not in parsed_class.methods.keys()">
    def test_workflowChains(self):
        getChain = self.portal.portal_workflow.getChainForPortalType
        self.failUnless(('plone_workflow' in getChain('Document')) or ('simple_publication_workflow' in getChain('Document')))
<dtml-else><dtml-var "parsed_class.methods['test_workflowChains'].getSrc()"></dtml-if>
<dtml-in "generator.getMethodsToGenerate(klass)[0]">

<dtml-let m="_['sequence-item']" mn="m.testmethodName()">
<dtml-if "m.getParent() != klass">
    # from class <dtml-var "m.getParent().getName()">:
</dtml-if>
<dtml-if "parsed_class and mn in parsed_class.methods.keys()"><dtml-var "parsed_class.methods[mn].getSrc()"><dtml-else>
    def <dtml-var "mn">(self):
        pass
</dtml-if>
</dtml-let>
</dtml-in>

    # Manually created methods
<dtml-if parsed_class>
<dtml-let allmethodnames="[m.testmethodName() for m in generator.getMethodsToGenerate(klass)[0]]">
<dtml-in "parsed_class.methods.values()">
<dtml-if "_['sequence-item'].getName() not in allmethodnames+['afterSetUp', 'test_tools',
            'test_types', 'test_skins', 'test_workflows', 'test_workflowChains']">

<dtml-var "_['sequence-item'].getSrc()"></dtml-if>
</dtml-in>
</dtml-let>
</dtml-if>


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(<dtml-var "klass.getCleanName()">))
    return suite

<dtml-var "generator.getProtectedSection(parsed_class, 'module-footer')">
if __name__ == '__main__':
    framework()
