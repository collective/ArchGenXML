#
# Product configuration. This contents of this module will be imported into
# __init__.py and every content type module.
#
# If you wish to perform custom configuration, you may put a file AppConfig.py
# in your product's root directory. This will be included in this file if
# found.
#
from Products.CMFCore.CMFCorePermissions import setDefaultRoles
<dtml-if "[cn for cn in generator.getGeneratedClasses(package) if cn.hasStereoType(generator.cmfmember_stereotype)]">
from Products.CMFMember.MemberPermissions import ADD_MEMBER_PERMISSION
</dtml-if>
<dtml-var "generator.getProtectedSection(parsed_config,'config-head')">

PROJECTNAME = "<dtml-var "package.getProductName ()">"

# Check for Plone 2.1
try:
    from Products.CMFPlone.migrations import v2_1
except ImportError:
    HAS_PLONE21 = False
else:
    HAS_PLONE21 = True
    
# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "<dtml-var "default_creation_permission">"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
<dtml-if "creation_permissions">
ADD_CONTENT_PERMISSIONS = {
<dtml-in "creation_permissions">
<dtml-let perm="_['sequence-item']">
    '<dtml-var "perm[0]">': <dtml-var "perm[1]">,
</dtml-let>
</dtml-in>
}

<dtml-if "len(creation_roles) > 0">
<dtml-in "range(0, len(creation_roles) )">
<dtml-let index="_['sequence-item']">
setDefaultRoles(<dtml-var "creation_roles[index][0]">, <dtml-var "creation_roles[index][1]">)
</dtml-let>
</dtml-in>
</dtml-if>
</dtml-if>

product_globals=globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

# You can overwrite these two in an AppConfig.py:
# STYLESHEETS = [{'id': 'my_global_stylesheet.css'},
#                {'id': 'my_contenttype.css',
#                 'expression': 'python:object.getTypeInfo().getId() == "MyType"}]
# You can do the same with JAVASCRIPTS.
STYLESHEETS = []
JAVASCRIPTS = []

<dtml-var "generator.getProtectedSection(parsed_config,'config-bottom')">

# load custom configuration not managed by ArchGenXML
try:
    from Products.<dtml-var "package.getProductName ()">.AppConfig import *
except ImportError:
    pass

# End of config.py
