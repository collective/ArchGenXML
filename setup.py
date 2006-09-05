#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

import re
import os
import sys
from setuptools import setup
from setuptools import find_packages

setup(name='archgenxml',
      version='1.6.a',
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
      #install_requires="""
      #zope_interface
      #zope_component
      #"""
      )
