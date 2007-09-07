<dtml-var "generator.generateModuleInfoHeader(package, name='Install')">
import os.path
import sys
from sets import Set
from StringIO import StringIO
from App.Common import package_home
from Products.CMFCore.utils import getToolByName
from zExceptions import NotFound, BadRequest
from Products.Archetypes.config import TOOL_NAME as ARCHETYPETOOLNAME
from Products.<dtml-var "package.getProductModuleName()">.config import PROJECTNAME
from Products.<dtml-var "package.getProductModuleName()">.config import product_globals


def install(self, reinstall=False):
    """ External Method to install <dtml-var "package.getProductModuleName()"> """
    out = StringIO()
    print >> out, "Installation log of %s:" % PROJECTNAME
    
<dtml-if "package.getProductName() in generator.vocabularymap.keys()">

    # Create vocabularies in vocabulary lib
    from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
    atvm = getToolByName(self, ATVOCABULARYTOOL)
    vocabmap = {<dtml-var "'),\n        '.join( [s[1:] for s in repr(generator.vocabularymap[package.getProductName()]).split(')')] )">}
    for vocabname in vocabmap.keys():
        if not vocabname in atvm.contentIds():
            atvm.invokeFactory(vocabmap[vocabname][0], vocabname)

        if len(atvm[vocabname].contentIds()) < 1:
            if vocabmap[vocabname][0] == "VdexVocabulary":
                vdexpath = os.path.join(
                    package_home(product_globals), 'data', '%s.vdex' % vocabname)
                if not (os.path.exists(vdexpath) and os.path.isfile(vdexpath)):
                    print >>out, 'No VDEX import file provided at %s.' % vdexpath
                    continue
                try:
                    #read data
                    f = open(vdexpath, 'r')
                    data = f.read()
                    f.close()
                except:
                    print >>out, 'Problems while reading VDEX import file provided at %s.' % vdexpath
                    continue
                atvm[vocabname].importXMLBinding(data)
            else:
                pass
</dtml-if>

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

<dtml-let klasses="[(klass.getTaggedValue('portal_type') or klass.getCleanName()) for klass in generator.getGeneratedClasses(package) if utils.isTGVFalse(generator.getOption('searchable_type', klass, True))]">
<dtml-if "klasses">
    # hide selected classes in the search form
    portalProperties = getToolByName(self, 'portal_properties', None)
    if portalProperties is not None:
        siteProperties = getattr(portalProperties, 'site_properties', None)
        if siteProperties is not None and siteProperties.hasProperty('types_not_searched'):
            for klass in <dtml-var "repr(klasses)">:
                current = list(siteProperties.getProperty('types_not_searched'))
                if klass not in current:
                    current.append(klass)
                    siteProperties.manage_changeProperties(**{'types_not_searched' : current})
</dtml-if>
</dtml-let>

<dtml-let klasses="[(klass.getTaggedValue('portal_type') or klass.getCleanName()) for klass in generator.getGeneratedClasses(package) if utils.isTGVFalse(generator.getOption('display_in_navigation', klass, True))]">
<dtml-if "klasses">
    # hide selected classes in the navigation
    portalProperties = getToolByName(self, 'portal_properties', None)
    if portalProperties is not None:
        navtree_properties = getattr(portalProperties, 'navtree_properties', None)
        if navtree_properties is not None and navtree_properties.hasProperty('metaTypesNotToList'):
            for klass in <dtml-var "repr(klasses)">:
                current = list(navtree_properties.getProperty('metaTypesNotToList'))
                if klass not in current:
                    current.append(klass)
                    navtree_properties.manage_changeProperties(**{'metaTypesNotToList' : current})
</dtml-if>
</dtml-let>

    return out.getvalue()

