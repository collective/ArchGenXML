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
from TaggedValueSupport import * # includes tgvRegistry
from xmiparser.xmiparser import XMIElement


class TestTaggedValueRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = tgvRegistry # from TaggedValueSupport

    def test_init(self):
        """ Init should create an empty registry
        """
        localRegistry = TaggedValueRegistry()
        self.assertEquals(len(localRegistry._registry), 0)

    def test_addTaggedValue1(self):
        """ Add a simple value, should be placed in the registry
        """
        self.registry.addTaggedValue(category='class', tagname='testtgv')
        self.assertEquals(True,
                          self.registry.isRegistered(category='class',
                                                     tagname='testtgv'))

    def test_addTaggedValue2(self):
        """ Add two categories, should both be present
        """
        self.registry.addTaggedValue(category='class', tagname='testclasstgv')
        self.registry.addTaggedValue(category='method', tagname='testmethodtgv')
        self.registry.addTaggedValue(category='method', tagname='testmethodtgv2')
        self.assertEquals(True,
                          self.registry.isRegistered(category='class',
                                                     tagname='testclasstgv'))
        self.assertEquals(True,
                          self.registry.isRegistered(category='method',
                                                     tagname='testmethodtgv'))
        self.assertEquals(True,
                          self.registry.isRegistered(category='method',
                                                     tagname='testmethodtgv2'))
    def test_isRegistered(self):
        """ Return False for unregistered value
        """
        self.assertEquals(False,
                          self.registry.isRegistered(category='bogus',
                                                     tagname='beer'))

    def test_isRegistered2(self):
        """ Return True, also with missing category.
        """

        self.registry.addTaggedValue(category='class', tagname='testclasstgv')
        self.assertEquals(True,
                          self.registry.isRegistered(tagname='testclasstgv'))
        self.assertEquals(False,
                          self.registry.isRegistered(tagname='oliebollen'))

    def test_isRegistered3(self):
        """Check special widget: tgvs
        """

        self.registry.addTaggedValue(category='attribute', tagname='testclasstgv')
        self.assertEquals(True,
                          self.registry.isRegistered(tagname='widget:something',
                                                     category='attribute'))

    def test_stuffAddedInTheFileWorks(self):
        """ The registering of TGVs at the end of the file should work
        """
        self.assertEquals(True,
                          self.registry.isRegistered(category='class',
                                                     tagname='archetype_name'))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTaggedValueRegistry))
    return suite

if __name__ == '__main__':
    unittest.main()
