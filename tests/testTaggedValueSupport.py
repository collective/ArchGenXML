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
        
    def test_IsTGVTrue1(self):
        """ Test if the correct True values are recognised

        1, '1', 'True' and 'true' are all ok.
        """
        for value in [1, '1', 'True', 'true']:
            self.assertEquals(True, isTGVTrue(value))

    def test_IsTGVTrue2(self):
        """ Test if wrong True values are rejected

        1, '1', 'True' and 'true' are all ok.
        """
        for value in ['j', 'y', 'yes', 'ja, meneer']:
            self.assertEquals(False, isTGVTrue(value))

    def test_IsTGVFalse1(self):
        """ Test if the correct False values are recognised

        '0', 0, 'false', 'False' are all ok
        """
        for value in ['0', 0, 'false', 'False']:
            self.assertEquals(True, isTGVFalse(value))

    def test_IsTGVFalse2(self):
        """ Test if wrong False values are rejected

        '0', 0, 'false', 'False' are all ok
        """
        for value in ['n', 'N', 'nyet', -2, 1]:
            self.assertEquals(False, isTGVFalse(value))

    def test_IsTGVFalse3(self):
        """ Test if None is rejected as a False value

        False must be set *explicitly*, so None doesn't qualify.
        """
        self.assertEquals(False, isTGVFalse(None))


class TestTaggedValueRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = TaggedValueRegistry()

    def test_init(self):
        """ Init should create an empty registry
        """
        self.assertEquals(len(self.registry._registry), 0)
        
    def test_addTaggedValue1(self):
        """ Add a simple value, should be placed in the registry
        """
        self.registry.addTaggedValue(category='class', name='testtgv')
        self.assert_(self.registry.isRegisteredTaggedValue(category='class',
                                                           name='testtgv'))

    def test_isRegisteredTaggedValue(self):
        """ Return False 
        """
        self.registry.addTaggedValue(category='class', name='testtgv')
        self.assert_(self.registry.isRegisteredTaggedValue(category='class',
                                                           name='testtgv'))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTaggedValueSupport))
    suite.addTest(unittest.makeSuite(TestTaggedValueRegistry))
    return suite

if __name__ == '__main__':
    unittest.main()
