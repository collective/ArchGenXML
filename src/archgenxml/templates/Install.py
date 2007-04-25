<dtml-var "generator.generateModuleInfoHeader(package, name='Install')">
import os.path
import sys
from StringIO import StringIO
from sets import Set
from App.Common import package_home
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import manage_addTool
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from zExceptions import NotFound, BadRequest

from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes.Extensions.utils import install_subskin
from Products.Archetypes.config import TOOL_NAME as ARCHETYPETOOLNAME
from Products.Archetypes.atapi import listTypes
<dtml-if "[cn for cn in generator.getGeneratedClasses(package) if cn.hasStereoType(generator.cmfmember_stereotype)]">
from Products.CMFMember.Extensions.toolbox import SetupMember
</dtml-if>
<dtml-if "[klass for klass in generator.getGeneratedClasses(package) if generator.getOption('migrate_dynamic_view_fti', klass, None)]">
try:
    from Products.CMFDynamicViewFTI.migrate import migrateFTIs
except:
    HAS_DYNAMIC_VIEW_FTI = True
else:
    HAS_DYNAMIC_VIEW_FTI = False
</dtml-if>
from Products.<dtml-var "package.getProductModuleName()">.config import PROJECTNAME
from Products.<dtml-var "package.getProductModuleName()">.config import product_globals as GLOBALS


def install(self, reinstall=False):
    """ External Method to install <dtml-var "package.getProductModuleName()"> """
    out = StringIO()
    print >> out, "Installation log of %s:" % PROJECTNAME

    # If the config contains a list of dependencies, try to install
    # them.  Add a list called DEPENDENCIES to your custom
    # AppConfig.py (imported by config.py) to use it.
    try:
        from Products.<dtml-var "package.getProductModuleName()">.config import DEPENDENCIES
    except:
        DEPENDENCIES = []
    portal = getToolByName(self,'portal_url').getPortalObject()
    quickinstaller = portal.portal_quickinstaller
    for dependency in DEPENDENCIES:
        print >> out, "Installing dependency %s:" % dependency
        quickinstaller.installProduct(dependency)
        import transaction
        transaction.savepoint(optimistic=True)

    classes = listTypes(PROJECTNAME)
    installTypes(self, out,
                 classes,
                 PROJECTNAME)
    install_subskin(self, out, GLOBALS)
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
<dtml-if "generator.left_slots or generator.right_slots">
    portal = getToolByName(self,'portal_url').getPortalObject()
</dtml-if>
<dtml-if "generator.left_slots">
    for slot in <dtml-var "repr(generator.left_slots)">:
       if slot not in portal.left_slots:
           portal.left_slots = list(portal.left_slots) + [slot]
</dtml-if>
<dtml-if "generator.right_slots">
    for slot in <dtml-var "repr(generator.right_slots)">:
       if slot not in portal.right_slots:
           portal.right_slots = list(portal.right_slots) + [slot]
</dtml-if>
<dtml-let autoinstall_tools="[c.getName() for c in generator.getGeneratedTools(package) if not utils.isTGVFalse(c.getTaggedValue('autoinstall')) ]">
<dtml-if "autoinstall_tools">
    # autoinstall tools
    portal = getToolByName(self,'portal_url').getPortalObject()
    for t in <dtml-var "repr(autoinstall_tools)">:
        try:
            portal.manage_addProduct[PROJECTNAME].manage_addTool(t)
        except BadRequest:
            # if an instance with the same name already exists this error will
            # be swallowed. Zope raises in an unelegant manner a 'Bad Request' error
            pass
        except:
            e = sys.exc_info()
            if e[0] != 'Bad Request':
                raise

    # hide tools in the search form
    portalProperties = getToolByName(self, 'portal_properties', None)
    if portalProperties is not None:
        siteProperties = getattr(portalProperties, 'site_properties', None)
        if siteProperties is not None and siteProperties.hasProperty('types_not_searched'):
            for tool in <dtml-var "repr(autoinstall_tools)">:
                current = list(siteProperties.getProperty('types_not_searched'))
                if tool not in current:
                    current.append(tool)
                    siteProperties.manage_changeProperties(**{'types_not_searched' : current})

    # remove workflow for tools
    portal_workflow = getToolByName(self, 'portal_workflow')
    for tool in <dtml-var "repr(autoinstall_tools)">:
        portal_workflow.setChainForPortalTypes([tool], '')

</dtml-if>
</dtml-let>
<dtml-let all_tools="[c for c in generator.getGeneratedTools(package)]">
<dtml-if "all_tools">
    # uncatalog tools
    for toolname in <dtml-var "[t.getTaggedValue('tool_instance_name') or 'portal_%s' % t.getName().lower() for t in all_tools]">:
        try:
            portal[toolname].unindexObject()
        except:
            pass

    # hide tools in the navigation
    portalProperties = getToolByName(self, 'portal_properties', None)
    if portalProperties is not None:
        navtreeProperties = getattr(portalProperties, 'navtree_properties', None)
        if navtreeProperties is not None and navtreeProperties.hasProperty('idsNotToList'):
            for toolname in <dtml-var "[t.getTaggedValue('tool_instance_name') or 'portal_%s' % t.getName().lower() for t in all_tools]">:
                current = list(navtreeProperties.getProperty('idsNotToList'))
                if toolname not in current:
                    current.append(toolname)
                    navtreeProperties.manage_changeProperties(**{'idsNotToList' : current})

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
                    package_home(GLOBALS), 'data', '%s.vdex' % vocabname)
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
<dtml-let cmfmembers="[cn for cn in generator.getGeneratedClasses(package) if cn.hasStereoType(generator.cmfmember_stereotype)]">
<dtml-if "cmfmembers">

    # registers as CMFMember and update catalogs, workflow, ...
