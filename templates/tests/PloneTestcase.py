#
# Base TestCase for ProductName
#

from Products.PloneTestCase import PloneTestCase

PloneTestCase.installProduct('Archetypes')
PloneTestCase.installProduct('PortalTransforms', quiet=1)
PloneTestCase.installProduct('MimetypesRegistry', quiet=1)
PloneTestCase.installProduct('<dtml-var "klass.getPackage().getProductName()">')

PRODUCTS = ('Archetypes', '<dtml-var "klass.getPackage().getProductName()">')

PloneTestCase.setupPloneSite(products=PRODUCTS)


class <dtml-var "klass.getCleanName()">(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        pass

