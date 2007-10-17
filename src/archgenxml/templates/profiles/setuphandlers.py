<dtml-var "generator.generateModuleInfoHeader(package, name='setuphandlers')">
import logging
logger = logging.getLogger('<dtml-var "product_name">: setuphandlers')
from config import PROJECTNAME
from config import DEPENDENCIES
<dtml-if "hasvocabularies or hasrelations">
from config import product_globals
</dtml-if>
<dtml-if "hasvocabularies">
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
</dtml-if>
from Products.CMFCore.utils import getToolByName
##code-section HEAD
##/code-section HEAD

def installGSDependencies(context):
    """Install dependend profiles."""
    
    # XXX Hacky, but works for now. has to be refactored as soon as generic
    # setup allows a more flexible way to handle dependencies.
    
    dependencies = [<dtml-var "', '.join(dependend_profiles)">]
    if not dependencies:
        return
    
    site = context.getSite()
    setup_tool = getToolByName(site, 'portal_setup')
    for dependency in dependencies:
        if dependency.find(':') == -1:
            dependency += ':default'
        old_context = setup_tool.getImportContextID()
        setup_tool.setImportContext('profile-%s' % dependency)
        importsteps = setup_tool.getImportStepRegistry().sortSteps()
        excludes = [
            u'<dtml-var "product_name">-QI-dependencies',
            u'<dtml-var "product_name">-GS-dependencies'
        ]
        importsteps = [s for s in importsteps if s not in excludes]
        for step in importsteps:
            setup_tool.runImportStep(step) # purging flag here?
        setup_tool.setImportContext(old_context)
    
    # re-run some steps to be sure the current profile applies as expected
    importsteps = setup_tool.getImportStepRegistry().sortSteps()
    filter = [
        u'typeinfo',
        u'workflow',
        u'membranetool',
        u'factorytool',
        u'content_type_registry',
        u'membrane-sitemanager'
    ]
    importsteps = [s for s in importsteps if s in filter]
    for step in importsteps:
        setup_tool.runImportStep(step) # purging flag here?
        
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

<dtml-if "notsearchabletypes">
def setupHideTypesFromSearch(context):
    """hide selected classes in the search form"""
    # XXX use https://svn.plone.org/svn/collective/DIYPloneStyle/trunk/profiles/default/properties.xml
    portalProperties = getToolByName(context, 'portal_properties')
    siteProperties = getattr(portalProperties, 'site_properties')
    for klass in <dtml-var "repr(notsearchabletypes)">:
        propertyid = 'types_not_searched'
        lines = list(siteProperties.getProperty(propertyid))
        if klass not in current:
            lines.append(klass)
            siteProperties.manage_changeProperties(**{propertyid: lines})

</dtml-if>
<dtml-if "hidemetatypes">
def setupHideMetaTypesFromNavigations(context):
    """hide selected classes in the search form"""
    # XXX use https://svn.plone.org/svn/collective/DIYPloneStyle/trunk/profiles/default/properties.xml
    portalProperties = getToolByName(context, 'portal_properties')
    siteProperties = getattr(portalProperties, 'site_properties')
    for klass in <dtml-var "repr(hidemetatypes)">:
        propertyid = 'metaTypesNotToList'
        lines = list(siteProperties.getProperty(propertyid))
        if klass not in current:
            lines.append(klass)
            siteProperties.manage_changeProperties(**{propertyid: lines})

</dtml-if>
<dtml-if "toolnames">
def setupHideToolsFromNavigation(context):
    """hide tools"""
    # uncatalog tools
    site = context.getSite()
    toolnames = <dtml-var "repr(toolnames)">
    portalProperties = getToolByName(site, 'portal_properties')    
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
                kwargs = {'idsNotToList': current}
                navtreeProperties.manage_changeProperties(**kwargs)
                
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
                if not getToolByName(context, catalog, False):
                    raise AttributeError, 'Catalog "%s" does not exist!' % catalog
                current_catalogs.update([catalog])
        if 'black' in submap:
            for catalog in submap['black']:
                if catalog in current_catalogs:
                    current_catalogs.remove(catalog)
        atool.setCatalogsByType(meta_type, list(current_catalogs))
        
</dtml-if>
<dtml-if "hasrelations">
def installRelations(context):
    """imports the relations.xml file"""
    site = context.getSite()
    relations_tool = getToolByName(site, 'relations_library')
    xmlpath = os.path.join(package_home(product_globals), 'data', 
                           'relations.xml')
    f = open(xmlpath)
    xml = f.read()
    f.close()
    relations_tool.importXML(xml)    
    
</dtml-if>
<dtml-if "hasvocabularies">
def installVocabularies(context):
    """creates/imports the atvm vocabs."""
    site = context.getSite()
    # Create vocabularies in vocabulary lib
    atvm = getToolByName(site, ATVOCABULARYTOOL)
    vocabmap = {<dtml-var "'),\n        '.join( [s[1:] for s in repr(generator.vocabularymap[package.getProductName()]).split(')')] )">}
    for vocabname in vocabmap.keys():
        if not vocabname in atvm.contentIds():
            atvm.invokeFactory(vocabmap[vocabname][0], vocabname)

        if len(atvm[vocabname].contentIds()) < 1:
            if vocabmap[vocabname][0] == "VdexVocabulary":
                vdexpath = os.path.join(
                    package_home(product_globals), 'data', '%s.vdex' % vocabname)
                if not (os.path.exists(vdexpath) and os.path.isfile(vdexpath)):
                    logger.warn('No VDEX import file provided at %s.' % vdexpath)
                    continue
                try:
                    #read data
                    f = open(vdexpath, 'r')
                    data = f.read()
                    f.close()
                except:
                    logger.warn("Problems while reading VDEX import file "+\
                                "provided at %s." % vdexpath)
                    continue
                # this might take some time!
                atvm[vocabname].importXMLBinding(data)
            else:
                pass
            
</dtml-if>
##code-section FOOT
##/code-section FOOT
