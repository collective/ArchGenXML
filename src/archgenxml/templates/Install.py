<dtml-var "generator.generateModuleInfoHeader(package, name='Install')">
import os.path
import sys
from sets import Set
from StringIO import StringIO
from App.Common import package_home
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import manage_addTool
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from zExceptions import NotFound, BadRequest
<dtml-if "not generator._useGSSkinRegistration(package)">    
from Products.Archetypes.Extensions.utils import install_subskin
</dtml-if>
from Products.Archetypes.config import TOOL_NAME as ARCHETYPETOOLNAME
<dtml-if "not generator._useGSTypeRegistration(package)">
from Products.Archetypes.atapi import listTypes
from Products.Archetypes.Extensions.utils import installTypes
<dtml-if "[klass for klass in generator.getGeneratedClasses(package) if generator.getOption('migrate_dynamic_view_fti', klass, None)]">
try:
    from Products.CMFDynamicViewFTI.migrate import migrateFTIs
except:
    HAS_DYNAMIC_VIEW_FTI = True
else:
    HAS_DYNAMIC_VIEW_FTI = False
</dtml-if>
</dtml-if>
from Products.<dtml-var "package.getProductModuleName()">.config import PROJECTNAME
from Products.<dtml-var "package.getProductModuleName()">.config import product_globals


def install(self, reinstall=False):
    """ External Method to install <dtml-var "package.getProductModuleName()"> """
    out = StringIO()
    print >> out, "Installation log of %s:" % PROJECTNAME
    
    # DEPENDENCIES are installed using an import step (GenericSetup)
    # so this is no longer in here
    
<dtml-if "not generator._useGSSkinRegistration(package)">    
    install_subskin(self, out, product_globals)
    
</dtml-if>
<dtml-if "not generator._useGSTypeRegistration(package)">
    classes = listTypes(PROJECTNAME)
    installTypes(self, out, classes, PROJECTNAME)
    
<dtml-if "[klass for klass in generator.getGeneratedClasses(package) if generator.getOption('migrate_dynamic_view_fti', klass, None)]">
    # Migrate FTI, to make sure we get the necessary infrastructure for the
    # "display" menu to work.
    if HAS_DYNAMIC_VIEW_FTI:
<dtml-in "[klass for klass in generator.getGeneratedClasses(package) if generator.getOption('migrate_dynamic_view_fti', klass, None)]">
<dtml-let klass="_['sequence-item']">
        migrated = migrateFTIs(self, product=PROJECTNAME, fti_meta_type='<dtml-var "klass.getCleanName()">')
        print >>out, "Switched to DynamicViewFTI: %s" % ', '.join(migrated)
</dtml-let>
</dtml-in>
</dtml-if>
</dtml-if>
<dtml-let klasses="[klass for klass in generator.getGeneratedClasses(package) if generator.getOption('catalogmultiplex:white', klass, None) or generator.getOption('catalogmultiplex:black', klass, None)]">
<dtml-if "klasses">

    # Configure CatalogMultiplex:
    # explicit add classes (meta_types) be indexed in catalogs (white)
    # or removed from indexing in a catalog (black)
    atool = getToolByName(self, ARCHETYPETOOLNAME)
    catalogmap = {}
<dtml-in "klasses">
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
</dtml-let>


<dtml-let configlet_tools="[cn for cn in generator.getGeneratedTools(package) if not utils.isTGVFalse(cn.getTaggedValue('autoinstall')) and cn.getTaggedValue('configlet', None)]">
<dtml-if "configlet_tools">
    # register tools as configlets
    portal_controlpanel = getToolByName(self,'portal_controlpanel')
<dtml-in "configlet_tools">
<dtml-let c="_['sequence-item']">
<dtml-let tool_instance_name="c.getTaggedValue('tool_instance_name', 'portal_'+ c.getName().lower() )"
    configlet_view="'/'+c.getTaggedValue('configlet:view', 'view')">
    portal_controlpanel.unregisterConfiglet('<dtml-var "c.getName()">')
    portal_controlpanel.registerConfiglet(
        '<dtml-var "c.getName()">', #id of your Tool
        '<dtml-var "c.getTaggedValue('configlet:title',c.getName())">', # Title of your Product
        'string:${portal_url}/<dtml-var "tool_instance_name"><dtml-var "configlet_view">',
        '<dtml-var "c.getTaggedValue('configlet:condition', 'python:True')">', # a condition
        '<dtml-var "c.getTaggedValue('configlet:permission', 'Manage portal')">', # access permission
        '<dtml-var "c.getTaggedValue('configlet:section', 'Products')">', # section to which the configlet should be added: (Plone, Products (default) or Member)
        1, # visibility
        '<dtml-var "c.getName()">ID',
        '<dtml-var "c.getTaggedValue('configlet:icon', 'site_icon.gif')">', # icon in control_panel
        '<dtml-var "c.getTaggedValue('configlet:description', 'Configuration for tool %s.' % c.getName())">',
        None,
    )

