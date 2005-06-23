<dtml-let assocs="klass.getFromAssociations(aggtypes=['none','aggregation','composite'])" atts="klass.getAttributeDefs()" vars="atts+[a.toEnd for a in assocs]" >

<dtml-var "generator.getProtectedSection(parsed_class,'module-header')">

<dtml-var "generator.generateDependentImports(klass)">
class <dtml-var "klass.getCleanName()"><dtml-if "klass.getGenParents()">(<dtml-var "','.join([p.getCleanName() for p in klass.getGenParents()])">)</dtml-if>:
    ''' <dtml-var "klass.getDocumentation()">'''
<dtml-var "generator.generateImplements(klass,[p.getCleanName() for p in klass.getGenParents()])">
<dtml-var "generator.getProtectedSection(parsed_class,'class-header_'+klass.getCleanName(),1)">

<dtml-if vars>
    def __init__(self,*args,**kwargs):
<dtml-var "generator.getProtectedSection(parsed_class,'class-init',2)">
        #attributes
<dtml-in atts>
        self.<dtml-var "_['sequence-item'].getCleanName()">=None
</dtml-in>       

        #associations
<dtml-in assocs>
<dtml-if "_['sequence-item'].toEnd.getUpperBound()=='1'">
        self.<dtml-var "_['sequence-item'].toEnd.getCleanName()">=None 
<dtml-else>
        self.<dtml-var "_['sequence-item'].toEnd.getCleanName()">=<dtml-var "{None:'[]','dict':'{}','list':'[]','tuple':'()'}.get(_['sequence-item'].getStereoType(),str(_['sequence-item'].getStereoType())+'()')">
</dtml-if>
</dtml-in>       
</dtml-if>
<dtml-in "generator.getMethodsToGenerate(klass)[0]">
<dtml-let m="_['sequence-item']">
<dtml-if "m.getParent().__class__.__name__=='XMIInterface'"> 
    
    #from Interface <dtml-var "m.getParent().getName()">:
</dtml-if>
<dtml-if "parsed_class and m.getCleanName() in parsed_class.methods.keys()">

<dtml-var "parsed_class.methods[m.getCleanName()].getSrc()">    
<dtml-else>

    def <dtml-var "m.getName()">(self,<dtml-var "','.join(m.getParamNames())">):
        pass
</dtml-if>
</dtml-let>
</dtml-in>

<dtml-in vars>
<dtml-let mutator="'set'+_['sequence-item'].getCleanName().capitalize()" accessor="'get'+_['sequence-item'].getCleanName().capitalize()">
<dtml-if "mutator not in [m.name for m in generator.getMethodsToGenerate(klass)[1]]">    
    def <dtml-var "mutator">(self,value):
        self.<dtml-var "_['sequence-item'].getCleanName()">=value

</dtml-if>
<dtml-if "accessor not in [m.name for m in generator.getMethodsToGenerate(klass)[1]]">    
    def <dtml-var "accessor">(self):
        return self.<dtml-var "_['sequence-item'].getCleanName()">

</dtml-if>
</dtml-let>
</dtml-in>
    
<dtml-in "[m for m in generator.getMethodsToGenerate(klass)[1] if m.name not in ['__init__']]">

<dtml-var "_['sequence-item'].getSrc()">            
</dtml-in>
    
<dtml-var "generator.getProtectedSection(parsed_class,'module-footer')">
</dtml-let>