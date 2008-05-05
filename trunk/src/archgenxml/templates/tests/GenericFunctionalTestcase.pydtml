<dtml-let assocs="klass.getFromAssociations(aggtypes=['none','aggregation','composite'])"
          atts="klass.getAttributeDefs()"
          dependentImports="generator.generateDependentImports(klass)"
          additionalImports="generator.generateAdditionalImports(klass)"
          taggedImports="generator.getImportsByTaggedValues(klass)"
          vars="atts+[a.toEnd for a in assocs]">
<dtml-if taggedImports><dtml-var taggedImports></dtml-if>
<dtml-if dependentImports><dtml-var dependentImports></dtml-if>
<dtml-if additionalImports><dtml-var additionalImports></dtml-if>
import os, sys

<dtml-var "generator.getProtectedSection(parsed_class, 'module-header')">
#
# Test-cases for class(es) <dtml-var "', '.join([p.getName() for p in klass.getRealizationParents()])">
#

from mechanize import LinkNotFoundError
from Products.Five.testbrowser import Browser
from Products.<dtml-var "klass.getPackage().getProductName()">.config import *

# Import the tested classes
<dtml-in "klass.getRealizationParents() + klass.getClientDependencyClasses(includeParents=True)">
from <dtml-var "_['sequence-item'].getQualifiedModuleName(None, forcePluginRoot=1)"> import <dtml-var "_['sequence-item'].getCleanName()">
</dtml-in>

<dtml-var "generator.getProtectedSection(parsed_class, 'module-beforeclass')">


<dtml-let base_class="klass.getTaggedValue('base_class') or ','.join([p.getCleanName() for p in klass.getGenParents()])">
class <dtml-var "klass.getCleanName()"><dtml-if base_class>(<dtml-var base_class>)</dtml-if>:
</dtml-let>
    """<dtml-var "utils.indent(klass.getDocumentation(), 1, skipFirstRow=True, stripBlank=True)">
    """
<dtml-var "generator.generateImplements(klass,[p.getCleanName() for p in klass.getGenParents()])">
<dtml-var "generator.getProtectedSection(parsed_class,'class-header_'+klass.getCleanName(),1)">
<dtml-if "not parsed_class or '__init__' not in parsed_class.methods.keys()">
<dtml-if vars>

    def __init__(self,*args,**kwargs):
<dtml-in "klass.getGenParents()">
        <dtml-var "_['sequence-item'].getCleanName()">.__init__(self,*args,**kwargs)
</dtml-in>
        self._init_attributes(*args,**kwargs)
</dtml-if>
<dtml-else>

<dtml-var "parsed_class.methods['__init__'].getSrc()">
</dtml-if>
<dtml-if vars>

    def _init_attributes(self,*args,**kwargs):
<dtml-if atts>
        #attributes
</dtml-if>
<dtml-in atts>
<dtml-if "_['sequence-item'].mult[1]==1">
        self.<dtml-var "_['sequence-item'].getCleanName()">=None
<dtml-else>
        self.<dtml-var "_['sequence-item'].getCleanName()">=<dtml-var "{None:'[]','dict':'{}','list':'[]','tuple':'()'}.get(_['sequence-item'].getStereoType(),str(_['sequence-item'].getStereoType())+'()')">
</dtml-if>
</dtml-in>
<dtml-if assocs>
        #associations
</dtml-if>
<dtml-in assocs>
<dtml-if "_['sequence-item'].toEnd.getUpperBound()==1">
        self.<dtml-var "_['sequence-item'].toEnd.getCleanName()">=None
<dtml-else>
        self.<dtml-var "_['sequence-item'].toEnd.getCleanName()">=<dtml-var "{None:'[]','dict':'{}','list':'[]','tuple':'()'}.get(_['sequence-item'].getStereoType(),str(_['sequence-item'].getStereoType())+'()')">
</dtml-if>
</dtml-in>
        # automatically set attributes where mutators exist
        for key in kwargs.keys():
            # camel case: variable -> setVariable
            mutatorName = 'set'+key[0].upper()+key[1:]
            mutator = getattr(self, mutatorName)
            if mutator is not None and callable(mutator):
                mutator(kwargs[key])
</dtml-if>

<dtml-comment>
    #################################################################
    ##########         Begin UML method generation         ##########
    #################################################################
</dtml-comment>

<dtml-in "generator.getMethodsToGenerate(klass)[0]">

<dtml-let m="_['sequence-item']" mn="m.getCleanName()">
<dtml-if "m.getParent() != klass">
    # from class <dtml-var "m.getParent().getName()">:
</dtml-if>
<dtml-if "parsed_class and mn in parsed_class.methods.keys()">
<dtml-var "parsed_class.methods[mn].getSrc()">
<dtml-else>
    def <dtml-var "mn">(self):
        pass
</dtml-if>
</dtml-let>
</dtml-in>

<dtml-comment>
    #################################################################
    ##########          End UML method generation          ##########
    #################################################################
</dtml-comment>
<dtml-comment>
    #################################################################
    ##########           Begin manual method copy          ##########
    #################################################################
</dtml-comment>
    # Manually created methods
<dtml-if parsed_class>
<dtml-let allmethodnames="[m.getCleanName() for m in generator.getMethodsToGenerate(klass)[0]]">
<dtml-in "parsed_class.methods.values()">
<dtml-if "_['sequence-item'].getName() not in allmethodnames+['afterSetUp', 'getError', 'printError', '_setup', '__init__', '_init_attributes', 'Session']">

<dtml-var "_['sequence-item'].getSrc()"></dtml-if>
</dtml-in>
</dtml-let>
</dtml-if>
<dtml-comment>
    #################################################################
    ##########           End manual method copy            ##########
    #################################################################
</dtml-comment>


<dtml-var "generator.getProtectedSection(parsed_class,'module-footer')"></dtml-let>


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(<dtml-var "klass.getCleanName()">))
    return suite

<dtml-var "generator.getProtectedSection(parsed_class, 'module-footer')">
