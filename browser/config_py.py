from zope import interface
from zope import component
from interfaces import IConfigPyView
from archgenxml.interfaces import IPackage

class ConfigPyView(object):
    """A view for the toplevel config.py file
    """
    
    component.adapts(IPackage)
    interface.implements(IConfigPyView)

    pass
