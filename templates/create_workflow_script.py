## Workflow scripts
## <dtml-var "parsedModule.functions.keys()">    
<dtml-in "statemachine.getAllTransitionActions()">
<dtml-let action="_['sequence-item']">

<dtml-if "action.getCleanName() not in parsedModule.functions.keys()">
def <dtml-var "action.getCleanName()">(self,state_change,**kw):
<dtml-var "utils.indent(action.getExpressionBody() or 'pass' ,1)">

<dtml-else>
<dtml-var "parsedModule.functions[action.getCleanName()].getSrc()">
</dtml-if>
</dtml-let>
</dtml-in>

