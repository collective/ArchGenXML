#
# Product configuration. This contents of this module will be imported into
# __init__.py and every type definition. You may write a file AppConfig.py
# which will use be imported here if it is found, for your custom configuration.
#

ADD_CONTENT_PERMISSION = <dtml-var "add_content_permission">
PROJECTNAME = "<dtml-var "package.getProductName ()">"

product_globals=globals()

try:
    from Products.<dtml-var "package.getProductName ()">.AppConfig import *
except ImportError:
    pass