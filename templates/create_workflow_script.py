## Workflow scripts
## <dtml-var "parsedModule.functions.keys()">    
<dtml-in "statemachine.getAllTransitionActions()">
<dtml-let action="_['sequence-item']">

<dtml-if "action.getBeforeActionName() and action.getBeforeActionName() not in parsedModule.functions.keys()">
def <dtml-var "action.getBeforeActionName()">(self,state_change,**kw):
<dtml-var "utils.indent(action.getExpressionBody() or 'pass' ,1)">
<dtml-else>
<dtml-if "action.getBeforeActionName()"><dtml-var "parsedModule.functions[action.getBeforeActionName()].getSrc()"></dtml-if>
</dtml-if>


<dtml-if "action.getAfterActionName() and action.getAfterActionName() not in parsedModule.functions.keys()">
def <dtml-var "action.getAfterActionName()">(self,state_change,**kw):
<dtml-var "utils.indent(action.getExpressionBody() or 'pass' ,1)">
<dtml-else>
<dtml-if "action.getAfterActionName()"><dtml-var "parsedModule.functions[action.getAfterActionName()].getSrc()"></dtml-if>
</dtml-if>

</dtml-let>
</dtml-in>

