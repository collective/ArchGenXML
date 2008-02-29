<dtml-let assocs="klass.getFromAssociations(aggtypes=['none','aggregation','composite'])"
          atts="klass.getAttributeDefs()"
          dependentImports="generator.generateDependentImports(klass)"
          additionalImports="generator.generateAdditionalImports(klass)"
          taggedImports="generator.getImportsByTaggedValues(klass)"
          vars="atts+[a.toEnd for a in assocs]">
<dtml-var "generator.getProtectedSection(parsed_class, 'module-header')">
from zope import interface
from zope import component
from Products.CMFPlone import utils
from Products.Five import BrowserView
<dtml-if taggedImports><dtml-var taggedImports></dtml-if>
<dtml-if dependentImports><dtml-var dependentImports></dtml-if>
<dtml-if additionalImports><dtml-var additionalImports></dtml-if>
<dtml-if "klass.hasStereoType('z3') or 'z3' in ['z3' for p in klass.getRealizationParents() if p.hasStereoType('z3')]">
</dtml-if>

<dtml-let base_class="klass.getTaggedValue('base_class') or ','.join([p.getCleanName() for p in klass.getGenParents()]) or 'BrowserView'">
class <dtml-var "klass.getCleanName()"><dtml-if base_class>(<dtml-var base_class>)</dtml-if>:
</dtml-let>
    """<dtml-var "utils.indent(klass.getDocumentation(), 1, skipFirstRow=True, stripBlank=True)">
    """
<dtml-var "generator.generateImplements(klass,[p.getCleanName() for p in klass.getGenParents()])">
<dtml-var "generator.getProtectedSection(parsed_class,'class-header_'+klass.getCleanName(),1)">
<dtml-in "generator.getMethodsToGenerate(klass)[0]">
<dtml-let m="_['sequence-item']">
<dtml-if "m.getParent().__class__.__name__=='XMIInterface'">
    #from Interface <dtml-var "m.getParent().getName()">:
</dtml-if>
<dtml-if "parsed_class and m.getCleanName() in parsed_class.methods.keys()">
<dtml-var "parsed_class.methods[m.getCleanName()].getSrc()">
<dtml-else>
<dtml-let param="', '.join(m.getParamNames())">
    def <dtml-var "m.getName()">(self<dtml-if param>, <dtml-var param></dtml-if>):
</dtml-let>
        pass

</dtml-if>
<dtml-if "m.isStatic()">
    <dtml-var "m.getName()"> = staticmethod(<dtml-var "m.getName()">)
</dtml-if>
</dtml-let>
</dtml-in>

<dtml-in "[m for m in generator.getMethodsToGenerate(klass)[1]]">

<dtml-var "_['sequence-item'].getSrc()">
</dtml-in>

<dtml-var "generator.getProtectedSection(parsed_class,'module-footer')"></dtml-let>
