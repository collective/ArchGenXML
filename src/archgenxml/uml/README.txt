Reacting on UML model elements using interfaces
===============================================

What should archgenxml do with a UML package? Or a UML class? In "ye
olde days" (read: currently in 99% of the code), this is pretty much
defined in python code. Zope3 provides the handy adapter mechanism
with which we can expicitly say what we want to do with a certain UML
element.

    >>> from archgenxml.XMIParser import XMIPackage
    >>> package = XMIPackage(None)

In the pre-1.6 code, this would be it. Just a class. With quite a
number of methods. Part of the methods were UML-centric, like adding a
new class to the package or looking for state machines. Others were
archgenxml-centric, methods that didn't have anything to do with the
model as such, but more with the needs of the code generation.

In the 1.6 code, the class also has an interface. This allows us to
use zope3 adapters to react to the class. And to have those adapters
react differently to other interfaces.

    >>> from archgenxml.uml.interfaces import IPackage
    >>> IPackage.providedBy(package)
    True
    >>> from archgenxml.XMIParser import XMIMethodParameter
    >>> param = XMIMethodParameter(None)
    >>> IPackage.providedBy(param)
    False

    
