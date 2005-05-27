""" Tests for the PyParser.py file

PyParser is a bit hard to test, as everything depends on the loading
of an initial file by PyModule's '__init__()'. Together with the
testcases' being subclasses of eachother, this results in a lot of
tests which are effectively called a number of times with exactly the
same inputs. Ah well.
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

from utils import *

class TestUtils(unittest.TestCase):
    """ Test the utilities in /utils.py
    """
    def test_indentOneLine(self):
        """ indent a simple string
        """
        result = indent('string', 0)
        self.assertEquals(result, 'string')

    def test_indentDepths(self):
        """ indent a simple string
        """
        result = indent('string', 1)
        self.assertEquals(result, '    string')
        result = indent('string', 2)
        self.assertEquals(result, '        string')

    def test_indentTwoLines(self):
        """ indent two lines
        """
        input = 'line1\nline2'
        result = indent(input, 1)
        expected = '    line1\n    line2'
        self.assertEquals(result, expected)

    def test_indentThreeLinesOneEmpty(self):
        """ indent two lines plus an empty one
        """
        input = 'line1\nline2\n'
        result = indent(input, 1)
        expected = '    line1\n    line2\n    '
        # No, we don't want an \n at the end (just like in the rest)
        self.assertEquals(result, expected)

    def test_indentDontBarfOnEmptyString(self):
        """ Don't barf on an empty string
        """
        result = indent('', 0)
        self.assertEquals(result, '')
    
    def test_indentDontBarfOnEmptyStringWhenIndenting(self):
        """ Don't barf on an empty string
        """
        result = indent('', 1)
        self.assertEquals(result, '    ')

    def test_indentDontBarfOnNone(self):
        """ Don't barf on a None value

        This can happen, see
        https://sourceforge.net/tracker/index.php?func=detail&aid=1159358&group_id=75272&atid=543430
        """
        result = indent(None, 0)
        self.assertEquals(result, '')
    



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite

if __name__ == '__main__':
    unittest.main()
