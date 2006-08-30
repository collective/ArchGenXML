<dtml-var "generator.generateModuleInfoHeader(package)">
from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod.ExternalMethod import ExternalMethod

<dtml-var "generator.getProtectedSection(parsedModule,
'module-header', 0)">
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
    if '<dtml-var "generator.cleanName(sm.getName())">' in workflowTool.listWorkflows():
        print >> out, '<dtml-var "generator.cleanName(sm.getName())"> already in workflows.'
    else:
        workflowTool._setObject('<dtml-var "generator.cleanName(sm.getName())">', workflow)
    workflowTool.setChainForPortalTypes(<dtml-var "repr(sm.getClassNames())">, workflow.getId())
</dtml-let>
</dtml-in>

<dtml-var "generator.getProtectedSection(parsedModule,
'after-workflow-install', 1)">
    return workflowTool

def uninstallWorkflows(self, package, out):
    """Deinstall the workflows.

    This code doesn't really do anything, but you can place custom
    code here in the protected section.
    """

<dtml-var "generator.getProtectedSection(parsedModule,
'workflow-uninstall', 1)">
    pass
