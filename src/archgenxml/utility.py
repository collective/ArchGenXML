"""Global utilities for archgenxml.

Using named utilities is a way of limiting the amount of information
that you have to pass along. Especially the ArchetypesGenerator gets
passed along a lot of times simply because that contains all the
parsed options in its self.__dict__. Putting the parsed options into a
named utility can greatly cut down the number of times the generator
has to be passed along.

Once the utility module gets imported, the utility is set up.

  >>> import archgenxml.utility

Grab the utility like this:
  
  >>> from zope import component
  >>> options = component.getUtility(IOptions, name='options')
  >>> options
  <archgenxml.utility.OptionsHolder object at ...>

Fill the utility with a dictionary of options like this:

  >>> someOptions = {'color': 'disgustingly pink',
  ...                'adored_by': 'daughter'}
  >>> options.storeOptions(someOptions)

Getting the values back is a simple `option()` call. As the
optionparser ought to set defaults for all options, a missing key
should generate a nice, quick, explicit error right away. **Fail
early** is python's motto.

  >>> options.option('color')
  'disgustingly pink'
  >>> options.option('taste')
  Traceback (most recent call last):
  ...
  NonExistingOptionError: Non-existing global option: taste.

Calling storeOptions() again should update the already stored options,
it should not override them.

  >>> extraOptions = {'color': 'blue',
  ...                'taste': 'tasty'}
  >>> options.storeOptions(extraOptions)
  >>> options.option('color')
  'blue'
  >>> options.option('adored_by')
  'daughter'
  >>> options.option('taste')
  'tasty'

"""

from archgenxml.interfaces import IOptions
from zope import component
from zope import interface

class NonExistingOptionError(Exception):
    def __init__(self, optionName):
        self.option = optionName
        
    def __str__(self):
        msg = u'Non-existing global option: %s.'
        return msg % self.option
    

class OptionsHolder(object):
    interface.implements(IOptions)

    def __init__(self):
        self.options = {}

    def storeOptions(self, options):
        """Store the options.

        Options should be a dictionary.
        """
        self.options.update(options)
        

    def option(self, optionName):
        """Retrieve the option.
        """

        if not optionName in self.options:
            raise NonExistingOptionError(optionName)
        return self.options[optionName]


optionsHolder = OptionsHolder()
component.provideUtility(optionsHolder, name='options')
