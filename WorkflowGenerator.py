#generate workflows
import os
from documenttemplate.documenttemplate import HTML

from utils import readTemplate, cleanName
import utils

from PyParser import PyModule

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
        
        d={'package':self.package,'generator':self,'builtins':__builtins__,'utils':utils}
        d.update(__builtins__)
        
        for sm in statemachines:
            extDir=os.path.join(self.package.getFilePath(),'Extensions')
            scriptpath=os.path.join(extDir,cleanName(sm.getName())+'.py')

            filesrc=self.atgenerator.readFile(scriptpath) or ''
            parsedModule=PyModule(filesrc,mode='string')

            d['statemachine']=sm
            d['parsedModule']=parsedModule
            
            print 'generating Workflow:', sm.getName()
            templ=readTemplate('create_workflow.py')
            dtml=HTML(templ,d)
            res=dtml()
            
            self.atgenerator.makeDir(extDir)
            of=self.atgenerator.makeFile(scriptpath)
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
    