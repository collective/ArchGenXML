<dtml-var "generator.generateModuleInfoHeader(package, name='setuphandlers')">
import logging
logger = logging.getLogger('<dtml-var "product_name">: setuphandlers')
from config import PROJECTNAME
from config import DEPENDENCIES
from Products.CMFCore.utils import getToolByName
<dtml-if "bbbExcecuteAppInstall">
from Products.ExternalMethod.ExternalMethod import ExternalMethod
</dtml-if>
##code-section HEAD
##/code-section HEAD

def installGSDependencies(context):
    """Install dependend profiles."""
    # XXX this one needs testing and review!
    dependencies = [<dtml-var "', '.join(dependend_profiles)">]
    if not dependencies:
        return
    site = context.getSite()
    setup_tool = getToolByName(site, 'portal_setup')
    for dependency in dependencies:
        if dependency.find(':') = -1:
            dependency += ':default'
        old_context = setup_tool.getImportContextID()
        setup_tool.setImportContext(dependency)
        setup_tool.runAllImportSteps()
        setup_tool.setImportContext(old_context)    

def installQIDependencies(context):
    """This is for old-style products using QuickInstaller"""
    site = context.getSite()
    qi = getToolByName(site, 'portal_quickinstaller')
    for dependency in DEPENDENCIES:
        if qi.isProductInstalled(dependency):            
            logger.info("Re-Installing dependency %s:" % dependency)
            qi.reinstallProducts([dependency])
        else:
            logger.info("Installing dependency %s:" % dependency)
            qi.installProducts([dependency])

<dtml-if "toolnames">
def setupHideToolsFromNavigation(context):
    """hide tools"""
    # uncatalog tools
    site = context.getSite()
    toolnames = <dtml-var "repr(toolnames)">
    portalProperties = getToolByName(self, 'portal_properties')    
    navtreeProperties = getattr(portalProperties, 'navtree_properties')
    if navtreeProperties.hasProperty('idsNotToList'):
    for toolname in toolnames:
        try:
            portal[toolname].unindexObject()
        except:
            pass        
        current = list(navtreeProperties.getProperty('idsNotToList'))
        if toolname not in current:
            current.append(toolname)
            navtreeProperties.manage_changeProperties({'idsNotToList': current})
                
</dtml-if>
<dtml-if "bbbExcecuteAppInstall">
def installOldSchoolAppInstall(context):
    """BBB code, deprecated, will be removed in AGX 1.7"""
    # try to call a custom install method
    # in 'AppInstall.py' method 'install'    
    try:
        install = ExternalMethod('temp', 'temp',
                                 PROJECTNAME+'.AppInstall', 'install')
    except NotFound:
        return

    logger.info('BBB code execution! AppInstall.py will be removed in AGX 1.7')
    try:
        res = install(self, reinstall)
    except TypeError:
        res = install(self)
    if res:
        logger.info("AppInstall.py returned:\n%s" % res) 
               
</dtml-if>  
##code-section FOOT
##/code-section FOOT
