from Products.CMFCore.utils import getToolByName,manage_addTool
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.ExternalMethod.ExternalMethod import ExternalMethod


from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.Archetypes import listTypes
from Products.%(project_dir)s import PROJECTNAME,product_globals

from zExceptions import NotFound

from StringIO import StringIO
import sys

def install(self):
    portal=getToolByName(self,'portal_url').getPortalObject()
    out = StringIO()
    classes=listTypes(PROJECTNAME)
    installTypes(self, out,
                 classes,
                 PROJECTNAME)

    print >> out, "Successfully installed %%s." %% PROJECTNAME
    sr = PloneSkinRegistrar('skins', product_globals)
    print >> out,sr.install(self)
    #sr = PloneSkinRegistrar('skins', product_globals)
    print >> out,sr.install(self,position='custom',mode='after',layerName=PROJECTNAME+'_public')

    #register folderish classes in use_folder_contents
    props=getToolByName(self,'portal_properties').site_properties
    use_folder_tabs=list(props.use_folder_tabs)
    print >> out, 'adding classes to use_folder_tabs:'
    for cl in classes:
        print >> out,  'type:',cl['klass'].portal_type
        if cl['klass'].isPrincipiaFolderish and not cl['klass'].portal_type in %(no_use_of_folder_tabs)s:
            use_folder_tabs.append(cl['klass'].portal_type)

    props.use_folder_tabs=tuple(use_folder_tabs)

    #autoinstall tools
    for t in %(autoinstall_tools)s:
        try:
            portal.manage_addProduct[PROJECTNAME].manage_addTool(t)
            # tools are not content. dont list it in navtree
        except:
            #heuristics for testing if an instance with the same name already exists
            #only this error will be swallowed.
            #Zope raises in an unelegant manner a 'Bad Request' error
            e=sys.exc_info()
            if e[0] != 'Bad Request':
                raise

    #hide tools in the navigation
    for t in %(all_tools)s:
        try:
            if t not in self.portal_properties.navtree_properties.metaTypesNotToList:
                self.portal_properties.navtree_properties.metaTypesNotToList= \
                   list(self.portal_properties.navtree_properties.metaTypesNotToList) + \
                      [t]
        except TypeError, e:
            print 'Attention: could not set the navtree properties:',e

    # register tool in control panel
    try:
        portal_control_panel=getToolByName(self,'portal_control_panel_actions')
    except AttributeError:
        #portal_control_panel has been renamed in RC1 (grumpf)
        portal_control_panel=getToolByName(self,'portal_controlpanel',None)

    %(register_configlets)s

    portal.left_slots=list(portal.left_slots)+%(left_slots)s
    portal.right_slots=list(portal.right_slots)+%(right_slots)s

    #try to call a custom install method
    #in 'AppInstall.py' method 'install'
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

    #try to call a workflow install method
    #in 'InstallWorkflows.py' method 'installWorkflows'
    try:
        installWorkflows = ExternalMethod('temp','temp',PROJECTNAME+'.InstallWorkflows', 'installWorkflows').__of__(self)
    except NotFound:
        installWorkflows=None

    if installWorkflows:
        print >>out,'Workflow Install:'
        res=installWorkflows(self,out)
        if res:
            print >>out,res
        else:
            print >>out,'no output'
    else:
        print >>out,'no workflow install'

    return out.getvalue()

def uninstall(self):
    out = StringIO()
    classes=listTypes(PROJECTNAME)

    #unregister folderish classes in use_folder_contents
    props=getToolByName(self,'portal_properties').site_properties
    use_folder_tabs=list(props.use_folder_tabs)
    print >> out, 'removing classes from use_folder_tabs:'
    for cl in classes:
        print >> out,  'type:', cl['klass'].portal_type
        if cl['klass'].isPrincipiaFolderish and not cl['klass'].portal_type in %(no_use_of_folder_tabs)s:
            if cl['klass'].portal_type in use_folder_tabs:
                use_folder_tabs.remove(cl['klass'].portal_type)

    props.use_folder_tabs=tuple(use_folder_tabs)

    #autouninstall tools
    for t in %(autoinstall_tools)s:
        # undo: tools are not content. dont list it in navtree
        try:
            self.portal_properties.navtree_properties.metaTypesNotToList=list(self.portal_properties.navtree_properties.metaTypesNotToList)
            self.portal_properties.navtree_properties.metaTypesNotToList.remove(t)
        except ValueError:
            pass
        except:
            raise
    # unregister tool in control panel
    try:
        portal_control_panel=getToolByName(self,'portal_control_panel_actions')
    except AttributeError:
        #portal_control_panel has been renamed in RC1 (grumpf)
        portal_control_panel=getToolByName(self, 'portal_controlpanel', None)
    %(unregister_configlets)s



    #try to call a custom uninstall method
    #in 'AppInstall.py' method 'uninstall'
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