</dtml-let>
</dtml-let>
</dtml-in>
</dtml-if>
</dtml-let>
<dtml-if "package.getProductName() in generator.vocabularymap.keys()">

    # Create vocabularies in vocabulary lib
    from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
    atvm = getToolByName(self, ATVOCABULARYTOOL)
    vocabmap = {<dtml-var "'),\n        '.join( [s[1:] for s in repr(generator.vocabularymap[package.getProductName()]).split(')')] )">}
    for vocabname in vocabmap.keys():
        if not vocabname in atvm.contentIds():
            atvm.invokeFactory(vocabmap[vocabname][0], vocabname)

        if len(atvm[vocabname].contentIds()) < 1:
            if vocabmap[vocabname][0] == "VdexVocabulary":
                vdexpath = os.path.join(
                    package_home(product_globals), 'data', '%s.vdex' % vocabname)
                if not (os.path.exists(vdexpath) and os.path.isfile(vdexpath)):
                    print >>out, 'No VDEX import file provided at %s.' % vdexpath
                    continue
                try:
                    #read data
                    f = open(vdexpath, 'r')
                    data = f.read()
                    f.close()
                except:
                    print >>out, 'Problems while reading VDEX import file provided at %s.' % vdexpath
                    continue
                atvm[vocabname].importXMLBinding(data)
            else:
                pass
</dtml-if>

<dtml-let remembers="[cn for cn in generator.getGeneratedClasses(package) if cn.hasStereoType(generator.remember_stereotype)]">
<dtml-if "remembers"> 
    # Adds our types to MemberDataContainer.allowed_content_types
    types_tool = getToolByName(self, 'portal_types')
    act = types_tool.MemberDataContainer.allowed_content_types
    types_tool.MemberDataContainer.manage_changeProperties(allowed_content_types=act+(<dtml-in remembers>'<dtml-var "_['sequence-item'].getCleanName()">', </dtml-in>))
    # registers with membrane tool ...
    membrane_tool = getToolByName(self, 'membrane_tool')
<dtml-in "remembers">
    membrane_tool.registerMembraneType('<dtml-var "_['sequence-item'].getCleanName()">')
    # print >> out, SetupMember(self, member_type='<dtml-var "_['sequence-item'].getCleanName()">', register=<dtml-var "str(_['sequence-item'].getTaggedValue('register', False))">).finish()
</dtml-in>
</dtml-if>
</dtml-let>

<dtml-if "package.num_generated_relations">
    # configuration for Relations
    relations_tool = getToolByName(self,'relations_library')
    xmlpath = os.path.join(package_home(product_globals),'relations.xml')
    f = open(xmlpath)
    xml = f.read()
    f.close()
    relations_tool.importXML(xml)

</dtml-if>

<dtml-if "not generator._useGSTypeRegistration(package)">
<dtml-let klasses="[klass for klass in generator.getGeneratedClasses(package) if utils.isTGVTrue(generator.getOption('use_portal_factory', klass, True)) and not (klass.getPackage().hasStereoType('tests') or klass.isAbstract() or klass.hasStereoType(['widget', 'field', 'stub']))]">
<dtml-if "klasses">
    # enable portal_factory for given types
    factory_tool = getToolByName(self,'portal_factory')
    factory_types=[
        <dtml-in "klasses"><dtml-let
                 klass="_['sequence-item']">"<dtml-var
                       "klass.getTaggedValue('portal_type') or klass.getCleanName()">",
        </dtml-let>
</dtml-in>] + factory_tool.getFactoryTypes().keys()
    factory_tool.manage_setPortalFactoryTypes(listOfTypeIds=factory_types)
