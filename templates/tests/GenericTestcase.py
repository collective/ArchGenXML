<dtml-let allmethodnames="['test%s%s'%(m.getParent().getCleanName().capitalize(),m.getCleanName().capitalize()) for m in generator.getMethodsToGenerate(klass)[0]]">
#
# Skeleton test module
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from <dtml-var "parent.getQualifiedModuleName(klass.getPackage())"> import <dtml-var "parent.getCleanName()">
#import the tested classes
<dtml-in "klass.getRealizationParents()">
from <dtml-var "_['sequence-item'].getQualifiedModuleName(klass.getPackage(),forcePluginRoot=1)"> import <dtml-var "_['sequence-item'].getCleanName()">
</dtml-in>

class <dtml-var "klass.getCleanName()">(<dtml-var "parent.getCleanName()">):

    def afterSetUp(self):
        pass


    <dtml-in "generator.getMethodsToGenerate(klass)[0]">
    <dtml-let m="_['sequence-item']" mn="'test%s%s'%(m.getParent().getCleanName().capitalize(),m.getCleanName().capitalize())">
    <dtml-if "m.getParent() != klass"> 
    
    #from Class <dtml-var "m.getParent().getName()">:
    </dtml-if>
    <dtml-if "parsed_class and mn in parsed_class.methods.keys()">

<dtml-var "parsed_class.methods[mn].getSrc()">    
    <dtml-else>

    def <dtml-var "mn">(self,<dtml-var "','.join(m.getParamNames())">):
        <dtml-let name="'temp_'+m.getParent().getCleanName()">
        
        ''' '''
        #o=<dtml-var "m.getParent().getCleanName()">('<dtml-var name>')
        #self.folder.<dtml-var name>=o
        #print self.folder.<dtml-var name>
        
        </dtml-let>
    </dtml-if>
    </dtml-let>
    </dtml-in>
    
    #Manually created methods!!
    <dtml-if parsed_class>
    <dtml-in "parsed_class.methods.values()">
    <dtml-if "_['sequence-item'].getName() not in allmethodnames">
    
<dtml-var "_['sequence-item'].getSrc()">            

    </dtml-if>
    </dtml-in>
    </dtml-if>


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(<dtml-var "klass.getCleanName()">))
    return suite

if __name__ == '__main__':
    framework()

</dtml-let>