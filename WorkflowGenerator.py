#generate workflows
import os
from documenttemplate.documenttemplate import HTML

from utils import readTemplate, cleanName

class WorkflowGenerator:
    atgenerator=None
    package=None
    
    def __init__(self,package,atgenerator):
        self.package=package
        self.atgenerator=atgenerator
        

        
    def generateWorkflows(self):
        statemachines=self.package.getStateMachines()
        if not statemachines:
            return
        
        print 'Generating Workflows'
        print '===================='
        
        d={'package':self.package,'generator':self,'builtins':__builtins__}
        d.update(__builtins__)
        
        for sm in statemachines:
            d['statemachine']=sm
            print 'generating Workflow:', sm.getName()
            templ=readTemplate('create_workflow.py')
            dtml=HTML(templ,d)
            res=dtml()
            
            extDir=os.path.join(self.package.getFilePath(),'Extensions')
            self.atgenerator.makeDir(extDir)
            of=self.atgenerator.makeFile(os.path.join(extDir,cleanName(sm.getName())+'.py'))
            of.write(res)
            of.close()

        del d['statemachine']
        templ=readTemplate('InstallWorkflows.py')
        dtml=HTML(templ,d)
        res=dtml()
        
        extDir=os.path.join(self.package.getFilePath(),'Extensions')
        self.atgenerator.makeDir(extDir)
        of=self.atgenerator.makeFile(os.path.join(extDir,'InstallWorkflows.py'))
        of.write(res)
        of.close()
        
    def cleanName(self,n):
        return cleanName(n)
    