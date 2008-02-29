"""
Setup all functional tests.


The purpose of this file is to create a suite of all functional tests for the product
being tested.  We do not simply enumerate all files matching a particular file nameing
pattern as we do for unit tests, as often functional tests require that the suite be
run in a particular order.  In functional testing, one test often builds upon what
a previous test has done.

Also, the whole framework based method of testing no longer is valid with Five browser
based functional testing.  The correct way to run these tests is with test.py in the 
zope bin directory.  I haven't yet taken the time to make this file do everything that
is necessary to setup and execute test.py, so that will need to be a manual process on
your part.

The form of this file should be:

##############################################################################
from Products.{product}.tests import *

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite({module_to_test_first}.{class_name1}))
    suite.addTest(makeSuite({module_to_test_second}.{class_name1}))
    suite.addTest(makeSuite({module_to_test_third}.{class_name1}))
    return suite

##############################################################################

Then, you can run the tests with:
test.py -v --config-file "{path_to_plone_instance}/etc/zope.conf"  -s Products.{MyProduct}


So copy the code above to below, and change as necessary.
"""



