
<dtml-var "generator.getProtectedSection(parsed_class,'module-header')">

<dtml-var "generator.generateDependentImports(klass)">
class <dtml-var "klass.getCleanName()"><dtml-if "klass.getGenParents()">(<dtml-var "','.join([p.getCleanName() for p in klass.getGenParents()])">)</dtml-if>:
    ''' <dtml-var "klass.getDocumentation()">'''
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

    def <dtml-var "m.getName()">(self,<dtml-var "','.join(m.getParamNames())">):
        pass
    </dtml-if>
    </dtml-let>
    </dtml-in>
    
    #Manually created methods!!
    <dtml-in "generator.getMethodsToGenerate(klass)[1]">

<dtml-var "_['sequence-item'].getSrc()">            
    </dtml-in>
    
<dtml-var "generator.getProtectedSection(parsed_class,'module-footer')">
