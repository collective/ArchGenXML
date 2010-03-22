#
# Base TestCase for <dtml-var "klass.getPackage().getProductName()">
#

import os, sys, code
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
from Products.<dtml-var "klass.getPackage().getProductName()">.config import PRODUCT_DEPENDENCIES
from Products.<dtml-var "klass.getPackage().getProductName()">.config import DEPENDENCIES

# Add common dependencies
DEPENDENCIES.append('Archetypes')
PRODUCT_DEPENDENCIES.append('MimetypesRegistry')
PRODUCT_DEPENDENCIES.append('PortalTransforms')
PRODUCT_DEPENDENCIES.append('<dtml-var "klass.getPackage().getProductName()">')

# Install all (product-) dependencies, install them too
for dependency in PRODUCT_DEPENDENCIES + DEPENDENCIES:
    ZopeTestCase.installProduct(dependency)

ZopeTestCase.installProduct('<dtml-var "klass.getPackage().getProductName()">')

PRODUCTS = list()
PRODUCTS += DEPENDENCIES
PRODUCTS.append('<dtml-var "klass.getPackage().getProductName()">')

testcase = <dtml-if "parent is not None"><dtml-var "parent.getCleanName()"><dtml-else>PloneTestCase.PloneTestCase</dtml-if>

<dtml-var "generator.getProtectedSection(parsed_class,'module-before-plone-site-setup')">
PloneTestCase.setupPloneSite(products=PRODUCTS)

class <dtml-var "klass.getCleanName()">(testcase):
    """Base TestCase for <dtml-var "klass.getPackage().getProductName()">."""

<dtml-var "generator.getProtectedSection(parsed_class,'class-header_'+klass.getCleanName(),1)">
    # Commented out for now, it gets blasted at the moment anyway.
    # Place it in the protected section if you need it.
    #def afterSetup(self):
    #    """
    #    """
    #    pass

    def interact(self, locals=None):
        """Provides an interactive shell aka console inside your testcase.

        It looks exact like in a doctestcase and you can copy and paste
        code from the shell into your doctest. The locals in the testcase are
        available, becasue you are in the testcase.

        In your testcase or doctest you can invoke the shell at any point by
        calling::

            >>> self.interact( locals() )

        locals -- passed to InteractiveInterpreter.__init__()
        """
        savestdout = sys.stdout
        sys.stdout = sys.stderr
        sys.stderr.write('='*70)
        console = code.InteractiveConsole(locals)
        console.interact("""
ZopeTestCase Interactive Console
(c) BlueDynamics Alliance, Austria - 2005

Note: You have the same locals available as in your test-case.
""")
        sys.stdout.write('\nend of ZopeTestCase Interactive Console session\n')
        sys.stdout.write('='*70+'\n')
        sys.stdout = savestdout


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(<dtml-var "klass.getCleanName()">))
    return suite

<dtml-var "generator.getProtectedSection(parsed_class,'module-footer')">
if __name__ == '__main__':
    framework()
