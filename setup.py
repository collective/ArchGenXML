#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

import re
import os
import sys
from setuptools import setup
from setuptools import find_packages

version = open(os.path.join(os.path.dirname(__file__), 'src', 'archgenxml', 
                            'version.txt')).read()
shortdesc = 'UML to code generator for Plone'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='archgenxml',
      version=version,
      license='GPL',
      description=shortdesc,
      long_description=longdesc,
      keywords="zope plone UML generator",
      author='Phil Auersperg, Jens Klein',
      author_email='dev@bluedynamics.com',
      url='http://plone.org/products/archgenxml',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      entry_points={
        'console_scripts':[
            'archgenxml = archgenxml.ArchGenXML:main',
            'agx_taggedvalues = archgenxml.TaggedValueSupport:main',
            'agx_stereotypes = archgenxml.UMLProfile:main',
            'agx_argouml_profile = archgenxml.ArgoUMLProfileGenerator:main',
            ]
        },
      test_suite='archgenxml.tests.runalltests.suite',
      zip_safe=False,
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
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      
      )
