<dtml-let infoheader="atgenerator.getHeaderInfo(package)">
"""Workflow: <dtml-var "statemachine.getCleanName()">
"""

# <dtml-var "infoheader['copyright']">
#
# Generator: ArchGenXML Version <dtml-var "infoheader['version']">
#            http://plone.org/products/archgenxml
#
# <dtml-var "infoheader['licence']">
#
__author__    = '''<dtml-var "infoheader['authorline']">'''
__docformat__ = 'plaintext'
__version__   = '$ Revision 0.0 $'[11:-2]
</dtml-let>

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.ExternalMethod.ExternalMethod import ExternalMethod

<dtml-var "generator.getProtectedSection(parsedModule,'create-workflow-module-header')">

productname = '<dtml-var "package.getCleanName()">'

def setup<dtml-var "statemachine.getCleanName()">(self, workflow):
    """Define the <dtml-var "statemachine.getCleanName()"> workflow.
    """
<dtml-let additional_roles="statemachine.getAllRoles(ignore=['Owner','Manager','Member','Reviewer','Authenticated','Anonymous'])">
<dtml-if "additional_roles">
    # add additional roles to portal
    portal = getToolByName(self,'portal_url').getPortalObject()
    data = list(portal.__ac_roles__)
    for role in <dtml-var "additional_roles">:
        if not role in data:
            data.append(role)
    portal.__ac_roles__ = tuple(data)
</dtml-if>
</dtml-let>

    workflow.setProperties(title='<dtml-var "statemachine.getCleanName()">')

<dtml-var "generator.getProtectedSection(parsedModule,'create-workflow-setup-method-header',1)">

    for s in <dtml-var "repr(statemachine.getStateNames(no_duplicates = 1))">:
        workflow.states.addState(s)

    for t in <dtml-var "repr(statemachine.getTransitionNames(no_duplicates = 1))">:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

<dtml-in "generator.getAllPermissionNames(statemachine)">
    workflow.addManagedPermission(<dtml-var "_['sequence-item']">)
</dtml-in>

    for l in <dtml-var "repr(statemachine.getAllWorklistNames())">:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('<dtml-var "statemachine.getInitialState().getName()">')

    ## States initialization

<dtml-in "[s for s in statemachine.getStates(no_duplicates = 1) if s.getName()]">
    stateDef = workflow.states['<dtml-var "_['sequence-item'].getName()">']
    stateDef.setProperties(title="""<dtml-var "_['sequence-item'].getTitle(generator)">""",
                           transitions=<dtml-var "repr([t.getName() for t in _['sequence-item'].getOutgoingTransitions()])">)
<dtml-in "generator.getPermissionsDefinitions(_['sequence-item'])">
    stateDef.setPermission(<dtml-var "_['sequence-item'].get('permission')">,
                           <dtml-var "_['sequence-item'].get('acquisition')">,
                           <dtml-var "_['sequence-item'].get('roles')">)
</dtml-in>

</dtml-in>
    ## Transitions initialization
<dtml-in "[t for t in statemachine.getTransitions(no_duplicates = 1) if t.getName()]">
<dtml-let transition="_['sequence-item']">
<dtml-if "transition.getAction()">

    ##creation of workflow scripts
    for wf_scriptname in <dtml-var "repr(transition.getAction().getUsedActionNames())">:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.<dtml-var "statemachine.getCleanName()">_scripts',
                wf_scriptname))
</dtml-if>

    transitionDef = workflow.transitions['<dtml-var "transition.getName()">']
    transitionDef.setProperties(title="""<dtml-var "transition.getTaggedValue('label') or transition.getName()">""",
                                new_state_id="""<dtml-var "transition.getTargetStateName()">""",
                                trigger_type=<dtml-var "transition.getTriggerType()">,
                                script_name="""<dtml-var "transition.getBeforeActionName() or ''">""",
                                after_script_name="""<dtml-var "transition.getAfterActionName() or ''">""",
                                actbox_name="""<dtml-var "transition.getTaggedValue('label') or transition.getName()">""",<dtml-call name="atgenerator.addMsgid(transition.getTaggedValue('label') or transition.getName())">
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props=<dtml-var "transition.getProps()">,
                                )
</dtml-let>
</dtml-in>

    ## State Variable
    workflow.variables.setStateVar('review_state')

    ## Variables initialization
    variableDef = workflow.variables['review_history']
    variableDef.setProperties(description="""Provides access to workflow history""",
                              default_value="""""",
                              default_expr="""state_change/getHistory""",
                              for_catalog=0,
                              for_status=0,
                              update_always=0,
                              props={'guard_permissions': 'Request review; Review portal content'})

    variableDef = workflow.variables['comments']
    variableDef.setProperties(description="""Comments about the last transition""",
                              default_value="""""",
                              default_expr="""python:state_change.kwargs.get('comment', '')""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['time']
    variableDef.setProperties(description="""Time of the last transition""",
                              default_value="""""",
                              default_expr="""state_change/getDateTime""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['actor']
    variableDef.setProperties(description="""The ID of the user who performed the last transition""",
                              default_value="""""",
                              default_expr="""user/getId""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['action']
    variableDef.setProperties(description="""The last transition""",
                              default_value="""""",
                              default_expr="""transition/getId|nothing""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    ## Worklists Initialization

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

    # WARNING: below protected section is deprecated.
    # Add a tagged value 'worklist' with the worklist name to your state(s) instead.

<dtml-var "generator.getProtectedSection(parsedModule,'create-workflow-setup-method-footer',1)">


def create<dtml-var "statemachine.getCleanName()">(self, id):
    """Create the workflow for <dtml-var "package.getCleanName()">.
    """

    ob = DCWorkflowDefinition(id)
    setup<dtml-var "statemachine.getCleanName()">(self, ob)
    return ob

addWorkflowFactory(create<dtml-var "statemachine.getCleanName()">,
                   id='<dtml-var "statemachine.getCleanName()">',
                   title='<dtml-var "statemachine.getTaggedValue('label') or statemachine.getCleanName()">')

<dtml-var "generator.getProtectedSection(parsedModule,'create-workflow-module-footer')">