</dtml-if>
</dtml-let>
</dtml-if>
<dtml-let klasses="[(klass.getTaggedValue('portal_type') or klass.getCleanName()) for klass in generator.getGeneratedClasses(package) if utils.isTGVFalse(generator.getOption('searchable_type', klass, True))]">
<dtml-if "klasses">
    # hide selected classes in the search form
    portalProperties = getToolByName(self, 'portal_properties', None)
    if portalProperties is not None:
        siteProperties = getattr(portalProperties, 'site_properties', None)
        if siteProperties is not None and siteProperties.hasProperty('types_not_searched'):
            for klass in <dtml-var "repr(klasses)">:
                current = list(siteProperties.getProperty('types_not_searched'))
                if klass not in current:
                    current.append(klass)
                    siteProperties.manage_changeProperties(**{'types_not_searched' : current})
</dtml-if>
</dtml-let>
<dtml-let klasses="[(klass.getTaggedValue('portal_type') or klass.getCleanName()) for klass in generator.getGeneratedClasses(package) if utils.isTGVFalse(generator.getOption('display_in_navigation', klass, True))]">
<dtml-if "klasses">
    # hide selected classes in the navigation
    portalProperties = getToolByName(self, 'portal_properties', None)
    if portalProperties is not None:
        navtree_properties = getattr(portalProperties, 'navtree_properties', None)
        if navtree_properties is not None and navtree_properties.hasProperty('metaTypesNotToList'):
            for klass in <dtml-var "repr(klasses)">:
                current = list(navtree_properties.getProperty('metaTypesNotToList'))
                if klass not in current:
                    current.append(klass)
                    navtree_properties.manage_changeProperties(**{'metaTypesNotToList' : current})
</dtml-if>
</dtml-let>

    return out.getvalue()

<dtml-comment>
def uninstall(self, reinstall=False):
    out = StringIO()
<dtml-let remembers="[cn for cn in generator.getGeneratedClasses(package) if cn.hasStereoType(generator.remember_stereotype)]">
<dtml-if "remembers">
    # Removes our types from MemberDataContainer.allowed_content_types
    types_tool = getToolByName(self, 'portal_types')
    act = types_tool.MemberDataContainer.allowed_content_types
    types_tool.MemberDataContainer.manage_changeProperties(allowed_content_types=[ct for ct in act if ct not in (<dtml-in remembers>'<dtml-var "_['sequence-item'].getCleanName()">', </dtml-in>) ])
    # unregister with membrane tool ...
    membrane_tool = getToolByName(self, 'membrane_tool')
<dtml-in "remembers">
    membrane_tool.unregisterMembraneType('<dtml-var "_['sequence-item'].getCleanName()">')
    # print >> out, SetupMember(self, member_type='<dtml-var "_['sequence-item'].getCleanName()">', register=<dtml-var "str(_['sequence-item'].getTaggedValue('register', False))">).finish()
</dtml-in>
</dtml-if>
</dtml-let>
<dtml-let autoinstalled_tools="[c.getName() for c in generator.getGeneratedTools(package) if not utils.isTGVFalse(c.getTaggedValue('autoinstall')) ]">
<dtml-if "autoinstalled_tools">
    # unhide tools in the search form
    portalProperties = getToolByName(self, 'portal_properties', None)
    if portalProperties is not None:
        siteProperties = getattr(portalProperties, 'site_properties', None)
        if siteProperties is not None and siteProperties.hasProperty('types_not_searched'):
            for tool in <dtml-var "repr(autoinstalled_tools)">:
                current = list(siteProperties.getProperty('types_not_searched'))
                if tool in current:
                    current.remove(tool)
                    siteProperties.manage_changeProperties(**{'types_not_searched' : current})

</dtml-if>
</dtml-let>
<dtml-let klasses="[(klass.getTaggedValue('portal_type') or klass.getCleanName()) for klass in generator.getGeneratedClasses(package) if utils.isTGVFalse(generator.getOption('searchable_type', klass, True))]">
<dtml-if "klasses">
    # unhide types in the search form
    portalProperties = getToolByName(self, 'portal_properties', None)
    if portalProperties is not None:
        siteProperties = getattr(portalProperties, 'site_properties', None)
        if siteProperties is not None and siteProperties.hasProperty('types_not_searched'):
            for klass in <dtml-var "repr(klasses)">:
                current = list(siteProperties.getProperty('types_not_searched'))
                if klass in current:
                    current.remove(klass)
                    siteProperties.manage_changeProperties(**{'types_not_searched' : current})

