<dtml-var "generator.generateModuleInfoHeader(package)">
<dtml-var "protected_module_header">

# Subpackages
<dtml-if "len(subpackages)">
__all__ = [<dtml-in "subpackages"> <dtml-var sequence-item>,</dtml-in> ]
# NARF: not sure if __all__ is correct with other imports..
# NARF: pretty sure it improves package reload behaviour in zmi, though
</dtml-if>
# Additional
<dtml-var "package.getTaggedValue('imports')">
# Classes
<dtml-if "not package.hasStereoType(['tests'])">
<dtml-in "class_imports">
import <dtml-var sequence-item>
</dtml-in>
</dtml-if>

<dtml-var "protected_module_footer">
