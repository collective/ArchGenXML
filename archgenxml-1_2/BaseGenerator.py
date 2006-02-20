#-----------------------------------------------------------------------------
# Name:        BaseGenerator.py
# Purpose:     provide some common methods for the generator
#
# Author:      Jens Klein
#
# Created:     2005-01-10
# RCS-ID:      $Id: BaseGenerator.py 3411 2005-01-05 01:55:45Z yenzenz $
# Copyright:   (c) 2005 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

_marker = []

class BaseGenerator:
    """ abstract base class for the different concrete generators """

    def getOption(self,option,element,default=_marker,aggregate=False):
        ''' query a certain option for an element including 'aquisition' :
            search the lement, then the packages upwards, then global options'''

        if element:
            o=element

            #climb up the hierarchy
            aggregator=''
            while o:
                if o.hasTaggedValue(option):
                    if aggregate:
                        # create a multiline string
                        aggregator+=o.getTaggedValue(option)+'\n'
                    else:
                        return o.getTaggedValue(option)
                o=o.getParent()
            if aggregator:
                return aggregator

        #look in the options
        if hasattr(self,option):
            return getattr(self,option)

        if default != _marker:
            return default
        else:
            raise ValueError,"option '%s' is mandatory for element '%s'" % (option,element and element.getName())

    def cleanName(self, name):
        return name.replace(' ','_').replace('.','_').replace('/','_')
