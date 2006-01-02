<dtml-var "generator.generateModuleInfoHeader(package)">
from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod.ExternalMethod import ExternalMethod

def installWorkflows(self, package, out):
    """Install the custom workflows for this product."""

    productname = '<dtml-var "package.getCleanName()">'
    workflowTool = getToolByName(self, 'portal_workflow')
<dtml-in "package.getStateMachines()">
<dtml-let sm="_['sequence-item']">

    ourProductWorkflow = ExternalMethod('temp', 'temp',
                         productname+'.'+'<dtml-var "generator.cleanName(sm.getName())">',
                         'create<dtml-var "generator.cleanName(sm.getName())">')
    workflow = ourProductWorkflow(self, '<dtml-var "generator.cleanName(sm.getName())">')
    workflowTool._setObject('<dtml-var "generator.cleanName(sm.getName())">', workflow)
    workflowTool.setChainForPortalTypes(<dtml-var "repr(sm.getClassNames())">, workflow.getId())
</dtml-let>
</dtml-in>

    return workflowTool
