# Initialise this package. You may add your own code in the protected sections
# below.

<dtml-var "protected_module_header"> 

#subpackages
<dtml-in "package_imports">
import <dtml-var sequence-item>
</dtml-in>

#classes
<dtml-if "not package.hasStereoType(['tests'])">
<dtml-in "class_imports">
import <dtml-var sequence-item>
</dtml-in>
</dtml-if>

<dtml-var "protected_module_footer">