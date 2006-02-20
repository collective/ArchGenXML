from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews


from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes import listTypes
from Products.%(project_dir)s import PROJECTNAME,product_globals

from StringIO import StringIO

class PloneSkinRegistrar:
    """
    Controls (un)registering of a layer in the skins tool:
     - the layer in the content of the skin tool
     - the layer in the path of all skins
    @author: U{Gilles Lenfant <glenfant@bigfoot.com>}
    @version: 0.1.0
    @ivar _layer: Name of the Product's subdirectory that contains
        the various layers for the Product.
    @type _layer: string
    @ivar _prodglobals: Globals from this Product.
    @type _propglobals: mapping object
    """

    def __init__(self, skinsdir, prodglobals):
        """Constructor
        @param skinsdir: Name of the Product's subdirectory that
            contains the various layers for the Product.
        @type skinsdir: string
        @param prodglobals: Globals from this Product.

            should be provided by Product's C{__init__.py} like this:

            C{product_globals = globals()}

        @type propglobals: mapping object
        @return: None
        """

        self._skinsdir = skinsdir
        self._prodglobals = prodglobals
        return

    def install(self, aq_obj):
        """Installs and registers the skin resources
        @param aq_obj: object from which cmf site object is acquired
        @type aq_obj: any Zope object in the CMF
        @return: Installation log
        @rtype: string
        """

        rpt = '=> Installing and registering layers from directory %%s\n' %% self._skinsdir
        skinstool = getToolByName(aq_obj, 'portal_skins')

        # Create the layer in portal_skins

        if self._skinsdir not in skinstool.objectIds():
            addDirectoryViews(skinstool, self._skinsdir, self._prodglobals)
            rpt += 'Added "%%s" directory view to portal_skins\n' %% self._skinsdir
        else:
            rpt += 'Warning: directory view "%%s" already added to portal_skins\n' %% self._skinsdir

        # Insert the layer in all skins
        # XXX FIXME: Actually assumes only one layer directory with the name of the Product
        # (should be replaced by a smarter solution that finds individual Product's layers)

        layerName = self._prodglobals['__name__'].split('.')[-1]
        skins = skinstool.getSkinSelections()
        for skin in skins:
            layers = skinstool.getSkinPath(skin)
            layers = [layer.strip() for layer in layers.split(',')]
            if layerName not in layers:
                try:
                    layers.insert(layers.index('content'), layerName)
                except ValueError:
                    layers.append(layerName)
                layers = ','.join(layers)
                skinstool.addSkinSelection(skin, layers)
                rpt += 'Added "%%s" to "%%s" skin\n' %% (layerName, skin)
            else:
                rpt += '! Warning: skipping "%%s" skin, "%%s" is already set up\n' %% (skin, type)
        return rpt

    def unInstall(self, aq_obj):
        """Uninstalls and unregisters the skin resources
        @param aq_obj: object from which cmf site object is acquired
        @type aq_obj: any Zope object in the CMF
        @return: Uninstallation log
        @rtype: string
        """

        rpt = '=> Uninstalling and unregistering %%s layer\n' %% self._skinsdir
        skinstool = getToolByName(aq_obj, 'portal_skins')

        # Removing layer from portal_skins
        # XXX FIXME: Actually assumes only one layer directory with the name of the Product
        # (should be replaced by a smarter solution that finds individual Product's layers)

        layerName = self._prodglobals['__name__'].split('.')[-1]
        if layerName in skinstool.objectIds():
            skinstool.manage_delObjects([layerName])
            rpt += 'Removed "%%s" directory view from portal_skins\n' %% layerName
        else:
            rpt += '! Warning: directory view "%%s" already removed from portal_skins\n' %% layerName

        # Removing from skins selection

        skins = skinstool.getSkinSelections()
        for skin in skins:
            layers = skinstool.getSkinPath(skin)
            layers = [layer.strip() for layer in layers.split(',')]
            if layerName in layers:
                layers.remove(layerName)
                layers = ','.join(layers)
                skinstool.addSkinSelection(skin, layers)
                rpt += 'Removed "%%s" to "%%s" skin\n' %% (layerName, skin)
            else:
                rpt += 'Skipping "%%s" skin, "%%s" is already removed\n' %% (skin, layerName)
        return rpt
# /class PloneSkinRegistrar

def install(self):
    out = StringIO()
    installTypes(self, out,
                 listTypes(PROJECTNAME),
                 PROJECTNAME)

    print >> out, "Successfully installed %%s." %% PROJECTNAME
    sr = PloneSkinRegistrar('skins', product_globals)
    print >> out,sr.install(self)
    return out.getvalue()

