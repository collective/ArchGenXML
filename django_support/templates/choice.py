<dtml-let assocs="klass.getFromAssociations(aggtypes=['none','aggregation','composite'])"
          atts="klass.getAttributeDefs()"
          dependentImports="generator.generateDependentImports(klass)"
          additionalImports="generator.generateAdditionalImports(klass)"
          taggedImports="generator.getImportsByTaggedValues(klass)"
          vars="atts+[a.toEnd for a in assocs]">

"""<dtml-var "utils.indent(klass.getDocumentation(), 1, skipFirstRow=True, stripBlank=True)">
"""
<dtml-var "klass.getCleanName()"> = (
<dtml-if vars>
<dtml-in atts>
<dtml-let value="_['sequence-item'].getTaggedValue('documentation',_['sequence-item'].getCleanName())">
    ('<dtml-var "_['sequence-item'].getCleanName()">', <dtml-var "generator.translate(value)">),
</dtml-let>
</dtml-in>
</dtml-if>
)
</dtml-let>