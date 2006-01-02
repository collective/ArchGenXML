<dtml-var "generator.generateModuleInfoHeader(package)">
# Workflow Scripts for: <dtml-var "statemachine.getCleanName()">

<dtml-var "generator.getProtectedSection(parsedModule,'workflow-script-header',0)">
## <dtml-var "parsedModule.functions.keys()">
<dtml-in "statemachine.getAllTransitionActionNames()">
<dtml-let actionname="_['sequence-item']">
<dtml-let action="statemachine.getTransitionActionByName(actionname)">

<dtml-if "actionname not in parsedModule.functions.keys()">
def <dtml-var "actionname">(self,state_change,**kw):
<dtml-var "utils.indent(action.getExpressionBody() or 'pass' ,1)">
<dtml-else>
<dtml-var "parsedModule.functions[actionname].getSrc()">
</dtml-if>

</dtml-let>
</dtml-let>
</dtml-in>
