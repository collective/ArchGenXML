import doctest
import unittest

import archgenxml
import archgenxml.utility
import archgenxml.plone.config_py

modules = [
    archgenxml.utility,
    archgenxml.plone.config_py,
    ]

textfiles = [
    ]

def test_suite():
    optionflags = (doctest.ELLIPSIS |
                   doctest.NORMALIZE_WHITESPACE |
                   doctest.REPORT_ONLY_FIRST_FAILURE)
    suite = unittest.TestSuite()
    for module in modules:
        suite.addTest(doctest.DocTestSuite(
            module,
            optionflags=optionflags))
    for textfile in textfiles:
        suite.addTest(doctest.DocFileSuite(
            textfile,
            module_relative=True,
            package=archgenxml,
            optionflags=optionflags))
    return suite
