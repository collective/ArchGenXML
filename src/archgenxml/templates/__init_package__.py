<dtml-var "generator.generateModuleInfoHeader(package, all=1)">
<dtml-var "protected_module_header">

# Subpackages
<dtml-in "package_imports">
import <dtml-var sequence-item>
</dtml-in>
# Additional
<dtml-var "package.getTaggedValue('imports')">
# Classes
<dtml-if "not package.hasStereoType(['tests'])">
<dtml-in "class_imports">
import <dtml-var sequence-item>
</dtml-in>
</dtml-if>

<dtml-var "protected_module_footer">
