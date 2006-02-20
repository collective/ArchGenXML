#generate workflows
import os
from documenttemplate.documenttemplate import HTML

from utils import readTemplate, cleanName
import utils
from PyParser import PyModule
from BaseGenerator import BaseGenerator
import logging
log = logging.getLogger('workflow')

class WorkflowGenerator(BaseGenerator):
    atgenerator=None
    package=None

    def __init__(self,package,atgenerator):
        self.package=package
        self.atgenerator=atgenerator
        self.targetRoot=atgenerator.targetRoot
        self.method_preservation=atgenerator.method_preservation


    def generateWorkflows(self):
        statemachines=self.package.getStateMachines()
        if not statemachines:
            return

        d={'package'    : self.package,
           'generator'  : self,
           'wfgenerator' : self,
           'atgenerator': self.atgenerator,
           'builtins'   : __builtins__,
           'utils'       :utils,
        }
        d.update(__builtins__)


        for sm in statemachines:

            extDir=os.path.join(self.package.getFilePath(),'Extensions')
            scriptpath=os.path.join(extDir,cleanName(sm.getName())+'.py')

            filesrc=self.atgenerator.readFile(scriptpath) or ''
            parsedModule=PyModule(filesrc,mode='string')

            d['statemachine']=sm
            d['parsedModule']=parsedModule

            # generate workflow script
            log.info("Generating workflow '%s'.",
                     sm.getName())
            templ=readTemplate('create_workflow.py')
            dtml=HTML(templ,d)
            res=dtml()

            self.atgenerator.makeDir(extDir)
            of=self.atgenerator.makeFile(scriptpath)
            of.write(res)
            of.close()

            # generate workflow transition script
            log.info("Generating workflow script(s).")
            templ=readTemplate('create_workflow_script.py')

            scriptpath=os.path.join(extDir,cleanName(sm.getName())+'_scripts.py')
            filesrc=self.atgenerator.readFile(scriptpath) or ''
            parsedModule=PyModule(filesrc,mode='string')
            d['parsedModule']=parsedModule
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

    def getActionScriptName(self,action):
        trans=action.getParent()
        wf=trans.getParent()
        return '%s_%s_%s' %( wf.getCleanName(),trans.getCleanName(),action.getCleanName())
