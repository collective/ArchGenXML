<dtml-let infoheader="generator.getHeaderInfo(package)">
""" Extensions/Install.py """

# <dtml-var "infoheader['copyright']">
#
# Generated: <dtml-var "infoheader['date']">
# Generator: ArchGenXML Version <dtml-var "infoheader['version']">
#            http://sf.net/projects/archetypes/
#
# <dtml-var "infoheader['licence']">
#
__author__    = '''<dtml-var "infoheader['authorline']">'''
__docformat__ = 'plaintext'
__version__   = '$ Revision 0.0 $'[11:-2]
</dtml-let>
from Products.CMFCore.utils import manage_addTool
from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod.ExternalMethod import ExternalMethod

from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes.Extensions.utils import install_subskin
try:
    from Products.Archetypes.lib.register import listTypes
except ImportError:
    from Products.Archetypes.public import listTypes

<dtml-if "[cn for cn in generator.getGeneratedClasses(package) if cn.hasStereoType(generator.cmfmember_stereotype)]">
from Products.CMFMember.Extensions.toolbox import SetupMember
</dtml-if>
from Products.<dtml-var "package.getProductModuleName()"> import PROJECTNAME
from Products.<dtml-var "package.getProductModuleName()"> import product_globals as GLOBALS

from zExceptions import NotFound, BadRequest

from StringIO import StringIO
import sys

def install(self):
    """ External Method to install <dtml-var "package.getProductModuleName()"> """
    out = StringIO()
    #install_dependencies(self, out)

    print >> out, "Installation log of %s:" % PROJECTNAME

    classes=listTypes(PROJECTNAME)
    installTypes(self, out,
                 classes,
                 PROJECTNAME)
    install_subskin(self,out,GLOBALS)

<dtml-let hide_folder_tabs="[cn.getName() for cn in generator.getGeneratedClasses(package) if cn.getTaggedValue('hide_folder_tabs', False)]">
<dtml-if "hide_folder_tabs">
    #register folderish classes in use_folder_contents
    props=getToolByName(self,'portal_properties').site_properties
    use_folder_tabs=list(props.use_folder_tabs)
    print >> out, 'adding %d classes to use_folder_tabs:' % len(classes)
    for cl in classes:
        if cl['klass'].isPrincipiaFolderish and \
            not cl['klass'].portal_type in <dtml-var "repr(hide_folder_tabs)">:
            print >> out, 'portal type:',cl['klass'].portal_type
            use_folder_tabs.append(cl['klass'].portal_type)

    props.use_folder_tabs=tuple(use_folder_tabs)
</dtml-if>
</dtml-let>
<dtml-if "generator.left_slots or generator.right_slots">

    portal=getToolByName(self,'portal_url').getPortalObject()
</dtml-if>
<dtml-if "generator.left_slots">
    portal.left_slots=list(portal.left_slots)+<dtml-var "repr(generator.left_slots)">
</dtml-if>
<dtml-if "generator.right_slots">
    portal.right_slots=list(portal.right_slots)+<dtml-var "repr(generator.right_slots)">
</dtml-if>
<dtml-let autoinstall_tools="[c.getName() for c in generator.getGeneratedTools(package) if utils.isTGVTrue(c.getTaggedValue('autoinstall')) ]">
<dtml-if "autoinstall_tools">
    #autoinstall tools
    portal=getToolByName(self,'portal_url').getPortalObject()
    for t in <dtml-var "repr(autoinstall_tools)">:
        try:
            portal.manage_addProduct[PROJECTNAME].manage_addTool(t)
        except BadRequest:
            pass
        except:
            # if an instance with the same name already exists this error will
            # be swallowed. Zope raises in an unelegant manner a 'Bad Request' error
            e=sys.exc_info()
            if e[0] != 'Bad Request':
                raise
