class testAtpConnector(AtpTestcase):
    """ test-cases for class(es) AtpConnector
    """

    def testmethod(self):
        """ The problem here is that last list which used
        to get truncated by the pyparser.
        """
        self.atp = AtpConnector('testid')
        self.empty_data = []
        self.full_data = [
            ['SUPPLY', 20, '2005-01-01 09:30:21.00'],
            ['DEMAND', 20, '2005-04-01 09:30:21.00'],
            ['SUPPLY', 20, '2005-03-01 09:30:21.00'],
            ['SUPPLY', 10, '2005-03-01 09:30:21.00'],
            ]

# Above method isn't parsed correctly. It only detects 7
# lines instead of 12. Those last 5 indented lines are
# missing when writing back this parsed method to another
# file. Adding an unindented "test = 42" or so corrects the
# problem... Hmpf.

    def testmethodcorrect(self):
        """ The problem here is that last list which used
        to get truncated. The extra line fixes it
        """
        self.atp = AtpConnector('testid')
        self.empty_data = []
        self.full_data = [
            ['SUPPLY', 20, '2005-01-01 09:30:21.00'],
            ['DEMAND', 20, '2005-04-01 09:30:21.00'],
            ['SUPPLY', 20, '2005-03-01 09:30:21.00'],
            ['SUPPLY', 10, '2005-03-01 09:30:21.00'],
            ]
        test = 42
