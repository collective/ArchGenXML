#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

import re
import os
import sys
from setuptools import setup
from setuptools import find_packages

setup(name='archgenxml',
      version='2.0-beta5 (dev/svn)',
      license='GPL',
      description='Generates Plone products from UML',
      long_description="""
With ArchGenXML you can create working python code without writing one single 
line of python. It is is a commandline utility that generates fully functional 
Zope Products based on the Archetypes framework from UML models using XMI 
(.xmi, .zargo, .zuml) files. The most common use case is to generate a set of 
custom content types, possibly with a few tools, a custom Member type and some 
workflows thrown in.

In practice, you draw your UML diagrams in a tool like ArgoUML or Poseidon
which has the ability to generate XMI files. Once you are ready to test your 
product, you run ArchGenXML on the XMI file, which will generate the product 
directory. After generation, you will be able to install your product in Plone 
and have your new content types, tools and workflows available.

At present, round-trip support is not implemented: Custom code can't be 
converted back into XMI (and thus diagams). However, you can re-generate 
your product over existing code. Method bodies and certain "protected" code 
sections will be preserved. This means that you can evolve your product's 
public interfaces, its methods and its attributes in the UML model, without 
fear of losing your hand-written code.
      """,
      keywords="zope plone UML",
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
      )
