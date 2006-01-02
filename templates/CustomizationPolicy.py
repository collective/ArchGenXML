<dtml-var "generator.generateModuleInfoHeader(package)">
from zLOG import LOG, INFO
from Products.CMFPlone.Portal import addPolicy
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from config import PROJECTNAME


class <dtml-var "package.getProductName()">CustomizationPolicy(DefaultCustomizationPolicy):
    """Make a custom Plone for <dtml-var "package.getProductName()">."""

    def customize(self, portal):
        """Custom customize method."""
        # If the customization Policy id called inside an already existing
        # portal, calling the DefaultCustomizationPolicy.customize is a
        # problem
        # ugly try catch arround works, but should somewhere in future be
        # replaced by a test from which location we are calling.
        try:
            DefaultCustomizationPolicy.customize(self, portal)
        except:
            pass

        # Call all methods starting with 'customize'
        LOG(PROJECTNAME, INFO, "Customization Policy applied:")
        for method in dir(self):
            if method.startswith('customize') and method!='customize':
                print "Processing customization '%s' ..." % method
                eval('self.%s(portal)' % method)

    def customize_1_InstallProducts(self, portal):
        """Install the product.

        Note that you can add dependencies to the DEPENDENCIES list in
        config.py, these are auto-installed by Install.py so no need
        to add them here.
        """
        portal.portal_quickinstaller.installProduct(PROJECTNAME)
        get_transaction().commit(1)

    # Define your own customize_#_name methods after this line


def register(context):
    addPolicy('<dtml-var "package.getProductName()">', <dtml-var "package.getProductName()">CustomizationPolicy())
