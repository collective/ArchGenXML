print 'Product %(project_name)s installed'


try:
    import CustomizationPolicy
    print 'Customizationpolicy for %(project_name)s installed'
except ImportError:
    CustomizationPolicy=None

from Globals import package_home
from Products.CMFCore import utils, CMFCorePermissions, DirectoryView
from Products.Archetypes.public import *
from Products.Archetypes import listTypes
from Products.Archetypes.utils import capitalize

import os, os.path


ADD_CONTENT_PERMISSION = %(add_content_permission)s
PROJECTNAME = "%(project_name)s"

product_globals=globals()

DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/%(project_name)s', product_globals)


def initialize(context):
    ##Import Types here to register them
%(imports)s

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    %(toolinit)s

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    %(extra_perms)s

    if CustomizationPolicy and hasattr(CustomizationPolicy,'register'):
        CustomizationPolicy.register(context)
