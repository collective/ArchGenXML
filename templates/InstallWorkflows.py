from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod.ExternalMethod import ExternalMethod

def installWorkflows(self,out):
    ''' '''
    productname='<dtml-var "package.getCleanName()">'
    wft=getToolByName(self,'portal_workflow')

    <dtml-in "package.getStateMachines()">
    <dtml-let sm="_['sequence-item']">
        
    iwf=ExternalMethod('temp','temp',productname+'.'+'<dtml-var "generator.cleanName(sm.getName())">', 'create<dtml-var "generator.cleanName(sm.getName())">') 
    wf=iwf('<dtml-var "generator.cleanName(sm.getName())">')
    wft._setObject('<dtml-var "generator.cleanName(sm.getName())">',wf)
    wft.setChainForPortalTypes( <dtml-var "repr(sm.getClassNames())">,wf.getId())
    
    </dtml-let>
    </dtml-in>


    return wft
