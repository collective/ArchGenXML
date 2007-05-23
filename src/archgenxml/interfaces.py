from zope.interface import Interface

class IOptions(Interface):
    """Interface of the utility that stores option values.
    """

    def storeOptions(self, options):
        pass

    def option(self, optionName, default):
        pass
