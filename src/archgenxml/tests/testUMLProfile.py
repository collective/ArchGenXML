""" Tests for the TaggedValueSupport.py file
"""
import os
import sys
import unittest
# Something dirty. It is assumed that ArchGenXML isn't installed as a
# python module but that it resides "just somewhere" on the
# filesystem.
testDir = os.path.dirname(os.path.abspath(__file__))
parentDir = testDir[:-6] # Strips off '/tests'
# Appends the parent dir to the module search path
sys.path.append(parentDir)
from UMLProfile import *
from xmiparser.xmiparser import XMIElement


class TestUMLProfile(unittest.TestCase):
    def setUp(self):
        pass

    def testChainedDict(self):
        a = {'a1': 'a1v',
             'a2': 'a2v'}
        ca = ChainedDict([a], ca1='ca1v', ca2='ca2v')
        self.assertEquals(2, len(ca)) # Hm, I'd expect 4
        self.assertEquals('a1v', ca['a1'])
        self.assertEquals('ca2v', ca['ca2'])

    def testProfile(self):
        baseprofile = UMLProfile()
        baseprofile.addStereoType('python_class', ['XMIClass'])
        baseprofile.addStereoType('portal_type', ['XMIClass'], murf=1)
        baseprofile.addStereoType('view', ['XMIMethod'])
        self.assertEquals(3, len(baseprofile.getAllStereoTypes()))

        archprofile=UMLProfile(baseprofile)
        archprofile.addStereoType('remember', ['XMIClass'])

        self.assert_(archprofile.findStereoTypes(entities=['XMIClass']))
        self.assert_(archprofile.findStereoTypes(entities=['XMIMethod']))
        self.assert_(archprofile.findStereoTypes(entities=['XMIClass'], murf=1))



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUMLProfile))
    return suite

if __name__ == '__main__':
    unittest.main()
