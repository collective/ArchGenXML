#
# Product configuration. This contents of this module will be imported into
# __init__.py and every content type module.
#
# If you wish to perform custom configuration, you may put a file AppConfig.py
# in your product's root directory. This will be included in this file if
# found.
#

ADD_CONTENT_PERMISSION = <dtml-var "add_content_permission">
PROJECTNAME = "<dtml-var "package.getProductName ()">"

product_globals=globals()

try:
    from Products.<dtml-var "package.getProductName ()">.AppConfig import *
except ImportError:
    pass