<dtml-let assocs="generator.getAssocs(klass)"
          atts="generator.getAtts(klass)"
          dependentImports="generator.generateDependentImports(klass)"
          additionalImports="generator.generateAdditionalImports(klass)"
          taggedImports="generator.getImportsByTaggedValues(klass)"
          vars="atts+[a.toEnd for a in assocs]">

<dtml-let base_class="klass.getTaggedValue('base_class') or 'models.Model' or ','.join([p.getCleanName() for p in klass.getGenParents()]+['models.Model'])">

class <dtml-var "klass.getCleanName()"><dtml-if base_class>(<dtml-var base_class>)</dtml-if>:
</dtml-let>
    <dtml-var "generator.getDocFor(klass,indent=1)">

<dtml-var "generator.getProtectedSection(parsed_class,'class-header_'+klass.getCleanName(),1)">

<dtml-if vars>
<dtml-if atts>

    #attributes
    ##############

</dtml-if>
<dtml-in atts>
    <dtml-var "_['sequence-item'].getCleanName()">=<dtml-var "generator.convertAttToDjango(_['sequence-item'], klass)">
</dtml-in>
<dtml-if assocs>

    #associations
    ##############

</dtml-if>
<dtml-in assocs>
<dtml-let m="_['sequence-item']">
    #<dtml-var "_['sequence-item'].getName()">
    <dtml-var "m.toEnd.getCleanName()">=<dtml-var "generator.convertAssocToDjango(m)">
<dtml-if "m.fromEnd.getTaggedValue('documentation',False)">
    """<dtml-var "m.fromEnd.getTaggedValue('documentation','')">"""

</dtml-if>
</dtml-let>
</dtml-in>

</dtml-if>

    #methods
    ##############

<dtml-in "generator.getMethods(klass)">
<dtml-let m="_['sequence-item']">
<dtml-if "m.getParent().__class__.__name__=='XMIInterface'">
    #from Interface <dtml-var "m.getParent().getName()">:
</dtml-if>
<dtml-if "not m.getTaggedValue('force-code', False) and ((hasattr(parsed_class,'methods') and (m.getCleanName() in parsed_class.methods.keys())) or (hasattr(m.inherited_from,'parsed_class') and (hasattr(m.inherited_from.parsed_class,'methods')) and (m.getCleanName() in m.inherited_from.parsed_class.methods.keys())))">
<dtml-var "generator.getMethodSource(generator.getMethods(klass),m)">
<dtml-let param="generator.getParamList(m)">
    def <dtml-var "m.getName()">(self<dtml-if param>, <dtml-var param></dtml-if>):
</dtml-let>
        <dtml-var "generator.getDocFor(m)">
        #Code from UML-Diagramm
        <dtml-var "m.getTaggedValue('code','pass')">
</dtml-if>
<dtml-if "m.isStatic()">
    <dtml-var "m.getName()"> = staticmethod(<dtml-var "m.getName()">)
</dtml-if>
</dtml-let>



</dtml-in>
<dtml-if "not '__str__' in generator.getMethodNames(klass) and not generator.model_representation is None">
    def __str__(self):
        return self.<dtml-var "generator.model_representation.getName()">
</dtml-if>

    #meta
    ##############

<dtml-if "klass.getTaggedValue('admin',False)">
    class Admin:
        <dtml-var "klass.getTaggedValue('admin','pass')">
</dtml-if>

<dtml-if "klass.getTaggedValue('meta',False)">
    class Meta:
        <dtml-var "klass.getTaggedValue('meta','pass')">
</dtml-if>

</dtml-let>