from operator import itemgetter
import os.path
import utils
import logging
from PyParser import PyModule
from BaseGenerator import BaseGenerator
from archgenxml.documenttemplate.documenttemplate import HTML

log = logging.getLogger('workflow')


class WorkflowGenerator(BaseGenerator):

    atgenerator = None
    package = None

    def __init__(self, package, atgenerator):
        self.package = package
        self.atgenerator = atgenerator
        self.__dict__.update(atgenerator.__dict__)

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

        # we do not create the Extension directory here any longer, since
        # it is just used by workflow scripts (we aim to get
        # rid of them too), so we create it jit when scripts are generated.
        extDir = os.path.join(self.package.getFilePath(), 'Extensions')
        profileDir = os.path.join(self.package.getFilePath(),
                                  'profiles', 'default')
        self.atgenerator.makeDir(profileDir)
        workflowDir = os.path.join(profileDir, 'workflows')
        self.atgenerator.makeDir(workflowDir)

        for sm in statemachines:
            d['statemachine'] = sm
            d['info'] = WorkflowInfo(sm, self)
            
            # start BBB warning 
            smName = utils.cleanName(sm.getName())
            smDir = os.path.join(workflowDir, smName)
            oldFile = os.path.join(extDir, smName + '.py')
            if os.path.exists(oldFile):
                log.warn('Workflow now uses generic setup, please '
                         'remove %s.', oldFile)
            # end BBB warning 
            
            self.atgenerator.makeDir(smDir)
            log.debug("Generated specific workflow's dir '%s'.",
                      smDir)
            
            # Generate workflow xml
            log.info("Generating workflow '%s'.", smName)
            templ = self.readTemplate(['profiles', 'definition.xml'])
            scriptpath = os.path.join(smDir, 'definition.xml')
            dtml = HTML(templ, d)
            res = dtml()
            of = self.atgenerator.makeFile(scriptpath)
            of.write(res)
            of.close()

            self._collectSubscribers(sm)
            
        # generate wfsubscribers.zcml
        self._generateWorkflowSubscribers()
        
        del d['statemachine']
        oldFile = os.path.join(extDir, 'InstallWorkflows.py')
        
        # start BBB warning 
        if os.path.exists(oldFile):
            log.warn('Workflow now uses generic setup, please '
                     'remove %s.', oldFile)
        # end BBB warning 
        
        log.debug("Creating workflows.xml file.")
        d['workflowNames'] = self.workflowNames()
        d['workflowless'] = self.workflowLessTypes()
        d['typeMapping'] = self.typeMapping()
        d['defaultId'] = self.findDefaultWorkflowId()
        templ = self.readTemplate(['profiles', 'workflows.xml'])
        scriptpath = os.path.join(profileDir, 'workflows.xml')
        dtml = HTML(templ, d)
        res = dtml()
        of = self.atgenerator.makeFile(scriptpath)
        of.write(res)
        of.close()

        if len(self.extraRoles()) == 0:
            log.debug("Skipping creation of rolemap.xml file.")
            return
        log.debug("Creating rolemap.xml file.")
        d['extraRoles'] = self.extraRoles()
        templ = self.readTemplate(['profiles', 'rolemap.xml'])
        scriptpath = os.path.join(profileDir, 'rolemap.xml')
        dtml = HTML(templ, d)
        res = dtml()
        of = self.atgenerator.makeFile(scriptpath)
        of.write(res)
        of.close()
        
    def _generateWorkflowSubscribers(self):
        product = self.package.getProduct()
        subscribers = product.getAnnotation('subscribers', None)
        modulepath = os.path.join(product.getFilePath(), 'wfsubscribers.py')
        if not subscribers:
            log.debug('No workflow subscribers in this product.')
            if os.path.exists(modulepath):
                log.warn('superfluos wfsubscribers.py left, no longer used.')
            return
        product = self.package.getProduct()
        if os.path.exists(modulepath):
            parsedModule = PyModule(modulepath)
        else:
            parsedModule = PyModule('', mode='string')
        templ = self.readTemplate(['wfsubscribers.py'])
        d = {
            'generator': self,
            'package': self.package,
            'subscribers': subscribers,
            'parsed_module': parsedModule,
            'builtins': __builtins__,
            'utils': utils,
        }
        d.update(__builtins__)
        res = HTML(templ, d)()
        of = self.atgenerator.makeFile(modulepath)
        of.write(res)
        of.close()
        return res        
    
    def _collectSubscribers(self, sm):
        """collect info for workflow transition subscribers"""
        product = self.package.getProduct()
        subscribers = product.getAnnotation('subscribers', dict())
        effects = self._effects(sm)
        for info in effects:
            id = self._infoid(info)
            if id in subscribers.keys():
                continue
            log.debug('Workflow subscriber added for %s' % sm.getCleanName())
            
            subscribers[id] = {}
            subscribers[id]['type'] = 'workflow'
            subscribers[id]['payload'] = info
            subscribers[id]['for'] = [
                info['objinterface'],
                info['wfinterface'],
            ]                
            subscribers[id]['method'] = self._infoid(info, short=True)
            subscribers[id]['handler'] = id
        product.annotate('subscribers', subscribers)

        
    def _effects(self, sm):
        """ subscriber info"""
        effects = []        
        for transition in sm.getTransitions(self):
            before = transition.getBeforeActionName()
            after = transition.getAfterActionName()                
            if before:
                effects.append(self._transEffectInfo(transition, 'before'))
            if after:
                effects.append(self._transEffectInfo(transition, 'after'))  
        return effects

    def _transEffectInfo(self, transition, type):
        res = {}
        action = transition.getAction()
        res['sourcestate'] = transition.getSourceState()
        res['targetstate'] = transition.getTargetState()
        res['transition'] = transition.getName()
        res['workflow'] = transition.getParent().getCleanName()
        if type == 'before':
            res['effectname'] = action.getBeforeActionName()
            res['wfinterface'] = 'Products.DCWorkflow.interfaces.IBeforeTransitionEvent'
        else:
            res['effectname'] = action.getAfterActionName()
            res['wfinterface'] = 'Products.DCWorkflow.interfaces.IAfterTransitionEvent'
        klass = res['sourcestate'].getParent().getParent()
        if klass.hasStereoType(self.atgenerator.noncontentstereotype,
                               umlprofile=self.atgenerator.uml_profile):
            defaultbinding = '*'
        else:
            # take the generated marker interface as defaultbinding
            path = klass.getQualifiedModuleName(klass.getPackage(), 
                                               includeRoot=0)
            rdot = path.rfind('.')
            if rdot >= 0:
                path = '.' + path[:rdot+1]
            else:
                path = '.'
            defaultbinding = '%sinterfaces.I%s' % (path, klass.getCleanName())
        tag = '%s:binding' % type
        print tag
        res['objinterface'] = action.getTaggedValue(tag, defaultbinding)
        return res
    
    def _infoid(self, info, short=False):
        base = info['effectname']
        if not short:
            base = '.wfsubscribers.' + base
        return base
        
    def workflowNames(self):
        statemachines = self.package.getStateMachines()
        names = [utils.cleanName(sm.getName()) for sm in
                 statemachines]
        names.sort()
        return names

    def workflowLessTypes(self):
        """Return workflow-less types (like tools).
        """

        tools = [c.getName() for c in
                 self.atgenerator.getGeneratedTools(self.package)
                 if not
                 utils.isTGVFalse(c.getTaggedValue('autoinstall'))]
        tools.sort()
        return tools

    def typeMapping(self):
        """Return list of {id, workflowId} dicts.
        """

        statemachines = self.package.getStateMachines()
        classes = {}
        for sm in statemachines:
            workflowId = sm.getCleanName()
            for klass in sm.getClasses():
                if not self.atgenerator._isContentClass(klass):
                    continue
                name = klass.getCleanName()
                classes[name] = workflowId
        classNames = classes.keys()
        classNames.sort()
        result = []
        for id_ in classNames:
            item = {}
            item['id'] = id_ # portal type
            item['workflowId'] = classes[id_]
            result.append(item)
            
        # remember special case
        remembertypes = []
        self.atgenerator.getRememberTypes(remembertypes, self.package)
        for remembertype in remembertypes:
            existent = False
            for type in result:
                if type['id'] == remembertype['portal_type']:
                    existent = True
            if existent:
                continue
            additionaltype = dict()
            additionaltype['id'] = remembertype['portal_type']
            additionaltype['workflowId'] = remembertype['workflow']
            result.append(additionaltype)
            
        # take tgv on state maschine itself into account
        for sm in statemachines:
            bindings = sm.getTaggedValue('bindings', '')
            bindings = [b.strip() for b in bindings.split(', ') if b.strip()]
            for binding in bindings:
                item = {}
                item['id'] = binding
                item['workflowId'] = sm.getCleanName()
                result.append(item)
        
        return result

    def extraRoles(self):
        statemachines = self.package.getStateMachines()
        extra = []
        for sm in statemachines:
            unknown = sm.getAllRoles(
                ignore=['Owner',
                        'Manager',
                        'Member',
                        'Reviewer',
                        'Authenticated',
                        'Anonymous',
                        'Contributor',
                        'Editor',
                        'Reader'])
            for item in unknown:
                if item not in extra:
                    extra.append(item)
        extra.sort()
        return extra

    def findDefaultWorkflowId(self):
        statemachines = self.package.getStateMachines()
        for sm in statemachines:
            if utils.isTGVTrue(sm.getTaggedValue('default', '0')):
                return sm.getCleanName()
        return None

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