<dtml-in "cmfmembers">
    print >> out, SetupMember(self, member_type='<dtml-var "_['sequence-item'].getCleanName()">', register=<dtml-var "str(_['sequence-item'].getTaggedValue('register', False))">).finish()
</dtml-in>
</dtml-if>
</dtml-let>
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

    # try to call a workflow install method
    # in 'InstallWorkflows.py' method 'installWorkflows'
    try:
        installWorkflows = ExternalMethod('temp', 'temp',
                                          PROJECTNAME+'.InstallWorkflows',
                                          'installWorkflows').__of__(self)
    except NotFound:
        installWorkflows = None

    if installWorkflows:
        print >>out,'Workflow Install:'
        res = installWorkflows(self,out)
        print >>out,res or 'no output'
    else:
        print >>out,'no workflow install'

<dtml-if "[klass for klass in generator.getGeneratedClasses(package) if generator.getOption('use_workflow', klass, None) is not None and not klass.getStateMachines()]">
    #bind classes to workflows
    wft = getToolByName(self,'portal_workflow')
<dtml-in "generator.getGeneratedClasses(package)">
<dtml-let klass="_['sequence-item']">
<dtml-if "generator.getOption('use_workflow', klass, None)">
    wft.setChainForPortalTypes( ['<dtml-var "klass.getCleanName()">'], <dtml-var "utils.getExpression(generator.getOption('use_workflow', klass))">)
</dtml-if>
</dtml-let>
</dtml-in>
</dtml-if>
<dtml-let all_tools="[c for c in generator.getGeneratedTools(package) if generator.getOption('use_workflow', c, None) is not None or c.getStateMachine()]">
<dtml-if "all_tools">
    # update workflow for created tools if they have been designated a workflow
    for toolname in <dtml-var "[t.getTaggedValue('tool_instance_name') or 'portal_%s' % t.getName().lower() for t in all_tools]">:
        try:
            portal[toolname].notifyWorkflowCreated()
        except:
            pass
</dtml-if>
</dtml-let>
<dtml-if "package.num_generated_relations">
    # configuration for Relations
    relations_tool = getToolByName(self,'relations_library')
    xmlpath = os.path.join(package_home(GLOBALS),'relations.xml')
    f = open(xmlpath)
    xml = f.read()
    f.close()
    relations_tool.importXML(xml)

</dtml-if>
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

    from Products.<dtml-var "package.getProductModuleName()">.config import STYLESHEETS
    try:
        portal_css = getToolByName(portal, 'portal_css')
        for stylesheet in STYLESHEETS:
            try:
                portal_css.unregisterResource(stylesheet['id'])
            except:
                pass
            defaults = {'id': '',
            'media': 'all',
            'enabled': True}
            defaults.update(stylesheet)
            portal_css.registerStylesheet(**defaults)
    except:
        # No portal_css registry
        pass
    from Products.<dtml-var "package.getProductModuleName()">.config import JAVASCRIPTS
    try:
        portal_javascripts = getToolByName(portal, 'portal_javascripts')
        for javascript in JAVASCRIPTS:
            try:
                portal_javascripts.unregisterResource(javascript['id'])
            except:
                pass
            defaults = {'id': ''}
            defaults.update(javascript)
            portal_javascripts.registerScript(**defaults)
    except:
        # No portal_javascripts registry
        pass

    # try to call a custom install method
    # in 'AppInstall.py' method 'install'
    try:
        install = ExternalMethod('temp', 'temp',
                                 PROJECTNAME+'.AppInstall', 'install')
    except NotFound:
        install = None

    if install:
        print >>out,'Custom Install:'
        try:
            res = install(self, reinstall)
        except TypeError:
            res = install(self)
        if res:
            print >>out,res
        else:
            print >>out,'no output'
    else:
        print >>out,'no custom install'
    return out.getvalue()


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
    # try to call a workflow uninstall method
    # in 'InstallWorkflows.py' method 'uninstallWorkflows'
    try:
        uninstallWorkflows = ExternalMethod('temp', 'temp',
                                            PROJECTNAME+'.InstallWorkflows',
                                            'uninstallWorkflows').__of__(self)
    except NotFound:
        uninstallWorkflows = None

    if uninstallWorkflows:
        print >>out, 'Workflow Uninstall:'
        res = uninstallWorkflows(self, out)
        print >>out, res or 'no output'
    else:
        print >>out,'no workflow uninstall'

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
