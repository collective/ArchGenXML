# Initialise this package. You may add your own code in the protected sections
# below.

<dtml-var "protected_module_header">

#subpackages
<dtml-in "package_imports">
import <dtml-var sequence-item>
</dtml-in>

#classes
<dtml-if "not package.hasStereoType(['tests'])">
<dtml-in "importedClasses">
from <dtml-var "_['sequence-item'].getModuleName()"> import <dtml-var "_['sequence-item'].getCleanName()">
</dtml-in>
</dtml-if>

<dtml-var "protected_module_footer">
