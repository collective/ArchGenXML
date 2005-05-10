#
# Runs all tests in the current directory
#
# Execute like:
#   python runalltests.py
#
# Alternatively use the testrunner: 
#   python /path/to/Zope/utilities/testrunner.py -qa
#

import os
import sys
import unittest

testDir = os.path.dirname(os.path.abspath(__file__))
TestRunner = unittest.TextTestRunner
suite = unittest.TestSuite()

tests = os.listdir(testDir)
tests = [n[:-3] for n in tests if n.startswith('test') and n.endswith('.py')]
for test in tests:
    print test
    m = __import__(test)
    if hasattr(m, 'test_suite'):
        suite.addTest(m.test_suite())

if __name__ == '__main__':
    TestRunner().run(suite)

