from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFPlone.Portal import addPolicy

class <dtml-var "package.getProductName()">CustomizationPolicy(DefaultCustomizationPolicy):
    """ Make a custom Plone for PloneMall """

    def customize(self, portal):
        ''' this method gets called during the customization '''
        DefaultCustomizationPolicy.customize( portal)

def register(context):
    addPolicy('<dtml-var "package.getProductName()">', <dtml-var "package.getProductName()">CustomizationPolicy())
