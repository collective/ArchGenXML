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
from PyParser import PyModule


class TestPyModule(unittest.TestCase):
    def setUp(self):
        self.emptyFile = 'tests/pythonfiles/empty.py'
        self.emptyStringFile = '# Empty python file\n# Some more'
        self.parser = PyModule(self.emptyFile)
    
    def testReadFile1(self):
        # Don't barf on an empty file
        self.parser.readFile(self.emptyFile)

    def testReadFile2(self):
        # Also accept a file pointer instead of a filename
        file = open(self.emptyFile)
        self.parser.readFile(file)
        file.close()

    def testReadFile3(self):
        # Don't barf on an empty string-file
        parser = PyModule(self.emptyStringFile, mode='string')

    def testReadFile4(self):
        # Barf on an empty string-file without correct mode
        self.assertRaises(IOError, self.parser.readFile, self.emptyStringFile)


if __name__ == '__main__':
    unittest.main()
