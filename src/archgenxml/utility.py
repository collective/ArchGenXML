"""Global utilities for archgenxml.

Using named utilities is a way of limiting the amount of information
that you have to pass along. Especially the ArchetypesGenerator gets
passed along a lot of times simply because that contains all the
parsed options in its self.__dict__. Putting the parsed options into a
named utility can greatly cut down the number of times the generator
has to be passed along.

"""

from archgenxml.interfaces import IOptions
from zope import component
from zope import interface

class OptionsHolder(object):
    interface.implements(IOptions)

    def __init__(self):
        self.options = {}

    def storeOptions(self, options):
        """Store the options.
        """
        self.options = options
        

    def option(self, optionName, default=None):
        """Retrieve the option.
        """

        if not optionName in self.options:
            return default
        return self.options[optionName]


optionsHolder = OptionsHolder()
component.provideUtility(optionsHolder, name='options')
