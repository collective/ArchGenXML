<dtml-let assocs="klass.getFromAssociations(aggtypes=['none','aggregation','composite'])+generator.getParentAssocs(klass)"
          atts="klass.getAttributeDefs()+generator.getParentAtts(klass)"
          dependentImports="generator.generateDependentImports(klass)"
          additionalImports="generator.generateAdditionalImports(klass)"
          taggedImports="generator.getImportsByTaggedValues(klass)"
          vars="atts+[a.toEnd for a in assocs]">

<dtml-let base_class="klass.getTaggedValue('base_class') or 'unittest.TestCase' or ','.join([p.getCleanName() for p in klass.getGenParents()]">

class <dtml-var "klass.getCleanName()"><dtml-if base_class>(<dtml-var base_class>)</dtml-if>:
</dtml-let>
    <dtml-var "generator.getDocFor(klass,indent=1)">

<dtml-if vars>
<dtml-if atts>

    #attributes
    ##############

</dtml-if>
<dtml-in atts>
    <dtml-var "_['sequence-item'].getCleanName()">=<dtml-var "generator.convertAttToDjango(_['sequence-item'])">
</dtml-in>
<dtml-if assocs>

    #associations
    ##############

</dtml-if>
<dtml-in assocs>
    <dtml-var "_['sequence-item'].toEnd.getCleanName()">=<dtml-var "generator.convertAssocToDjango(_['sequence-item'])">
<dtml-if "_['sequence-item'].fromEnd.getTaggedValue('documentation',False)">
    """<dtml-var "_['sequence-item'].fromEnd.getTaggedValue('documentation','')">"""

</dtml-if>
</dtml-in>

</dtml-if>

<dtml-in "generator.getMethodsToGenerate(klass)[0]">
<dtml-let m="_['sequence-item']">
<dtml-if "m.getParent().__class__.__name__=='XMIInterface'">
    #from Interface <dtml-var "m.getParent().getName()">:
</dtml-if>
<dtml-if "parsed_class and m.getCleanName() in parsed_class.methods.keys()">
<dtml-var "generator.refreshDocumentationInClassMethods(parsed_class, m)">


<dtml-else>
<dtml-let param="', '.join(m.getParamNames())">
    def <dtml-var "m.getName()">(self<dtml-if param>, <dtml-var param></dtml-if>):
</dtml-let>
<dtml-if "m.getTaggedValue('documentation',False)">
        <dtml-var "generator.getDocFor(m)">
</dtml-if>
        pass



</dtml-if>
<dtml-if "m.isStatic()">
    <dtml-var "m.getName()"> = staticmethod(<dtml-var "m.getName()">)
</dtml-if>
</dtml-let>
</dtml-in>
<dtml-if "not generator.model_representation is None">
    def __str__(self):
        return self.<dtml-var "generator.model_representation.getName()">
</dtml-if>

<dtml-if "klass.getTaggedValue('admin',False)">
    class Admin:
        <dtml-var "klass.getTaggedValue('admin','pass')">
</dtml-if>

<dtml-if "klass.getTaggedValue('meta',False)">
    class Meta:
        <dtml-var "klass.getTaggedValue('meta','pass')">
</dtml-if>
</dtml-let>