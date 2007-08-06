import os
from operator import itemgetter
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
            p_dict['permission'] = self.processExpression(
                p_dict['permission'], asString=False)
        return pdefs

    # XXX: Almost the same again.
    def getAllPermissionNames(self, statemachine):
        source_pdefs = statemachine.getAllPermissionNames()
        result_pdefs = [self.processExpression(pdef, asString=False)
                        for pdef in source_pdefs]
        return result_pdefs

    def generateWorkflows(self):
        log.debug("Generating workflows.")
        statemachines = self.package.getStateMachines()
        if not statemachines:
            log.debug("No workflows that agx knows off.")
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
        profileDir = os.path.join(self.package.getFilePath(), 'profiles', 'default')
        self.atgenerator.makeDir(profileDir)
        workflowDir = os.path.join(profileDir, 'workflows')
        self.atgenerator.makeDir(workflowDir)

        for sm in statemachines:
            d['statemachine'] = sm
            d['info'] = WorkflowInfo(sm, self)
            smName = utils.cleanName(sm.getName())
            smDir = os.path.join(workflowDir, smName)
            self.atgenerator.makeDir(smDir)
            log.debug("Generated specific workflow's dir '%s'.",
                      smDir)
            # Generate workflow script
            log.info("Generating workflow '%s'.", smName)
            templ = self.readTemplate('definition.xml')
            scriptpath = os.path.join(smDir, 'definition.xml')
            dtml = HTML(templ, d)
            res = dtml()
            of = self.atgenerator.makeFile(scriptpath)
            of.write(res)
            of.close()

            # Generate workflow transition script, if any
            if sm.getAllTransitionActionNames():
                log.info("Generating workflow script(s).")
                templ = self.readTemplate('create_workflow_script.py')
                scriptpath = os.path.join(extDir, smName + '_scripts.py')
                filesrc = self.atgenerator.readFile(scriptpath) or ''
                parsedModule = PyModule(filesrc, mode='string')
                d['parsedModule'] = parsedModule
                dtml = HTML(templ, d)
                res = dtml()
                of = self.atgenerator.makeFile(scriptpath)
                of.write(res)
                of.close()
            else:
                log.info("Workflow %s has no script(s)." % smName)

        del d['statemachine']
        log.debug("Creating InstallWorkflows.py file.")
        templ = self.readTemplate('InstallWorkflows.py')
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

class WorkflowInfo(object):
    """View-like utility class.
    """

    def __init__(self, sm, generator):
        self.sm = sm # state machine.
        self.generator = generator

    def id(self):
        return self.sm.getCleanName()

    def initialState(self):
        return self.sm.getInitialState().getName()

    def states(self):
        states = self.sm.getStates(no_duplicates = 1)
        filtered = [s for s in states if s.getName()]
        filtered.sort(cmp=lambda x,y: cmp(x.getName(), y.getName()))
        result = []
        for item in filtered:
            state = {}
            state['id'] = item.getName()
            state['title'] = item.getTitle(self.generator)
            state['description'] = item.getDescription()
            state['exit-transitions'] = [t.getName() for t in
                                         item.getOutgoingTransitions()]
            perms = self.generator.getPermissionsDefinitions(item)
            perms.sort(key=itemgetter('permission'))
            state['permissions'] = perms
            result.append(state)
        return result

    def transitions(self):
        transitions = self.sm.getTransitions(no_duplicates = 1)
        filtered = [t for t in transitions if t.getName()]
        filtered.sort(cmp=lambda x,y: cmp(x.getName(), y.getName()))
        return filtered

TODO = """

  <!--<dtml-var "_['sequence-item']['description']">-->


<dtml-if "transition.getAction()">

    ## Creation of workflow scripts
    for wf_scriptname in <dtml-var "repr(transition.getAction().getUsedActionNames())">:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.<dtml-var "statemachine.getCleanName()">_scripts',
                wf_scriptname))
</dtml-if>



<dtml-in "statemachine.getAllWorklistNames()">
<dtml-let worklistname="_['sequence-item']">
<dtml-let worklistStateNames="statemachine.getWorklistStateNames(worklistname)">
    worklistDef = workflow.worklists['<dtml-var "worklistname">']
    worklistStates = <dtml-var "repr(worklistStateNames)">
    actbox_url = "%(portal_url)s/search?review_state=" + "&review_state=".join(worklistStates)
    worklistDef.setProperties(description="Reviewer tasks",
                              actbox_name="Pending (%(count)d)",
                              actbox_url=actbox_url,
                              actbox_category="global",
                              props={'guard_permissions': '<dtml-var "statemachine.getWorklistGuardPermission(worklistname)">',
                                     'guard_roles': '<dtml-var "statemachine.getWorklistGuardRole(worklistname)">',
                                     'var_match_review_state': ';'.join(worklistStates)})
</dtml-let>
</dtml-let>
</dtml-in>

"""