</dtml-if>
</dtml-let>
<dtml-let all_tools="[c.getName() for c in generator.getGeneratedTools(package)]">
<dtml-if "all_tools">

    #hide tools in the navigation
    for t in <dtml-var "repr(all_tools)">:
        try:
            if t not in self.portal_properties.navtree_properties.metaTypesNotToList:
                self.portal_properties.navtree_properties.metaTypesNotToList= \
                   list(self.portal_properties.navtree_properties.metaTypesNotToList) + \
                      [t]
        except TypeError, e:
            print 'Attention: could not set the navtree properties:',e

</dtml-if>
</dtml-let>
<dtml-let configlet_tools="[cn for cn in generator.getGeneratedTools(package) if utils.isTGVTrue(cn.getTaggedValue('autoinstall','0') ) and cn.getTaggedValue('configlet', None)]">
<dtml-if "configlet_tools">
    # register tools as configlets
    portal_controlpanel=getToolByName(self,'portal_controlpanel')
<dtml-in "configlet_tools">
<dtml-let c="_['sequence-item']">
<dtml-let tool_instance_name="c.getTaggedValue('tool_instance_name', 'portal_'+ c.getName().lower() )"
    configlet_view="'/'+c.getTaggedValue('configlet:view')">
    portal_controlpanel.registerConfiglet(
        '<dtml-var "c.getName()">', #id of your Tool
        '<dtml-var "c.getTaggedValue('configlet:title',c.getName())">', # Title of your Troduct
        'string:${portal_url}/<dtml-var "tool_instance_name"><dtml-var "configlet_view">/',
        '<dtml-var "c.getTaggedValue('configlet:condition','python:True')">', # a condition
        '<dtml-var "c.getTaggedValue('configlet:permission','Manage Portal')">', # access permission
        '<dtml-var "c.getTaggedValue('configlet:section','Products')">', # section to which the configlet should be added: (Plone,Products,Members)
        1, # visibility
        '<dtml-var "c.getName()">ID',
        '<dtml-var "c.getTaggedValue('configlet:icon','site_icon.gif')">', # icon in control_panel
        '<dtml-var "c.getTaggedValue('configlet:description','Configuration for tool %s.' % c.getName())">',
        None,
    )
    # set title of tool:
    tool=getToolByName(self, '<dtml-var "tool_instance_name">')
    tool.title='<dtml-var "c.getTaggedValue('configlet:title',c.getName())">'
</dtml-let>
</dtml-let>
</dtml-in>
</dtml-if>
</dtml-let>
<dtml-if "package.getProductName() in generator.vocabularymap.keys()">

    # Create vocabularies in vocabulary lib
    #atvm = getToolByName(self, 'portal_vocabularies')
    #for vocab in <dtml-var "repr([])">:
    #    pass
</dtml-if>
<dtml-let cmfmembers="[cn for cn in generator.getGeneratedClasses(package) if cn.hasStereoType(generator.cmfmember_stereotype)]">
<dtml-if "cmfmembers">

    # registers as CMFMember and update catalogs, workflow, ...
<dtml-in "cmfmembers">
    print >> out, SetupMember(self, member_type='<dtml-var "_['sequence-item'].getCleanName()">').finish()
</dtml-in>
</dtml-if>
</dtml-let>

    # try to call a workflow install method
    # in 'InstallWorkflows.py' method 'installWorkflows'
    try:
        installWorkflows = ExternalMethod('temp','temp',PROJECTNAME+'.InstallWorkflows', 'installWorkflows').__of__(self)
    except NotFound:
        installWorkflows=None

    if installWorkflows:
        print >>out,'Workflow Install:'
        res=installWorkflows(self,out)
        print >>out,res or 'no output'
    else:
        print >>out,'no workflow install'

    <dtml-if "[klass for klass in package.getClasses(recursive=1) if klass.getTaggedValue('use_workflow')]">
    
    #bind classes to workflows
    wft=getToolByName(self,'portal_workflow')
    <dtml-in "package.getClasses(recursive=1)">
    <dtml-let klass="_['sequence-item']">
    <dtml-if "klass.getTaggedValue('use_workflow')">

    wft.setChainForPortalTypes( ['<dtml-var "klass.getCleanName()">'],'<dtml-var "klass.getTaggedValue('use_workflow')">')
    </dtml-if>
    </dtml-let>
    </dtml-in>
    </dtml-if>


    # try to call a custom install method
    # in 'AppInstall.py' method 'install'
    try:
        install = ExternalMethod('temp','temp',PROJECTNAME+'.AppInstall', 'install')
    except:
        install=None

    if install:
        print >>out,'Custom Install:'
        res=install(self)
        if res:
            print >>out,res
        else:
            print >>out,'no output'
    else:
        print >>out,'no custom install'

    return out.getvalue()

