#
# Initialise the product's module. There three ways to inject custom code
# here:
#
#   - To set global configuration variables, create a file AppConfig.py. This
#       will be imported in config.py, which in turns is imported in each
#       generated class and in this file.
#   - To perform custom initialisation after types have been registered, create
#       a file called AppInit.py, with a method initialize(context)
#   - To register a customisation policy, create a file CustomizationPolicy.py
#       with a method register(context) to register the policy
#


print 'Product %(project_name)s installed'


try:
    import CustomizationPolicy
except ImportError:
    CustomizationPolicy=None

from Globals import package_home
from Products.CMFCore import utils, CMFCorePermissions, DirectoryView
from Products.Archetypes.public import *
from Products.Archetypes import listTypes
from Products.Archetypes.utils import capitalize

import os, os.path

from Products.%(project_name)s.config import *

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
        print 'Customization policy for %(project_name)s installed'
        
    try:
        import AppInit
        if hasattr (AppInit, 'initialize'):
            AppInit.initialize (context)
    except ImportError:
        pass
