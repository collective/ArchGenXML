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
        print 'Generating Workflows'
        print '===================='
        
        for sm in self.package.getStateMachines():
            print 'generating Workflow:', sm.getName()
            d={'package':self.package,'statemachine':sm,'generator':self}
            templ=readTemplate('create_workflow.py')
            dtml=HTML(templ,d)
            res=dtml()
            
            extDir=os.path.join(self.package.getFilePath(),'Extensions')
            self.atgenerator.makeDir(extDir)
            of=self.atgenerator.makeFile(os.path.join(extDir,cleanName(sm.getName())+'.py'))
            of.write(res)
            of.close()
            

        d={'package':self.package,'generator':self}
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
    