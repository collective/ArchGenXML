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

packageTGVs = []
classTGVs = []
methodTGVs = []
attributeTGVs = []
tgvRegistry = {'package': packageTGVs,
               'class': classTGVs,
               'method': methodTGVs,
               'attribute': attributeTGVs}


