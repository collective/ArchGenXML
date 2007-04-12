import os, sys
try:
    from Products.PloneTestCase.layer import ZCMLLayer
    USELAYER = True
except:
    USELAYER = False
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

<dtml-var "generator.getProtectedSection(parsed_class, 'module-header')">
#
# Test-cases for class(es) <dtml-var "', '.join([p.getName() for p in klass.getRealizationParents()])">
#

from Testing import ZopeTestCase
<dtml-if "parent is not None">
from <dtml-var "parent.getQualifiedModuleName(None,forcePluginRoot=1)"> import <dtml-var "parent.getCleanName()">
<dtml-else>
from Products.PloneTestCase.PloneTestCase import PloneTestCase
</dtml-if>

# Import the tested classes
<dtml-in "klass.getRealizationParents() + klass.getClientDependencyClasses(includeParents=True)">
from <dtml-var "_['sequence-item'].getQualifiedModuleName(None, forcePluginRoot=1)"> import <dtml-var "_['sequence-item'].getCleanName()">
</dtml-in>


class <dtml-var "klass.getCleanName()"><dtml-if parent>(<dtml-var "parent.getCleanName()">)<dtml-else>(PloneTestCase)</dtml-if>:
<dtml-if "parsed_class and parsed_class.getDocumentation()">    """<dtml-var "parsed_class.getDocumentation()">"""
<dtml-else>    """Test-cases for class(es) <dtml-var "', '.join([p.getName() for p in klass.getRealizationParents()])">."""
</dtml-if>

<dtml-var "generator.getProtectedSection(parsed_class, 'class-header_'+klass.getCleanName(), 1)">
<dtml-if "not parsed_class or 'afterSetUp' not in parsed_class.methods.keys()">
    def afterSetUp(self):
        """
        """
        pass
<dtml-else>
<dtml-var "parsed_class.methods['afterSetUp'].getSrc()"></dtml-if>

    # Manually created methods
<dtml-if parsed_class>
<dtml-in "parsed_class.methods.values()">
<dtml-let allmethodnames="[m.testmethodName() for m in generator.getMethodsToGenerate(klass)[0]]">
<dtml-if "_['sequence-item'].getName() not in allmethodnames+['afterSetUp']">
<dtml-var "_['sequence-item'].getSrc()">
</dtml-if>
</dtml-let>
</dtml-in>
</dtml-if>


def test_suite():
    from unittest import TestSuite
    from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite

    <dtml-var "generator.getProtectedSection(parsed_class, 'test-suite-in-between')">

    s = ZopeDocFileSuite('<dtml-var "testname">.txt',
                         package='Products.<dtml-var "klass.getPackage().getProduct().getCleanName()">.doc',
                         test_class=<dtml-var "klass.getCleanName()">)
    if USELAYER:
        s.layer=ZCMLLayer
    return TestSuite((s,
                      ))

<dtml-var "generator.getProtectedSection(parsed_class, 'module-footer')">
if __name__ == '__main__':
    framework()