class WorkflowInfo(object):
    """View-like utility class.
    """

    def __init__(self, sm, generator):
        self.sm = sm # state machine.
        self.generator = generator
    
    @property
    def id(self):
        return self.sm.getCleanName()

    @property
    def initialstate(self):
        return self.sm.getInitialState().getName()

    @property
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

    @property
    def transitions(self):
        transitions = self.sm.getTransitions(no_duplicates = 1)
        filtered = [t for t in transitions if t.getName()]
        filtered.sort(cmp=lambda x,y: cmp(x.getName(), y.getName()))
        for tr in filtered:
            guardPermissions = tr.getGuardPermissions()
            guardRoles = tr.getGuardRoles()
            guardExpr = tr.getGuardExpr()
            if guardPermissions:
                perms = guardPermissions.split(';')
            else:
                perms = []
            perms = [p.strip() for p in perms]
            tr.guardPermissions = perms
            if guardRoles:
                roles = guardRoles.split(';')
            else:
                roles = []
            roles = [p.strip() for p in roles]
            tr.guardRoles = roles
            tr.guardExpression = guardExpr
        return filtered

    @property
    def worklists(self):
        names = self.sm.getAllWorklistNames()
        worklists = []
        for name in names:
            wl = {}
            wl['id'] = name
            worklistStates = self.sm.getWorklistStateNames(name)
            url = ("%(portal_url)s/search?review_state=" +
                   "&review_state=".join(worklistStates))
            wl['url'] = url
            wl['guardPermission'] = self.sm.getWorklistGuardPermission(name)
            wl['guardRole'] = self.sm.getWorklistGuardRole(name)
            wl['states'] = worklistStates
            worklists.append(wl)
        return worklists


TODO = """

  <!--<dtml-var "_['sequence-item']['description']">-->

    worklistStates = <dtml-var "repr(worklistStateNames)">
                   'var_match_review_state': ';'.join(worklistStates)})
</dtml-let>
</dtml-let>
</dtml-in>



in rolemap.xml: extra permissions like this

  <!--
  <permissions>
    <permission name="Access inactive portal content"
                acquire="True">
      <role name="Owner"/>
    </permission>
  </permissions>
  -->


"""
