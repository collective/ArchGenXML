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
from TaggedValueSupport import *
from XMIParser import XMIElement

class TestTaggedValueSupport(unittest.TestCase):
    def setUp(self):
        self.element = XMIElement()
        self.element.setTaggedValue('boolean1', '1')
        
    def testIsTGVTrue1(self):
        """ Test if the correct True values are recognised

        1, '1', 'True' and 'true' are all ok.
        """
        for value in [1, '1', 'True', 'true']:
            self.assertEquals(True, isTGVTrue(value))

    def testIsTGVTrue2(self):
        """ Test if wrong True values are rejected

        1, '1', 'True' and 'true' are all ok.
        """
        for value in ['j', 'y', 'yes', 'ja, meneer']:
            self.assertEquals(False, isTGVTrue(value))

    def testIsTGVFalse1(self):
        """ Test if the correct False values are recognised

        '0', 0, 'false', 'False' are all ok
        """
        for value in ['0', 0, 'false', 'False']:
            self.assertEquals(True, isTGVFalse(value))

    def testIsTGVFalse2(self):
        """ Test if wrong False values are rejected

        '0', 0, 'false', 'False' are all ok
        """
        for value in ['n', 'N', 'nyet', -2, 1]:
            self.assertEquals(False, isTGVFalse(value))

    def testIsTGVFalse3(self):
        """ Test if None is rejected as a False value

        False must be set *explicitly*, so None doesn't qualify.
        """
        self.assertEquals(False, isTGVFalse(None))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTaggedValueSupport))
    return suite

if __name__ == '__main__':
    unittest.main()