def uninstall(self):
    out = StringIO()

<dtml-let hide_folder_tabs="[cn.getName() for cn in generator.getGeneratedClasses(package) if cn.getTaggedValue('hide_folder_tabs', False)]">
<dtml-if "hide_folder_tabs">
    # unregister folderish classes in use_folder_contents
    classes=listTypes(PROJECTNAME)
    props=getToolByName(self,'portal_properties').site_properties
    use_folder_tabs=list(props.use_folder_tabs)
    print >> out, 'removing %d classes from use_folder_tabs:' % len(classes)
    for cl in classes:
        if cl['klass'].isPrincipiaFolderish and \
            not cl['klass'].portal_type in <dtml-var "repr(hide_folder_tabs)">:
            print >> out, 'portal type:',cl['klass'].portal_type
            use_folder_tabs.remove(cl['klass'].portal_type)

    props.use_folder_tabs=tuple(use_folder_tabs)
</dtml-if>
</dtml-let>
<dtml-let autoinstall_tools="[c.getName() for c in generator.getGeneratedClasses(package) if c.hasStereoType(generator.portal_tools) and utils.isTGVTrue(c.getTaggedValue('autoinstall')) ]">
<dtml-if "autoinstall_tools">

    # uninstall tools
    portal=getToolByName(self,'portal_url').getPortalObject()
    for t in <dtml-var "repr(autoinstall_tools)">:
        # undo: tools are not content. dont list it in navtree
        try:
            self.portal_properties.navtree_properties.metaTypesNotToList=list(self.portal_properties.navtree_properties.metaTypesNotToList)
            self.portal_properties.navtree_properties.metaTypesNotToList.remove(t)
        except ValueError:
            pass
        except:
            raise
</dtml-if>
</dtml-let>
<dtml-let configlet_tools="[cn for cn in generator.getGeneratedClasses(package) if cn.hasStereoType(generator.portal_tools) and utils.isTGVTrue(cn.getTaggedValue('autoinstall','0') ) and cn.getTaggedValue('configlet', None)]">
<dtml-if "configlet_tools">

    # unregister tools as configlets
    portal_control_panel=getToolByName(self,'portal_controlpanel')
<dtml-in "configlet_tools">
    portal_control_panel.unregisterConfiglet('<dtml-var "_['sequence-item'].getName()">')
</dtml-in>
</dtml-if>
</dtml-let>

    # try to call a workflow uninstall method
    # in 'InstallWorkflows.py' method 'installWorkflows'
    try:
        installWorkflows = ExternalMethod('temp','temp',PROJECTNAME+'.InstallWorkflows', 'uninstallWorkflows').__of__(self)
    except NotFound:
        installWorkflows=None

    if installWorkflows:
        print >>out,'Workflow Uninstall:'
        res=uninstallWorkflows(self,out)
        print >>out,res or 'no output'
    else:
        print >>out,'no workflow uninstall'

    # try to call a custom uninstall method
    # in 'AppInstall.py' method 'uninstall'
    try:
        uninstall = ExternalMethod('temp','temp',PROJECTNAME+'.AppInstall', 'uninstall')
    except:
        uninstall=None

    if uninstall:
        print >>out,'Custom Uninstall:'
        res=uninstall(self)
        if res:
            print >>out,res
        else:
            print >>out,'no output'
    else:
        print >>out,'no custom uninstall'

    return out.getvalue()
