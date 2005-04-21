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
        self.realFile = 'tests/pythonfiles/ParserTest.py'
        self.parser = PyModule(self.realFile)
        self.function = self.parser.functions['someMethod']
        self.oneLineFunction = self.parser.functions['oneLineMethod']
        self.klass = self.parser.classes['ParserTest']
        
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
        self.assertRaises(IOError, self.parser.readFile,
                          self.emptyStringFile) 

    def testFindClassesAndFunctions(self):
        # tests/pythonfiles/ParserTest.py contains:
        # 1 class + 1 function
        self.assertEquals(len(self.parser.classes), 1)
        self.assertEquals(len(self.parser.functions), 2)

    def testFindProtectedSections(self):
        # tests/pythonfiles/ParserTest.py contains 4 protected
        # sections: module-header, after-schema, class-header,
        # module-footer. 
        self.assertEquals(len(self.parser.protectedSections), 4)

    # Tests for PyFunction class inside PyParser
    def testCodeLength(self):
        self.assertEquals(self.function.codeLength(), 2)
        self.assertEquals(self.oneLineFunction.codeLength(), 1)

    def testExtractCode(self):
        # TODO
        pass

if __name__ == '__main__':
    unittest.main()
