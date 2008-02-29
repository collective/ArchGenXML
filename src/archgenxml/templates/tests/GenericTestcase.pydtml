import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

<dtml-var "generator.getProtectedSection(parsed_class, 'module-header')">
#
# Test-cases for class(es) <dtml-var "', '.join([p.getName() for p in klass.getRealizationParents()])">
#

from Testing import ZopeTestCase
from Products.<dtml-var "klass.getPackage().getProductName()">.config import *
<dtml-if "parent is not None">
from <dtml-var "parent.getQualifiedModuleName(None,forcePluginRoot=1)"> import <dtml-var "parent.getCleanName()">
<dtml-else>
from Products.PloneTestCase.PloneTestCase import PloneTestCase
</dtml-if>

# Import the tested classes
<dtml-in "klass.getRealizationParents() + klass.getClientDependencyClasses(includeParents=True)">
from <dtml-var "_['sequence-item'].getQualifiedModuleName(None, forcePluginRoot=1)"> import <dtml-var "_['sequence-item'].getCleanName()">
</dtml-in>

<dtml-var "generator.getProtectedSection(parsed_class, 'module-beforeclass')">

class <dtml-var "klass.getCleanName()"><dtml-if parent>(<dtml-var "parent.getCleanName()">)<dtml-else>(PloneTestCase)</dtml-if>:
<dtml-if "parsed_class and parsed_class.getDocumentation()">    """<dtml-var "parsed_class.getDocumentation()">"""
<dtml-else>    """Test-cases for class(es) <dtml-var "', '.join([p.getName() for p in klass.getRealizationParents()])">."""
</dtml-if>

<dtml-var "generator.getProtectedSection(parsed_class, 'class-header_'+klass.getCleanName(), 1)">
<dtml-if "not parsed_class or 'afterSetUp' not in parsed_class.methods.keys()">
    def afterSetUp(self):
        pass
<dtml-else><dtml-var "parsed_class.methods['afterSetUp'].getSrc()"></dtml-if>
<dtml-in "generator.getMethodsToGenerate(klass)[0]">

<dtml-let m="_['sequence-item']" mn="m.testmethodName()">
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
<dtml-let allmethodnames="[m.testmethodName() for m in generator.getMethodsToGenerate(klass)[0]]">
<dtml-in "parsed_class.methods.values()">
<dtml-if "_['sequence-item'].getName() not in allmethodnames+['afterSetUp']">

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
