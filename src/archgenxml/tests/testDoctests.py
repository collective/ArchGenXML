import doctest
import sys

files = ['interfaces/README.txt',
         'reutel/aargh',
         ]

    
def test_suite():
    optionflags = (doctest.ELLIPSIS |
                   doctest.NORMALIZE_WHITESPACE |
                   doctest.REPORT_ONLY_FIRST_FAILURE)
    suite = doctest.DocFileSuite(
        tests=files,
        optionflags=optionflags,
        #module_relative=True,
        #package='archgenxml',
        )
    print "Returning doctest suite"
    return suite
