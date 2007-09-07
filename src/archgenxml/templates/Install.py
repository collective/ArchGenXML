<dtml-var "generator.generateModuleInfoHeader(package, name='Install')">
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.<dtml-var "package.getProductModuleName()">.config import PROJECTNAME

def install(self, reinstall=False):
    """ External Method to install <dtml-var "package.getProductModuleName()"> """
    out = StringIO()
    print >> out, "Installation log of %s:" % PROJECTNAME
    
<dtml-let remembers="[cn for cn in generator.getGeneratedClasses(package) if cn.hasStereoType(generator.remember_stereotype)]">
<dtml-if "remembers"> 
    # Adds our types to MemberDataContainer.allowed_content_types
    types_tool = getToolByName(self, 'portal_types')
    act = types_tool.MemberDataContainer.allowed_content_types
    types_tool.MemberDataContainer.manage_changeProperties(allowed_content_types=act+(<dtml-in remembers>'<dtml-var "_['sequence-item'].getCleanName()">', </dtml-in>))
    # registers with membrane tool ...
    membrane_tool = getToolByName(self, 'membrane_tool')
<dtml-in "remembers">
    membrane_tool.registerMembraneType('<dtml-var "_['sequence-item'].getCleanName()">')
    # print >> out, SetupMember(self, member_type='<dtml-var "_['sequence-item'].getCleanName()">', register=<dtml-var "str(_['sequence-item'].getTaggedValue('register', False))">).finish()
</dtml-in>
</dtml-if>
</dtml-let>

    return out.getvalue()

