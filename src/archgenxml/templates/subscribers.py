from zope.component import adapter
<dtml-var "generator.getProtectedSection(parsed_module, 'module-header')">

<dtml-in "subscribers">
<dtml-let subscriber="_['sequence-item']">
@adapter(<dtml-var "subscriber['name']">)
def <dtml-var "subscriber['name']">(<dtml-if "subscriber['isobjectevent']">obj, </dtml-if>event):
    """<dtml-var "subscriber['docstring']">"""

</dtml-let>
</dtml-in>    
<dtml-in "parsed_module.functions">
<dtml-var "_['sequence-item'].src">
</dtml-in>

<dtml-var "generator.getProtectedSection(parsed_module, 'module-footer')">
    