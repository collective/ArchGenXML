# WARNING: work-in-progress. Don't touch for a day or three.


#----------------------------------------------------------------
# Name:        TaggedValueSupport.py
# Purpose:     Tools and registry for tagged values. The registry
#              improves documentation of the TGVs.
#
# Author:      Reinout van Rees
#
# Created:     2005-07-04
# Copyright:   (c) Zest software/Reinout van Rees
# Licence:     GPL
#-----------------------------------------------------------------------------

# isTGVTrue() and isTGVFalse are originally copied from utils.py

"""
Tagged values come in two variants. Boolean tagged values and
string-like tagged values that just set a certain value.

Getting our hands on the boolean ones is easy, as they get used
through the isTGVTrue/isTGVFalse methods. For the string-like ones we
need to think of an additional evil scheme... Perhaps look if we can
build a "just handle all other TGVs" method?

updatedKeysFromTGV

"""

def isTGVTrue(tgv):
    """ Return True if the TGV is true
    """
    if type(tgv) in (type(''),type(u'')):
        tgv=tgv.lower()
    return tgv in (1,'1','true')

def isTGVFalse(tgv):
    """ Return True if the TGV is explicitly false

    Checks if a tgv is _explicitly_ false, a 'None' value is undefined
    and _not_ false, so it is something different than (not
    toBoolean(tgv))
    """
    if type(tgv) in (type(''),type(u'')):
        tgv=tgv.lower()
    return tgv in (0,'0','false')


class TaggedValueRegistry:
    """ Registry for all known tagged values (TGVs)

    The aim is to get them finally well-documented by providing a
    place to actually document them.
    """

    def __init__(self):
        """ Initialise an empty registry
        """
        self._registry = {}

    def addTaggedValue(self, category='', name='', explanation=''):
        """ Adds a TGV to the registry

        If the category doesn't exist yet, create it in
        '_registry'. Then add the tagged value to it.
        """
        if not category or not name:
            raise "Category and/or name for TGV needed"
        if not self._registry.has_key(category):
            self._registry[category] = {}
        self._registry[category][name] = explanation

    def isRegisteredTaggedValue(self, category='', name=''):
        """
        """
        #import pdb; pdb.set_trace()
        if not self._registry.has_key(category):
            return False
        if not self._registry[category].has_key(name):
            return False
        return True


tgvRegistry = TaggedValueRegistry()
# Class level tagged values
category = 'class'

name = 'archetype_name'
explanation = '''The name which will be shown in the "add new item" drop-down and other
user-interface elements. Defaults to the class name, but whilst the
class name must be valid and unique python identifier, the
archetype_name can be any string.
'''
tgvRegistry.addTaggedValue(category=category, name=name, explanation=explanation)

