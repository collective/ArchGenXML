#
# Initialise the product's module. There are three ways to inject custom code
# here:
#
#   - To set global configuration variables, create a file AppConfig.py. This
#       will be imported in config.py, which in turn is imported in each
#       generated class and in this file.
#   - To perform custom initialisation after types have been registered, use
#       the protected code section at the bottom of initialize().
#   - To register a customisation policy, create a file CustomizationPolicy.py
#       with a method register(context) to register the policy
#


print 'Product <dtml-var "product_name"> installed'

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

from Products.<dtml-var "product_name">.config import *

DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/<dtml-var "product_name">', 
                                    product_globals)


def initialize(context):
    ##Import Types here to register them

<dtml-in "package_imports">
    import <dtml-var sequence-item>
</dtml-in>

<dtml-in "class_imports">
    import <dtml-var sequence-item>
</dtml-in>

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

<dtml-if "has_tools">
    tools = [<dtml-var "','.join (tool_names)">]
    utils.ToolInit( PROJECTNAME +' Tools',
                tools = tools,
                product_name = PROJECTNAME,
                icon='tool.gif'
                ).initialize( context )
</dtml-if>

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

<dtml-if "detailed_creation_permissions">
    # Generate separate permissions for adding each content type
    for i in range(0,len(content_types)):
        perm='Add ' + capitalize(ftis[i]['id'])+'s'
        methname='add' + capitalize(ftis[i]['id'])
        meta_type = ftis[i]['meta_type']

        context.registerClass(
            meta_type = meta_type,
            constructors = (
                getattr(locals()[meta_type],'add' + capitalize(meta_type)),
                               )
            , permission = perm
            )
</dtml-if>

    if CustomizationPolicy and hasattr(CustomizationPolicy, 'register'):
        CustomizationPolicy.register(context)
        print 'Customization policy for <dtml-var "product_name"> installed'
        
<dtml-var "protected_init_section">
