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


class TaggedValue():
    """ Base class for tagged values
    """
    pass

class StringTaggedValue(TaggedValue):
    """ Tagged value just for setting some value in the model
    """
    pass

class BooleanTaggedValue(TaggedValue):
    pass


