============================================
ArchGenXML - UML to code generator for Plone
============================================

Overview
========

With *ArchGenXML* you can create working python code without writing one single 
line of python. It is is a commandline utility that generates fully functional 
*Zope* Products based on the *Archetypes* framework from *UML* models using *XMI* 
(``.xmi``, ``.zargo``, ``.zuml``) files. The most common use case is to generate 
a set of custom content types, possibly with a few tools, a custom Member type 
and some workflows thrown in.

How it works
============

In practice, you draw your UML diagrams in a tool like *ArgoUML* or *Poseidon*
which has the ability to generate XMI files. Once you are ready to test your 
product, you run *ArchGenXML* on the XMI file, which will generate the product 
directory. After generation, you will be able to install your product in Plone 
and have your new content types, tools and workflows available.

At present, round-trip support is not implemented: Custom code can't be 
converted back into XMI (and thus diagrams). However, you can re-generate 
your product over existing code. Method bodies and certain *protected* code 
sections will be preserved. This means that you can evolve your product's 
public interfaces, its methods and its attributes in the UML model, without 
fear of losing your hand-written code.

Supported Plone Versions
========================

We support Plone Versions 2.5.x and 3.0.x. But if you have code generated 
with some ArchGenXML version below 2 you will need to adjust the generated 
model and code manually. There is no smooth migration. If you dont need to make 
your code run on Plone 3 stick to an older version of ArchGenXML.