<dtml-var "generator.generateModuleInfoHeader(package, name='Install')">
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.<dtml-var "package.getProductModuleName()">.config import PROJECTNAME

def install(self, reinstall=False):
    """External Method to install <dtml-var "package.getProductModuleName()"> 
    
    This method to install a product is kept, until something better will get
    part of Plones front end, which utilize portal_setup.
    """
    out = StringIO()
    print >> out, "Installation log of %s:" % PROJECTNAME

    setuptool = getToolByName(self, 'portal_setup')   
    importcontext = 'profile-Products.%s:default' % PROJECTNAME
    setuptool.setImportContext(importcontext)
    setuptool.runAllImportSteps()
    return out.getvalue()
