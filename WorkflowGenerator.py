import os
import utils
import logging
from PyParser import PyModule
from BaseGenerator import BaseGenerator
from documenttemplate.documenttemplate import HTML

log = logging.getLogger('workflow')


class WorkflowGenerator(BaseGenerator):

    atgenerator = None
    package = None

    def __init__(self, package, atgenerator):
        self.package = package
        self.atgenerator = atgenerator
        self.__dict__.update(atgenerator.__dict__)

    # XXX: now i start here something ugly, but i dont have time to
    # cleanup XMIParsers code - it has too much logic in, which should
    # be in this class.
    # Permissions from XMI are supposed to be strings upon here. But
    # we may have an import of a class containing the permissions as
    # attributes. So lets do a processExpression on each permission.
    def getPermissionsDefinitions(self, state):
        pdefs = state.getPermissionsDefinitions()
        for p_dict in pdefs:
            p_dict['permission'] = self.processExpression(p_dict['permission'])
        return pdefs

    # XXX: Almost the same again.
    def getAllPermissionNames(self, statemachine):
        source_pdefs = statemachine.getAllPermissionNames()
        result_pdefs = [self.processExpression(pdef) for pdef in source_pdefs]
        return result_pdefs

    def generateWorkflows(self):
        statemachines = self.package.getStateMachines()
        if not statemachines:
            return

        d = {
            'package': self.package,
            'generator': self,
            'wfgenerator': self,
            'atgenerator': self.atgenerator,
            'builtins': __builtins__,
            'utils' :utils,
        }
        d.update(__builtins__)

        extDir = os.path.join(self.package.getFilePath(), 'Extensions')
        self.atgenerator.makeDir(extDir)

        for sm in statemachines:
            d['statemachine'] = sm
            sm_name = utils.cleanName(sm.getName())

            # Generate workflow script
            log.info("Generating workflow '%s'.", sm_name)
            templ = utils.readTemplate('create_workflow.py')
            scriptpath = os.path.join(extDir, sm_name + '.py')
            filesrc = self.atgenerator.readFile(scriptpath) or ''
            parsedModule = PyModule(filesrc, mode='string')
            d['parsedModule'] = parsedModule
            dtml = HTML(templ, d)
            res = dtml()
            of = self.atgenerator.makeFile(scriptpath)
            of.write(res)
            of.close()

            # Generate workflow transition script, if any
            if sm.getAllTransitionActionNames():
                log.info("Generating workflow script(s).")
                templ = utils.readTemplate('create_workflow_script.py')
                scriptpath = os.path.join(extDir, sm_name + '_scripts.py')
                filesrc = self.atgenerator.readFile(scriptpath) or ''
                parsedModule = PyModule(filesrc, mode='string')
                d['parsedModule'] = parsedModule
                dtml = HTML(templ, d)
                res = dtml()
                of = self.atgenerator.makeFile(scriptpath)
                of.write(res)
                of.close()
            else:
                log.info("Workflow %s has no script(s)." % sm_name)

        del d['statemachine']
        templ = utils.readTemplate('InstallWorkflows.py')
        scriptpath = os.path.join(extDir, 'InstallWorkflows.py')
        filesrc = self.atgenerator.readFile(scriptpath) or ''
        parsedModule = PyModule(filesrc, mode='string')
        d['parsedModule'] = parsedModule
        dtml = HTML(templ, d)
        res = dtml()
        of = self.atgenerator.makeFile(scriptpath)
        of.write(res)
        of.close()

    def getActionScriptName(self, action):
        trans = action.getParent()
        wf = trans.getParent()
        return '%s_%s_%s' % (wf.getCleanName(), trans.getCleanName(), action.getCleanName())
