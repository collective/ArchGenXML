<dtml-let infoheader="atgenerator.getHeaderInfo(package)">
""" Workflow: <dtml-var "statemachine.getCleanName()"> """

# <dtml-var "infoheader['copyright']">
#
<dtml-var "infoheader['date']"># Generator: ArchGenXML Version <dtml-var "infoheader['version']">
#            http://sf.net/projects/archetypes/
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

def setup<dtml-var "statemachine.getCleanName()">(self, wf):
    """
    <dtml-var "statemachine.getCleanName()"> Workflow Definition
    """
<dtml-let additional_roles="statemachine.getAllRoles(ignore=['Owner','Manager','Member','Reviewer','Authenticated','Anonymous'])">
<dtml-if "additional_roles">
    # add additional roles to portal
    portal=getToolByName(self,'portal_url').getPortalObject()
    data=list(portal.__ac_roles__)
    for role in <dtml-var "additional_roles">:
        if not role in self.__ac_roles__:
            data.append(role)
    portal.__ac_roles__=tuple(data)
</dtml-if>
</dtml-let>

    wf.setProperties(title='<dtml-var "statemachine.getCleanName()">')

<dtml-var "generator.getProtectedSection(parsedModule,'create-workflow-setup-method-header',1)">

    # generation of worklists is not defined yet...
    ### XXX :-(

    for s in <dtml-var "repr(statemachine.getStateNames(no_duplicates = 1))">:
        wf.states.addState(s)

    for t in <dtml-var "repr(statemachine.getTransitionNames(no_duplicates = 1))">:
        wf.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        wf.variables.addVariable(v)

    for p in <dtml-var "repr(statemachine.getAllPermissionNames())">:
        wf.addManagedPermission(p)

    ## Initial State

    wf.states.setInitialState('<dtml-var "statemachine.getInitialState().getName()">')

    ## States initialization

<dtml-in "[s for s in statemachine.getStates(no_duplicates = 1) if s.getName()]">
    sdef = wf.states['<dtml-var "_['sequence-item'].getName()">']
    sdef.setProperties(title="""<dtml-var "_['sequence-item'].getDocumentation(striphtml=generator.atgenerator.striphtml) or _['sequence-item'].getName()">""",
                       transitions=<dtml-var "repr([t.getName() for t in _['sequence-item'].getOutgoingTransitions()])">)
<dtml-in "_['sequence-item'].getPermissionsDefinitions()">
    sdef.setPermission('<dtml-var "_['sequence-item'].get('permission')">', 0, <dtml-var "_['sequence-item'].get('roles')">)
</dtml-in>

</dtml-in>
    ## Transitions initialization
<dtml-in "[t for t in statemachine.getTransitions(no_duplicates = 1) if t.getName()]">
    <dtml-let tran="_['sequence-item']">
    <dtml-if "tran.getAction()">

    ##creation of workflow scripts
    for wf_scriptname in <dtml-var "repr(tran.getAction().getSplittedName(padding=0))">:
        if not wf_scriptname in wf.scripts.objectIds():
            wf.scripts._setObject(wf_scriptname,ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.<dtml-var "statemachine.getCleanName()">_scripts',
                wf_scriptname))
    </dtml-if>

    tdef = wf.transitions['<dtml-var "tran.getName()">']
    tdef.setProperties(title="""<dtml-var "tran.getTaggedValue('label') or tran.getName()">""",
                       new_state_id="""<dtml-var "tran.getTargetStateName()">""",
                       trigger_type=<dtml-var "tran.getTriggerType()">,
                       script_name="""<dtml-var "tran.getBeforeActionName() or ''">""",
                       after_script_name="""<dtml-var "tran.getAfterActionName() or ''">""",
                       actbox_name="""<dtml-var "tran.getTaggedValue('label') or tran.getName()">""",<dtml-call name="atgenerator.addMsgid(tran.getTaggedValue('label') or tran.getName())">
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props=<dtml-var "tran.getProps()">,
                       )
</dtml-let></dtml-in>

    ## State Variable
    wf.variables.setStateVar('review_state')

    ## Variables initialization
    vdef = wf.variables['review_history']
    vdef.setProperties(description="""Provides access to workflow history""",
                       default_value="""""",
                       default_expr="""state_change/getHistory""",
                       for_catalog=0,
                       for_status=0,
                       update_always=0,
                       props={'guard_permissions': 'Request review; Review portal content'})

    vdef = wf.variables['comments']
    vdef.setProperties(description="""Comments about the last transition""",
                       default_value="""""",
                       default_expr="""python:state_change.kwargs.get('comment', '')""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['time']
    vdef.setProperties(description="""Time of the last transition""",
                       default_value="""""",
                       default_expr="""state_change/getDateTime""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['actor']
    vdef.setProperties(description="""The ID of the user who performed the last transition""",
                       default_value="""""",
                       default_expr="""user/getId""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['action']
    vdef.setProperties(description="""The last transition""",
                       default_value="""""",
                       default_expr="""transition/getId|nothing""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    # XXX Generation of worklists is not implemented yet...
    # in the meantime, you can use the protected code section below to
    # do it manually

<dtml-var "generator.getProtectedSection(parsedModule,'create-workflow-setup-method-footer',1)">

def create<dtml-var "statemachine.getCleanName()">(self, id):
    "..."
    ob = DCWorkflowDefinition(id)
    setup<dtml-var "statemachine.getCleanName()">(self, ob)
    return ob

addWorkflowFactory(create<dtml-var "statemachine.getCleanName()">,
                   id='<dtml-var "statemachine.getCleanName()">',
                   title='<dtml-var "statemachine.getTaggedValue('label') or statemachine.getCleanName()">')

<dtml-var "generator.getProtectedSection(parsedModule,'create-workflow-module-footer')">
