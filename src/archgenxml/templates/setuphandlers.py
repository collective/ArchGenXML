<dtml-var "generator.generateModuleInfoHeader(package, name='setuphandlers')">
import logging
logger = logging.getLogger('<dtml-var "product_name">: setuphandlers')
from config import PROJECTNAME
from config import DEPENDENCIES
from config import product_globals

from Products.CMFCore.utils import getToolByName
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
        if dependency.find(':') == -1:
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
<dtml-if "catalogmultiplexed">
def setupCatalogMultiplex(context):
    """ Configure CatalogMultiplex.
    
    explicit add classes (meta_types) be indexed in catalogs (white)
    or removed from indexing in a catalog (black) 
    """
    site = context.getSite()
    muliplexed = <dtml-var "repr(catalogmultiplexed)">

    atool = getToolByName(site, 'archetypes_tool')
    catalogmap = {}
<dtml-in "catalogmultiplexed">
<dtml-let klass="_['sequence-item']">
    catalogmap['<dtml-var "klass.getCleanName()">'] = {}
<dtml-if "generator.getOption('catalogmultiplex:white', klass, None)">
    catalogmap['<dtml-var "klass.getCleanName()">']['white'] = [<dtml-var "', '.join( ['\'%s\'' % s.strip() for s in generator.getOption('catalogmultiplex:white', klass).split(',')])">]
</dtml-if>
<dtml-if "generator.getOption('catalogmultiplex:black', klass, None)">
    catalogmap['<dtml-var "klass.getCleanName()">']['black'] = [<dtml-var "', '.join( ['\'%s\'' % s.strip() for s in generator.getOption('catalogmultiplex:black', klass).split(',')])">]
</dtml-if>
</dtml-let>
</dtml-in>
    for meta_type in catalogmap:
        submap = catalogmap[meta_type]
        current_catalogs = Set([c.id for c in atool.getCatalogsByType(meta_type)])
        if 'white' in submap:
            for catalog in submap['white']:
                if not getToolByName(self, catalog, False):
                    raise AttributeError, 'Catalog "%s" does not exist!' % catalog
                current_catalogs.update([catalog])
        if 'black' in submap:
            for catalog in submap['black']:
                if catalog in current_catalogs:
                    current_catalogs.remove(catalog)
        atool.setCatalogsByType(meta_type, list(current_catalogs))
        
</dtml-if>
<dtml-if "catalogmultiplexed">
def installRelations(context):
    """imports the relations.xml file"""
    site = context.getSite()
    relations_tool = getToolByName(site,'relations_library')
    xmlpath = os.path.join(package_home(product_globals), 'data', 
                           'relations.xml')
    f = open(xmlpath)
    xml = f.read()
    f.close()
    relations_tool.importXML(xml)    
    
</dtml-if>
##code-section FOOT
##/code-section FOOT
