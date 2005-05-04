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
        self.method = self.klass.methods['parserMethod']
        self.manualMethod = self.klass.methods['parserMethod2']
        
    def testReadFile1(self):
        """ Don't barf on an empty file
        """ 
        self.parser.readFile(self.emptyFile)

    def testReadFile2(self):
        """ Also accept a file pointer instead of a filename
        """
        file = open(self.emptyFile)
        self.parser.readFile(file)
        file.close()

    def testReadFile3(self):
        """ Don't barf on an empty string-file
        """
        parser = PyModule(self.emptyStringFile, mode='string')

    def testReadFile4(self):
        """ Barf on an empty string-file without correct mode
        """
        self.assertRaises(IOError, self.parser.readFile,
                          self.emptyStringFile) 

    def testFindClassesAndFunctions(self):
        """ Find the correct number of classes and functions

        tests/pythonfiles/ParserTest.py contains: 1 class + 1 function
         """
        self.assertEquals(len(self.parser.classes), 1)
        self.assertEquals(len(self.parser.functions), 2)

    def testFindProtectedSections(self):
        """ Find the correct number of protected sections
        
        tests/pythonfiles/ParserTest.py contains 4 protected sections:
        module-header, after-schema, class-header, module-footer.
        """
        self.assertEquals(len(self.parser.protectedSections), 4)

    # Tests for PyCodeElement class inside PyParser
    # Tested with the two functions
    def testGetSrc(self):
        """ getSrc should return the source

        Pretty pedantic tests, but we want the source, just the
        source, luke. No messing around with it.
        """
        self.assertEquals(self.function.getSrc(), self.function.src)
        self.assertEquals(self.oneLineFunction.getSrc(),
                          self.oneLineFunction.src) 

    def testGetName(self):
        """ getName should return the name

        Also pretty pedantic, but safeguards against messing around!
        """
        self.assertEquals(self.oneLineFunction.getName(), 'oneLineMethod')
        self.assertEquals(self.function.getName(), 'someMethod')

    # Tests for PyFunction class inside PyParser
    def testCodeLength(self):
        """ Find the correct length of code for two examples
        """
        self.assertEquals(self.function.codeLength(), 2)
        self.assertEquals(self.oneLineFunction.codeLength(), 1)

    def testExtractCode(self):
        """ Output the correct code from the test files
        """
        desired = 'def oneLineMethod(): pass\n'
        self.assertEquals(self.oneLineFunction.extractCode(), desired)
        desired2 = 'def someMethod():\n    pass\n'
        self.assertEquals(self.function.extractCode(), desired2)

    def testBuildMethod(self):
        """ Test function name extraction

        self.name extraction is the only thing that needs checking,
        extractCode is checked seperately.
        """
        self.assertEquals(self.oneLineFunction.name, 'oneLineMethod')
        self.assertEquals(self.function.name, 'someMethod')

    # Tests for PyMethod class inside PyParser
    # Basically do the same tests, but with methods inside classes
    # instead of loose functions.
    def testCodeLength_method(self):
        """ Find the correct length of code for two methods
        """
        self.assertEquals(self.method.codeLength(), 6)
        self.assertEquals(self.manualMethod.codeLength(), 6)

    def testBuildMethod_method(self):
        """ Test method name extraction
        """
        self.assertEquals(self.method.name, 'parserMethod')
        self.assertEquals(self.manualMethod.name, 'parserMethod2')

    # Tests for PyClass class inside PyParser
    # TODO

if __name__ == '__main__':
    unittest.main()
