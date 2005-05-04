<dtml-var "generator.getProtectedSection(parsed_class, 'module-header')">
#
# test-cases for class(es) <dtml-var "', '.join([p.getName() for p in klass.getRealizationParents()])">
#
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
from Testing import ZopeTestCase
<dtml-if "parent is not None">
from Products.<dtml-var "klass.getPackage().getProductName()">.<dtml-var "parent.getQualifiedModuleName(klass.getPackage())"> import <dtml-var "parent.getCleanName()">
</dtml-if>
# import the tested classes
<dtml-in "klass.getRealizationParents() + klass.getClientDependencyClasses(includeParents=True)">
from <dtml-var "_['sequence-item'].getQualifiedModuleName(klass.getPackage(), forcePluginRoot=1)"> import <dtml-var "_['sequence-item'].getCleanName()">
</dtml-in>

class <dtml-var "klass.getCleanName()"><dtml-if parent>(<dtml-var "parent.getCleanName()">)</dtml-if>:
    """ test-cases for class(es) <dtml-var "', '.join([p.getName() for p in klass.getRealizationParents()])">
    """
<dtml-var "generator.getProtectedSection(parsed_class, 'class-header_'+klass.getCleanName(), 1)">
    def afterSetUp(self):
        pass

<dtml-in "generator.getMethodsToGenerate(klass)[0]">
<dtml-let m="_['sequence-item']" mn="m.testmethodName()">
<dtml-if "m.getParent() != klass"> 
    # from class <dtml-var "m.getParent().getName()">:
</dtml-if>
<dtml-if "parsed_class and mn in parsed_class.methods.keys()">
<dtml-var "parsed_class.methods[mn].getSrc()">
 
<dtml-else>
    def <dtml-var "mn">(self):
<dtml-let name="'temp_'+m.getParent().getCleanName()">
        ''' '''
        #Uncomment one of the following lines as needed
        ##self.loginAsPortalOwner()
        <dtml-if "m.getParent() != klass">
        
        ##o=<dtml-var "m.getParent().getCleanName()">('<dtml-var name>')
        ##self.folder._setObject('<dtml-var name>', o)
        </dtml-if>
        
        pass
        
</dtml-let>
</dtml-if>
</dtml-let>
</dtml-in>
    
    # Manually created methods
<dtml-if parsed_class>
<dtml-in "parsed_class.methods.values()">
<dtml-let allmethodnames="[m.testmethodName() for m in generator.getMethodsToGenerate(klass)[0]]">
<dtml-if "_['sequence-item'].getName() not in allmethodnames+['afterSetUp']">
<dtml-var "_['sequence-item'].getSrc()">
</dtml-if>
</dtml-let>
</dtml-in>
</dtml-if>

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(<dtml-var "klass.getCleanName()">))
    return suite

if __name__ == '__main__':
    framework()

<dtml-var "generator.getProtectedSection(parsed_class, 'module-footer')">
