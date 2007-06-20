<dtml-let assocs="klass.assocsFrom"
          atts="generator.getAtts(klass)"
          dependentImports="generator.generateDependentImports(klass)"
          additionalImports="generator.generateAdditionalImports(klass)"
          taggedImports="generator.getImportsByTaggedValues(klass)"
          vars="atts+[a.toEnd for a in assocs]">
<dtml-if taggedImports><dtml-var taggedImports></dtml-if>
<dtml-if dependentImports><dtml-var dependentImports></dtml-if>
<dtml-if additionalImports><dtml-var additionalImports></dtml-if>


<dtml-var "generator.getProtectedSection(parsed_mod, 'module-header')">

<dtml-if vars>
<dtml-in atts>
<dtml-if "_['sequence-item'].mult[1]==1">
<dtml-var "_['sequence-item'].getCleanName()">=<dtml-var "_['sequence-item'].getTaggedValue('default',_['sequence-item'].type)">
<dtml-else>
<dtml-var "_['sequence-item'].getCleanName()">=<dtml-var "{None:'[]','dict':'{}','list':'[]','tuple':'()'}.get(_['sequence-item'].getStereoType(),str(_['sequence-item'].getStereoType())+'()')">
</dtml-if>
</dtml-in>
<dtml-in assocs>
<dtml-let m="_['sequence-item']">
<dtml-if "m.toEnd.getUpperBound()==1">
<dtml-var "m.toEnd.getCleanName()">=<dtml-var "m.toEnd.getTarget().getCleanName()">()
<dtml-else>
<dtml-var "m.toEnd.getCleanName()">=<dtml-var "{None:'[]','dict':'{}','list':'[]','tuple':'()'}.get(_['sequence-item'].getStereoType(),str(_['sequence-item'].getStereoType())+'()')">
</dtml-if>
</dtml-let>
</dtml-in>
</dtml-if>

<dtml-in "generator.getMethods(klass)">

<dtml-let m="_['sequence-item']">
<dtml-if "m.getParent().__class__.__name__=='XMIInterface'">
    #from Interface <dtml-var "m.getParent().getName()">:
</dtml-if>
<dtml-if "parsed_funcs and m.persistence.name in parsed_funcs.keys()">
<dtml-var "generator.getMethodSource(parsed_funcs, m, indent=1)">

<dtml-else>
<dtml-let param="generator.getParamList(m)">
def <dtml-var "m.getName()">(<dtml-if param><dtml-var param></dtml-if>):
</dtml-let>
    <dtml-var "generator.getDocFor(m, indent=1)">
    pass

</dtml-if>
<dtml-if "m.isStatic()">
    <dtml-var "m.getName()"> = staticmethod(<dtml-var "m.getName()">)
</dtml-if>
</dtml-let>
</dtml-in>
<dtml-var "generator.getProtectedSection(parsed_mod,'module-footer')">
</dtml-let>