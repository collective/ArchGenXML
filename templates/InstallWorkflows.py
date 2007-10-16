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
    if workflow.getId() in workflowTool.listWorkflows():
        print >> out, '%s already in workflows.' % workflow.getId()
    else:
        try:
            # plone 2.x
            workflowTool._setObject('<dtml-var "generator.cleanName(sm.getName())">', workflow)
        except:
            # works in Plone 3.0, but isnt perfect! use ArchGenXML 2.0 for a 
            # better result!
            workflowTool._setOb('<dtml-var "generator.cleanName(sm.getName())">', workflow)
        print >> out, '%s added in workflows.' % workflow.getId()
    workflowTool.setChainForPortalTypes(<dtml-var "repr(sm.getClassNames())">, workflow.getId())
</dtml-let>
</dtml-in>

<dtml-var "generator.getProtectedSection(parsedModule,
'after-workflow-install', 1)">
    return out

def uninstallWorkflows(self, package, out):
    """Deinstall the workflows.

    This code doesn't really do anything, but you can place custom
    code here in the protected section.
    """

<dtml-var "generator.getProtectedSection(parsedModule,
'workflow-uninstall', 1)">
    pass
