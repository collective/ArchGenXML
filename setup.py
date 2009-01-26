#!/usr/bin/env python
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
      classifiers=[
            'Programming Language :: Python',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Topic :: Software Development :: Code Generators',
            'Framework :: Zope2',
            'Framework :: Plone',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords="zope plone UML generator",
      author='Phil Auersperg, Jens Klein, et al',
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
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'xmiparser >= 1.3',
          'zope.interface',
          'zope.component',
          'zope.documenttemplate',
      ],
      extras_require = dict(
          i18n=['i18ndude']
      ),
      
      )
