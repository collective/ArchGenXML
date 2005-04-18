<dtml-let infoheader="atgenerator.getHeaderInfo(package)">
""" Workflow Scripts for: <dtml-var "statemachine.getCleanName()"> """

# <dtml-var "infoheader['copyright']">
#
<dtml-var "infoheader['date']"># Generator: ArchGenXML Version <dtml-var "infoheader['version']">
#            http://sf.net/projects/archetypes/
#
# <dtml-var "infoheader['licence']">
#
__author__    = '''<dtml-var "infoheader['authorline']">'''
__docformat__ = 'plaintext'
__version__   = '$ Revision 0.0 $'[11:-2]
</dtml-let>

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
