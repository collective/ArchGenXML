<dtml-var "generator.getProtectedSection(parsed_class,'module-header')">
#
# Base TestCase for <dtml-var "klass.getPackage().getProductName()">
#

from Products.PloneTestCase import PloneTestCase

PloneTestCase.installProduct('Archetypes')
PloneTestCase.installProduct('PortalTransforms', quiet=1)
PloneTestCase.installProduct('MimetypesRegistry', quiet=1)
PloneTestCase.installProduct('<dtml-var "klass.getPackage().getProductName()">')
# If the products's config includes DEPENDENCIES, install them too
try:
    from Products.<dtml-var "klass.getPackage().getProductName()">.config import DEPENDENCIES
except:
    DEPENDENCIES = []
for dependency in DEPENDENCIES:
    PloneTestCase.installProduct(dependency)

PRODUCTS = ('Archetypes', '<dtml-var "klass.getPackage().getProductName()">')

PloneTestCase.setupPloneSite(products=PRODUCTS)


class <dtml-var "klass.getCleanName()">(PloneTestCase.PloneTestCase):
    """ Base TestCase for <dtml-var "klass.getPackage().getProductName()">"""
<dtml-var "generator.getProtectedSection(parsed_class,'class-header_'+klass.getCleanName(),1)">
    def afterSetUp(self):
        pass

<dtml-var "generator.getProtectedSection(parsed_class,'module-footer')">
