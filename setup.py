#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

import re
import os
import sys
from setuptools import setup
from setuptools import find_packages

setup(name='archgenxml',
      version='1.6.b1',
      license='GPL',
      description='Generates plone products from UML',
      long_description="""
      Archgenxml generates plone products out of UML models, saving
      you a lot of time and boilerplate code. Be lazy, use archgenxm!
      """,
      keywords="zope plone UML",
      author='Reinout van Rees',
      author_email='reinout@vanrees.org',
      url='http://plone.org/products/archgenxml',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      entry_points={
        'console_scripts':[
            'archgenxml = archgenxml.ArchGenXML:main'
            ]
        },
      test_suite='archgenxml.tests.runalltests.suite',
      # The stuff below messes up zope instances running on the same
      # python...
      #install_requires="""
      #zope.interface
      #zope.component
      #zope.testing
      #zope.configuration
      #""",
      #dependency_links = [
      #  'http://download.zope.org/distribution/'
      #  ],
      )
