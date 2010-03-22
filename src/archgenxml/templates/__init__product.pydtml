<dtml-var "generator.generateModuleInfoHeader(package, all=1)">
# There are three ways to inject custom code here:
#
#   - To set global configuration variables, create a file AppConfig.py.
#       This will be imported in config.py, which in turn is imported in
#       each generated class and in this file.
#   - To perform custom initialisation after types have been registered,
#       use the protected code section at the bottom of initialize().

import logging
logger = logging.getLogger('<dtml-var "product_name">')
logger.debug('Installing Product')

import os
import os.path
from Globals import package_home
import Products.CMFPlone.interfaces
from Products.Archetypes import listTypes
from Products.Archetypes.atapi import *
from Products.Archetypes.utils import capitalize
<dtml-if "has_skins">
from Products.CMFCore import DirectoryView
</dtml-if>
from Products.CMFCore import permissions as cmfpermissions
from Products.CMFCore import utils as cmfutils
from Products.CMFPlone.utils import ToolInit
from config import *
<dtml-if "generator.shouldPatchDCWorkflow(package)">
import dcworkflowpatch
</dtml-if>

<dtml-if "has_skins">
DirectoryView.registerDirectory('skins', product_globals)

</dtml-if>
<dtml-if "additional_permissions">
# Register additional (custom) permissions used by this product
<dtml-in "additional_permissions">
<dtml-let permdef="_['sequence-item']">
cmfpermissions.setDefaultRoles('<dtml-var "product_name">: <dtml-var "permdef[0]">',[<dtml-var "','.join(permdef[1])">])
</dtml-let>
</dtml-in>
</dtml-if>

<dtml-var "protected_init_section_head">

def initialize(context):
    """initialize product (called by zope)"""
<dtml-var "protected_init_section_top">
<dtml-if "class_imports or package_imports">
    # imports packages and types for registration
<dtml-in "package_imports">
<dtml-if sequence-item>
    import <dtml-var sequence-item>
</dtml-if>
</dtml-in>

<dtml-in "class_imports">
    import <dtml-var sequence-item>
</dtml-in>

</dtml-if>
<dtml-if "has_tools">
    # Initialize portal tools
    tools = [<dtml-var "', '.join (tool_names)">]
    ToolInit( PROJECTNAME +' Tools',
                tools = tools,
                icon='tool.gif'
                ).initialize( context )

</dtml-if>
<dtml-if "class_imports or package_imports">
    # Initialize portal content
<dtml-if "creation_permissions">
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = all_content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = all_constructors,
        fti                = all_ftis,
        ).initialize(context)

    # Give it some extra permissions to control them on a per class limit
    for i in range(0,len(all_content_types)):
        klassname=all_content_types[i].__name__
        if not klassname in ADD_CONTENT_PERMISSIONS:
            continue

        context.registerClass(meta_type   = all_ftis[i]['meta_type'],
                              constructors= (all_constructors[i],),
                              permission  = ADD_CONTENT_PERMISSIONS[klassname])
<dtml-else>
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
</dtml-if>
</dtml-if>

<dtml-var "protected_init_section_bottom">
