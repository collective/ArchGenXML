from operator import itemgetter
import os.path
import utils
import logging
from PyParser import PyModule
from BaseGenerator import BaseGenerator
from zope.documenttemplate import HTML
from archgenxml.TaggedValueSupport import STATE_PERMISSION_MAPPING
from CodeSectionHandler import handleSectionedFile
from TaggedValueSupport import tgvRegistry
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
        typemapping=self.typeMapping()
        if not statemachines and not typemapping:
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
            d['info'] = WorkflowInfo(sm)
            d['target_version'] = self.getOption('plone_target_version', self.package, 3.0)

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
        handleSectionedFile(['profiles', 'workflows.xml'],
                            os.path.join(profileDir, 'workflows.xml'),
                            sectionnames=['workflowobjects', 
                                          'workflowbindings'],
                            templateparams=d)        

        if len(self.extraRoles()) == 0:
            log.debug("Skipping creation of rolemap.xml file.")
            return
        log.debug("Creating rolemap.xml file.")
        d['extraRoles'] = self.extraRoles()

        handleSectionedFile(['profiles', 'rolemap.xml'],
                            os.path.join(profileDir, 'rolemap.xml'),
                            sectionnames=['roles',
                                          'permissions'],
                            templateparams=d)

    def _generateWorkflowSubscribers(self):
        product = self.package.getProduct()
        subscribers = product.getAnnotation('subscribers', None)
        modulepath = os.path.join(product.getFilePath(), 'wfsubscribers.py')
        if not subscribers:
            log.debug('No workflow subscribers in this product.')
            if os.path.exists(modulepath):
                log.warn('superfluous wfsubscribers.py left, no longer used.')
            return
        product = self.package.getProduct()
        if os.path.exists(modulepath):
            parsedModule = PyModule(modulepath)
        else:
            parsedModule = PyModule('', mode='string')
        templ = self.readTemplate(['wfsubscribers.pydtml'])
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
            id = '%s|%s|%s' % (info['objinterface'], info['wfinterface'],
                                self._infoid(info, short=True))
            if id in subscribers.keys():
                subscribers[id]['transitions'].update([info['transition']])
                continue
            log.debug('Workflow subscriber added for %s' % sm.getCleanName())

            subscribers[id] = {}
            subscribers[id]['type'] = 'workflow'
            subscribers[id]['payload'] = info
            if 'transitions' not in subscribers[id]:
                subscribers[id]['transitions'] = set()
            subscribers[id]['transitions'].update([info['transition']])
            subscribers[id]['for'] = [
                info['objinterface'],
                info['wfinterface'],
            ]
            subscribers[id]['method'] = self._infoid(info, short=True)
            dottedpath = ".wfsubscribers.%s" % (subscribers[id]['method'])
            subscribers[id]['handler'] = dottedpath
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
            path = klass.getQualifiedModuleName(klass.getPackage(), includeRoot=1)
            if path.startswith(self.package.getProduct().getName()):
                # strip product name - shouldnt be in there, xmiparser is here
                # a bit buggy :-(
                path = path[len(self.package.getProduct().getName()):]
            rdot = path.rfind('.')
            if rdot > 0:
                path = '.' + path[:rdot+1]
            else:
                path = '.'
            defaultbinding = '%sinterfaces.I%s' % (path, klass.getCleanName())
        tag = '%s:binding' % type
        res['objinterface'] = action.getTaggedValue(tag, defaultbinding)
        return res

    def _infoid(self, info, short=False):
        base = info['effectname']
        if not short:
            base = '.wfsubscribers.' + base
        return base

    def workflowNames(self):
        statemachines = self.package.getStateMachines()
        workflows = [(utils.cleanName(sm.getName()),
                      sm.getTaggedValue('meta_type', 'Workflow'))
                     for sm in statemachines]
        workflows.sort()
        
        result = []
        for name, meta_type in workflows:
            item = {}
            item['name'] = name
            item['meta_type'] = meta_type
            result.append(item)
        
        return result

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
                # We allow to bound a workflow to a <<stub>>
                if not self.atgenerator._isContentClass(klass) and \
                   not klass.hasStereoType(self.atgenerator.stub_stereotypes):
                    continue
                name = klass.getTaggedValue('portal_type') or \
                       klass.getCleanName()
                classes[name] = workflowId

        classNames = classes.keys()
        classNames.sort()
        result = []
        for id_ in classNames:
            item = {}
            item['id'] = id_ # portal type
            item['workflowId'] = classes[id_]
            result.append(item)

        # no need to check use_workflow, it's already done by xmiparser.XMIModel.associateClassesToStateMachines,
        # so the sm.getClasses() already returns classes which uses use_workflow tgv.
        # if you uncomment thoses lines, you will have the bound-workflow twice
        #handle the use_workflow tgvs
        #for klass in self.package.getProduct().getClasses(recursive=True):
        #    if klass.hasTaggedValue('use_workflow'):
        #        result.append(dict(id=klass.getCleanName(),workflowId=klass.getTaggedValue('use_workflow')))
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
            wi = WorkflowInfo(sm)
            unknown = wi.allRoles(
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

    def getPermissionsDefinitions(self, state):
        stateadapter = StateInfo(state)
        return stateadapter.permissionsDefinitions

    def getAllPermissionNames(self, statemachine):
        wi = WorkflowInfo
        source_pdefs = statemachine.getAllPermissionNames()
        result_pdefs = [self.processExpression(pdef, asString=False)
                        for pdef in source_pdefs]
        return result_pdefs

class WorkflowInfo(object):
    """View-like utility class.
    """

    striphtml = 0

    def __init__(self, sm, striphtml=0):
        self.sm = sm # state machine.

    @property
    def id(self):
        return self.sm.getCleanName()

    @property
    def state_var(self):
        return self.sm.getTaggedValue('state_var', 'review_state')

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
            state['title'] = item.getTitle(striphtml=self.striphtml)
            state['description'] = item.getDescription()
            state['exit-transitions'] = [t.getName() for t in
                                         item.getOutgoingTransitions()]
            si = StateInfo(item)
            perms = si.permissionsDefinitions
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
        names = self._getAllWorklistNames()
        worklists = []
        for name in names:
            wl = {}
            wl['id'] = name
            worklistStates = self._getWorklistStateNames(name)
            url = ("%(portal_url)s/search?review_state=" +
                   "&amp;review_state=".join(worklistStates))
            wl['url'] = url
            wl['guardPermission'] = self._getWorklistGuardPermission(name)
            wl['guardRoles'] = self._getWorklistGuardRoles(name)
            wl['guardExpression'] = self._getWorklistGuardExpression(name)
            wl['states'] = "; ".join(worklistStates)
            worklists.append(wl)
        return worklists

    @property
    def permissionNames(self):
        ret = []
        for state in self.sm.getStates():
            si = StateInfo(state)
            pd = si.permissionsDefinitions
            for pdef in pd:
                perm = pdef['permission'].strip()

                if perm not in ret:
                    ret.append(str(perm))
        return ret

    def allRoles(self, ignore=[]):
        roles = []
        # Reserved name to set the title
        ignore.append('label')
        for tran in self.sm.getTransitions(no_duplicates=1):
            dummy = [roles.append(r.strip()) \
                     for r in tran.getGuardRoles().split(';') \
                     if not (r.strip() in roles or r.strip() in ignore)]

        for state in self.sm.getStates():
            si = StateInfo(state)
            perms = si.permissionsDefinitions
            sroles = []
            dummy = [[sroles.append(j) for j in i] \
                     for i in [d['roles'] for d in perms] \
                    ]
            dummy = [roles.append(r.strip()) \
                     for r in sroles \
                     if not (r.strip() in roles or r.strip() in ignore)]

        return [r for r in roles if r]

    def _getAllWorklistNames(self):
        """Return all worklists mentioned in this statemachine.

        A worklist is mentioned by adding a tagged value 'worklist' to a state.
        """
        log.debug("Finding all worklists mentioned in this statemachine.")
        worklists = {}
        names = [s.getTaggedValue('worklist')
                 for s in self.sm.getStates(no_duplicates = 1)
                 if s.getTaggedValue('worklist')]
        for name in names:
            worklists[name] = 'just filtering out doubles'
        result = worklists.keys()
        log.debug("Found the following worklists: %r.", result)
        return result

    def _getWorklistStateNames(self, worklistname):
        """Returns the states associated with the worklistname."""
        results = [s.getName()
                   for s in self.sm.getStates(no_duplicates = 1)
                   if s.getTaggedValue('worklist') == worklistname]
        log.debug("Associated with worklist '%s' are the "
                  "following states: %r.", worklistname, results)
        return results

    def _getWorklistGuardRoles(self, worklistname):
        """Returns the guard roles associated with the worklistname."""
        log.debug("Getting the guard roles for the worklist...")
        default = ''
        results = [s.getTaggedValue('worklist:guard_roles')
                   for s in self.sm.getStates(no_duplicates = 1)
                   if s.getTaggedValue('worklist') == worklistname
                   and s.getTaggedValue('worklist:guard_roles')]
        if not results:
            log.debug("No tagged value found, returning the default: '%s'.",
                      default)
            return default
        guardRoles = results[0]
        log.debug("Tagged value(s) found, taking the first (or only) "
                  "one: '%s'.", guardRoles)
        if guardRoles:
            guardRoles = guardRoles.replace(';', ',')
            guardRoles = guardRoles.split(',')
        else:
            guardRoles = []
        return [p.strip() for p in guardRoles]

    def _getWorklistGuardPermission(self, worklistname):
        """Returns the guard permission associated with the worklistname."""
        log.debug("Getting the guard permission for the worklist...")
        default = 'Review portal content' #XXX odd convention
        results = [s.getTaggedValue('worklist:guard_permissions')
                   for s in self.sm.getStates(no_duplicates = 1)
                   if s.getTaggedValue('worklist') == worklistname
                   and s.getTaggedValue('worklist:guard_permissions')]
        if not results:
            log.debug("No tagged value found, returning the default: '%s'.",
                      default)
            return default
        # There might be more than one guard_permissions tgv, take the first
        result = results[0]
        log.debug("Tagged value(s) found, taking the first (or only) one: '%s'.",
                  result)
        if utils.isTGVFalse(result):
            return None
        return result

    def _getWorklistGuardExpression(self, worklistname):
        """Returns the guard expression associated with the worklistname."""
        log.debug("Getting the guard expression for the worklist...")
        default = ''
        results = [s.getTaggedValue('worklist:guard_expressions')
                   for s in self.sm.getStates(no_duplicates = 1)
                   if s.getTaggedValue('worklist') == worklistname
                   and s.getTaggedValue('worklist:guard_expressions')]
        if not results:
            log.debug("No tagged value found, returning the default: '%s'.",
                      default)
            return default
        # There might be more than one guard_expressions tgv, take the first
        log.debug("Tagged value(s) found, taking the first (or only) one: '%s'.",
                  results[0])
        return results[0]


class StateInfo(object):
    """adapter like objetc on a state to fetch information from it"""

    non_permissions = [
        'initial_state', 'documentation',
        'label', 'description', 'worklist',
        'worklist:guard_permissions',
        'worklist:guard_roles',
        'worklist:guard_expressions',
    ]

    def __init__(self, state):
        self.state = state

    @property
    def permissionsDefinitions(self):
        """ return a list of dictionaries with permission definitions

        Each dict contains a key 'permission' with a string value and
        a key 'roles' with a list of strings as value and a key
        'acquisition' with value 1 or 0.
        """

        ### for the records:
        ### this method contains lots of generation logic. in fact this
        ### should move over to the WorkflowGenerator.py and reduce here in
        ### just deliver the pure data
        ### the parser should really just parse to be as independent as possible

        # permissions_mapping (abbreviations for lazy guys)
        # keys are case insensitive

        # STATE_PERMISSION_MAPPING in TaggedValueSupport.py now
        # contains the handy mappings from 'access' to 'Access contents
        # information' and so.

        state = self.state
        tagged_values = state.getTaggedValues()
        permission_definitions = []

        for tag_name, tag_value in tagged_values.items():
            # list of tagged values that are NOT permissions
            if tag_name in self.non_permissions:
                # short check if its registered, registry complains in log.
                tgvRegistry.isRegistered(tag_name, state.classcategory,
                                         silent=True)
                continue
            tag_name = tag_name.strip()

            # look up abbreviations if any
            permission = STATE_PERMISSION_MAPPING.get(tag_name.lower(),
                                                      tag_name or '')

            if not tag_value:
                log.debug("Empty tag value, treating it as a reset "
                          "for acquisition, so acquisition=0.")
                permission_definitions.append({'permission' : permission,
                                               'roles' : [],
                                               'acquisition' : 0})
                continue

            # split roles-string into list
            raw_roles = tag_value.replace(';', ',')
            roles = [str(r.strip()) for r in raw_roles.split(',') if r.strip()]

            # verify if this permission is acquired
            nv = 'acquire'
            acquisition = 0
            if nv in roles:
                acquisition = 1
                roles.remove(nv)

            permission = utils.processExpression(permission, asString=False)
            permission_definitions.append(
                        {'permission' : permission,
                         'roles' : roles,
                         'acquisition' : acquisition}
            )

        # If View was defined but Access was not defined, the Access
        # permission should be generated with the same rights defined
        # for View

        has_access = 0
        has_view = 0
        view = {}
        for permission_definition in permission_definitions:
            if (permission_definition.get('permission', None) ==
                STATE_PERMISSION_MAPPING['access']):
                has_access = 1
            if (permission_definition.get('permission', None) ==
                STATE_PERMISSION_MAPPING['view']):
                view = permission_definition
                has_view = 1
        if has_view and not has_access:
            permission = STATE_PERMISSION_MAPPING['access']
            permission_definitions.append({'permission': permission,
                                           'roles': view['roles'],
                                           'acquisition': view['acquisition']})
        return permission_definitions



TODO = """

  <!--<dtml-var "_['sequence-item']['description']">-->

    worklistStates = <dtml-var "repr(worklistStateNames)">
                   'var_match_review_state': ';'.join(worklistStates)})
</dtml-let>
</dtml-let>
</dtml-in>




"""
