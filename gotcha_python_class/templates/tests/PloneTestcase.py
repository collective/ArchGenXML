import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

<dtml-var "generator.getProtectedSection(parsed_class,'module-header')">
#
# Base TestCase for <dtml-var "klass.getPackage().getProductName()">
#
from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
<dtml-if "parent is not None">
<dtml-if "parent.hasStereoType('stub')">
from <dtml-var "parent.getTaggedValue('import_from')"> import <dtml-var "parent.getCleanName()">
<dtml-else>
from <dtml-var "parent.getQualifiedModuleName(None,forcePluginRoot=1)"> import <dtml-var "parent.getCleanName()">
</dtml-if>
</dtml-if>

ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('MimetypesRegistry', quiet=1)
ZopeTestCase.installProduct('<dtml-var "klass.getPackage().getProductName()">')
# If the products's config includes DEPENDENCIES, install them too
try:
    from Products.<dtml-var "klass.getPackage().getProductName()">.config import DEPENDENCIES
except:
    DEPENDENCIES = []
for dependency in DEPENDENCIES:
    ZopeTestCase.installProduct(dependency)

PRODUCTS = ('Archetypes', '<dtml-var "klass.getPackage().getProductName()">')

testcase = <dtml-if "parent is not None"><dtml-var "parent.getCleanName()"><dtml-else>PloneTestCase.PloneTestCase</dtml-if>

PloneTestCase.setupPloneSite(products=PRODUCTS<dtml-if "klass.getTaggedValue('policy', None)">, policy="<dtml-var "klass.getTaggedValue('policy')">"</dtml-if>)

<dtml-var "generator.getProtectedSection(parsed_class, 'module-beforeclass')">

class <dtml-var "klass.getCleanName()">(testcase):
    """ Base TestCase for <dtml-var "klass.getPackage().getProductName()">"""
<dtml-var "generator.getProtectedSection(parsed_class,'class-header_'+klass.getCleanName(),1)">
    # Commented out for now, it gets blasted at the moment anyway.
    # Place it in the protected section if you need it.
    #def afterSetUp(self):
    #    """
    #    """
    #    pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(<dtml-var "klass.getCleanName()">))
    return suite

<dtml-var "generator.getProtectedSection(parsed_class,'module-footer')">

if __name__ == '__main__':
    framework()
