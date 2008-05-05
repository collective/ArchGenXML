#
# Interface tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Interface import Implements

from <dtml-var "parent.getQualifiedModuleName(None,forcePluginRoot=1)"> import <dtml-var "parent.getCleanName()">


from Interface.Verify import verifyClass

<dtml-in "klass.getRealizationParents()">
<dtml-let p="_['sequence-item']">

from <dtml-var "p.getQualifiedModuleName(None,forcePluginRoot=1)"> import <dtml-var "p.getCleanName()">

<dtml-in "p.getRealizationParents()">
from <dtml-var "_['sequence-item'].getQualifiedModuleName(klass.getPackage(),forcePluginRoot=1)"> import <dtml-var "_['sequence-item'].getCleanName()">
</dtml-in>


</dtml-let>
</dtml-in>


class <dtml-var "klass.getCleanName()">(<dtml-var "parent.getCleanName()">):
    <dtml-in "klass.getRealizationParents()">
    <dtml-let p="_['sequence-item']">

    def testInterfacesFor<dtml-var "p.getCleanName()">(self):
        '''test interface compliance for class <dtml-var "p.getCleanName()">'''

        <dtml-if "generator.isTGVTrue(klass.getTaggedValue('strict'))">

        for iface in Implements.flattenInterfaces(getattr(<dtml-var "klass.getCleanName()">,'__implements__',[])):
            self.failUnless(verifyClass(iface, <dtml-var "p.getCleanName()">))
        </dtml-if>

    <dtml-in "p.getRealizationParents()">

        self.failUnless(verifyClass(<dtml-var "_['sequence-item'].getCleanName()">, <dtml-var "p.getCleanName()">))
    </dtml-in>

    </dtml-let>
    </dtml-in>

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(<dtml-var "klass.getCleanName()">))
    return suite

if __name__ == '__main__':
    framework()