</dtml-if>
</dtml-let>
<dtml-let klasses="[(klass.getTaggedValue('portal_type') or klass.getCleanName()) for klass in generator.getGeneratedClasses(package) if utils.isTGVFalse(generator.getOption('display_in_navigation', klass, True))]">
<dtml-if "klasses">
    # unhide selected classes in the navigation
    portalProperties = getToolByName(self, 'portal_properties', None)
    if portalProperties is not None:
        navtree_properties = getattr(portalProperties, 'navtree_properties', None)
        if navtree_properties is not None and navtree_properties.hasProperty('metaTypesNotToList'):
            for klass in <dtml-var "repr(klasses)">:
                current = list(navtree_properties.getProperty('metaTypesNotToList'))
                if klass in current:
                    current.remove(klass)
                    navtree_properties.manage_changeProperties(**{'metaTypesNotToList' : current})

</dtml-if>
</dtml-let>
<dtml-let all_tools="[c for c in generator.getGeneratedTools(package)]">
<dtml-if "all_tools">
    # unhide tools
    portalProperties = getToolByName(self, 'portal_properties', None)
    if portalProperties is not None:
        navtreeProperties = getattr(portalProperties, 'navtree_properties', None)
        if navtreeProperties is not None and navtreeProperties.hasProperty('idsNotToList'):
            for toolname in <dtml-var "[t.getTaggedValue('tool_instance_name') or 'portal_%s' % t.getName().lower() for t in all_tools]">:
                current = list(navtreeProperties.getProperty('idsNotToList'))
                if toolname in current:
                    current.remove(toolname)
                    navtreeProperties.manage_changeProperties(**{'idsNotToList' : current})

</dtml-if>
</dtml-let>
<dtml-let configlet_tools="[cn for cn in generator.getGeneratedClasses(package) if cn.hasStereoType(generator.portal_tools) and utils.isTGVTrue(cn.getTaggedValue('autoinstall','0') ) and cn.getTaggedValue('configlet', None)]">
<dtml-if "configlet_tools">

    # unregister tools as configlets
    portal_control_panel = getToolByName(self,'portal_controlpanel', None)
    if portal_control_panel is not None:
<dtml-in "configlet_tools">
        portal_control_panel.unregisterConfiglet('<dtml-var "_['sequence-item'].getName()">')
</dtml-in>
</dtml-if>
</dtml-let>
    # try to call a custom uninstall method
    # in 'AppInstall.py' method 'uninstall'
    try:
        uninstall = ExternalMethod('temp', 'temp',
                                   PROJECTNAME+'.AppInstall', 'uninstall')
    except:
        uninstall = None
    if uninstall:
        print >>out,'Custom Uninstall:'
        try:
            res = uninstall(self, reinstall)
        except TypeError:
            res = uninstall(self)
        if res:
            print >>out,res
        else:
            print >>out,'no output'
    else:
        print >>out,'no custom uninstall'
    return out.getvalue()


def beforeUninstall(self, reinstall, product, cascade):
    """ try to call a custom beforeUninstall method in 'AppInstall.py'
        method 'beforeUninstall'
    """
    out = StringIO()
    try:
        beforeuninstall = ExternalMethod(
            'temp', 'temp',
            PROJECTNAME+'.AppInstall', 'beforeUninstall')
    except:
        beforeuninstall = []

    if beforeuninstall:
        print >>out, 'Custom beforeUninstall:'
        res = beforeuninstall(self,
                              reinstall=reinstall,
                              product=product,
                              cascade=cascade)
        if res:
            print >>out, res
        else:
            print >>out, 'no output'
    else:
        print >>out, 'no custom beforeUninstall'
    return (out,cascade)


def afterInstall(self, reinstall, product):
    """ try to call a custom afterInstall method in 'AppInstall.py' method
        'afterInstall'
    """
    out = StringIO()
    try:
        afterinstall = ExternalMethod('temp', 'temp',
                                   PROJECTNAME+'.AppInstall', 'afterInstall')
    except:
        afterinstall = None

    if afterinstall:
        print >>out, 'Custom afterInstall:'
        res = afterinstall(self,
                           product=None,
                           reinstall=None)
        if res:
            print >>out, res
        else:
            print >>out, 'no output'
    else:
        print >>out, 'no custom afterInstall'
    return out
</dtml-comment>
