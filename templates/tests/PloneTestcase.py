#
# Base TestCase for <dtml-var "klass.getPackage().getProductName()">
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

<dtml-var "generator.getProtectedSection(parsed_class,'module-header')">
from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
<dtml-if "parent is not None">
<dtml-if "parent.hasStereoType('stub')">
from <dtml-var "parent.getTaggedValue('import_from')"> import <dtml-var "parent.getCleanName()">
<dtml-else>
from <dtml-var "parent.getQualifiedModuleName(None,forcePluginRoot=1)"> import <dtml-var "parent.getCleanName()">
</dtml-if>
</dtml-if>
from Products.<dtml-var "klass.getPackage().getProductName()">.config import HAS_PLONE21
from Products.<dtml-var "klass.getPackage().getProductName()">.config import PRODUCT_DEPENDENCIES
from Products.<dtml-var "klass.getPackage().getProductName()">.config import DEPENDENCIES

# Add common dependencies
if not HAS_PLONE21:
    DEPENDENCIES.append('Archetypes')
    PRODUCT_DEPENDENCIES.append('MimetypesRegistry')
    PRODUCT_DEPENDENCIES.append('PortalTransforms')
PRODUCT_DEPENDENCIES.append('<dtml-var "klass.getPackage().getProductName()">')

# Install all (product-) dependencies, install them too
for dependency in PRODUCT_DEPENDENCIES + DEPENDENCIES:
    ZopeTestCase.installProduct(dependency)

ZopeTestCase.installProduct('<dtml-var "klass.getPackage().getProductName()">')

PRODUCTS = list()
<dtml-if "klass.getTaggedValue('quickinstall_dependencies', '1') == '1'">
PRODUCTS += DEPENDENCIES
</dtml-if>
<dtml-if "klass.getTaggedValue('quickinstall_self', '1') == '1'">
PRODUCTS.append('<dtml-var "klass.getPackage().getProductName()">')
</dtml-if>

testcase = <dtml-if "parent is not None"><dtml-var "parent.getCleanName()"><dtml-else>PloneTestCase.PloneTestCase</dtml-if>


<dtml-var "generator.getProtectedSection(parsed_class,'module-before-plone-site-setup')">
PloneTestCase.setupPloneSite(products=PRODUCTS<dtml-if "klass.getTaggedValue('policy', None)">, policy=<dtml-var "generator.processExpression(klass.getTaggedValue('policy'))"></dtml-if>)

class <dtml-var "klass.getCleanName()">(testcase):
    """Base TestCase for <dtml-var "klass.getPackage().getProductName()">."""

<dtml-var "generator.getProtectedSection(parsed_class,'class-header_'+klass.getCleanName(),1)">
    # Commented out for now, it gets blasted at the moment anyway.
    # Place it in the protected section if you need it.
    #def afterSetup(self):
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
