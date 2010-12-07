# -*- coding: utf-8 -*-

import unittest
import time

from archgenxml.ArchetypesGenerator import ArchetypesGenerator
from archgenxml.ArchetypesGenerator import DummyModel
from archgenxml.interfaces import IOptions

import zope.component



class TestArchetypesGenerator(unittest.TestCase):

    def setUp(self):
        self.options = {
            'detailed_creation_permissions': 1,
            'default_class_type': 'content_class',
            'force': 1,
            'backreferences_support': None,
            'unknownTypesAsString': 0,
            'generated_date': 0,
            'relation_implementation': 'basic',
            'generate_packages': None,
            'copyright': '',
            'outfilename': '',
            'manual_code_sections': 1,
            'config_file': None,
            'version_info': 1,
            'pdb_on_exception': 0,
            'rcs_id': 0,
            'default_interface_type': 'z3',
            'module_info_header': 1,
            'default_creation_permission': 'Add portal content',
            'build_msgcatalog': 1,
            'i18n_content_support': '',
            'license': 'GPL',
            'default_field_generation': 0,
            'profile_dir': '',
            'strip_html': 0,
            'generateActions': 1,
            'creation_roles': "python:('Manager','Owner')",
            'author': 'Example Author',
            'email': 'author@example.org',
        }
        optionsHolder = zope.component.getUtility(IOptions, name='options')
        optionsHolder.storeOptions(self.options)
        self.model = DummyModel('test')

    def test_getHeaderInfo_copyright_info_simple(self):
        """Test the copyright info output."""
        year = time.localtime()[0]
        expected = 'Copyright (c) %s by %s <%s>' % (year,
                                                    self.options['author'],
                                                    self.options['email'])

        generator = ArchetypesGenerator('/dev/null', **self.options)
        headerinfo = generator.getHeaderInfo(self.model)

        self.failUnless(headerinfo['copyright'] == expected)

    def test_getHeaderInfo_copyright_info_list(self):
        """Test for multiple authors."""
        self.options.update(author='Example1, Example2')
        self.options.update(email='one@example.org, two@example.org')
        year = time.localtime()[0]
        expected = 'Copyright (c) %s by Example1 <one@example.org>, ' \
                   'Example2 <two@example.org>' % (year)
        generator = ArchetypesGenerator('/dev/null', **self.options)
        headerinfo = generator.getHeaderInfo(self.model)

        self.failUnless(headerinfo['copyright'] == expected)

    def test_getHeaderInfo_copyright_info_unicode(self):
        """Test that non-ASCII characters are processed correctly."""
        self.options.update(author='Äöü€')
        year = time.localtime()[0]
        expected = 'Copyright (c) %s by Äöü€ <%s>' % (year,
                                                      self.options['email'])
        generator = ArchetypesGenerator('/dev/null', **self.options)
        headerinfo = generator.getHeaderInfo(self.model)
        self.failUnless(headerinfo['copyright'] == expected)

    def test_generateModuleInfoHeader(self):
        self.options.update(author='Äöü€')
        generator = ArchetypesGenerator('/dev/null', **self.options)
        result = generator.generateModuleInfoHeader(self.model)
        assert u'Copyright (c) 2010 by Äöü€ <author@example.org>' in result


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestArchetypesGenerator))
    return suite

