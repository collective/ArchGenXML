""" Tests for the PyParser.py file

PyParser is a bit hard to test, as everything depends on the loading
of an initial file by PyModule's '__init__()'. Together with the
testcases' being subclasses of eachother, this results in a lot of
tests which are effectively called a number of times with exactly the
same inputs. Ah well.
"""
import os
import sys
import unittest
# Something dirty. It is assumed that ArchGenXML isn't installed as a
# python module but that it resides "just somewhere" on the
# filesystem.
testDir = os.path.dirname(os.path.abspath(__file__))
parentDir = testDir[:-6] # Strips off '/tests'
# Appends the parent dir to the module search path
sys.path.append(parentDir)

from XMIParser import XMI1_0
from XMIParser import XMI1_1 
from XMIParser import XMI1_2 
from XMIParser import NoObject
from XMIParser import PseudoElement
from XMIParser import XMIElement
from XMIParser import StateMachineContainer
from XMIParser import XMIPackage
from XMIParser import XMIModel
from XMIParser import XMIClass 
from XMIParser import XMIInterface
from XMIParser import XMIMethodParameter
from XMIParser import XMIMethod 
from XMIParser import XMIAttribute 
from XMIParser import XMIAssocEnd 
from XMIParser import XMIAssociation 
from XMIParser import XMIAssociationClass 
from XMIParser import XMIAbstraction
from XMIParser import XMIDependency
from XMIParser import XMIStateContainer
from XMIParser import XMIStateMachine
from XMIParser import XMIStateTransition
from XMIParser import XMIAction
from XMIParser import XMIGuard
from XMIParser import XMIState
from XMIParser import XMICompositeState
from XMIParser import XMIDiagram


class TestXMI1_0(unittest.TestCase):
    """
    """
    pass


class TestXMI1_0(unittest.TestCase):
    """
    """
    pass


class TestXMI1_1(unittest.TestCase):
    """
    """
    pass


class TestXMI1_2(unittest.TestCase):
    """
    """
    pass


class TestNoObject(unittest.TestCase):
    """
    """
    pass


class TestPseudoElement(unittest.TestCase):
    """
    """
    pass


class TestXMIElement(unittest.TestCase):
    """
    """
    pass


class TestStateMachineContainer(unittest.TestCase):
    """
    """
    pass


class TestXMIPackage(unittest.TestCase):
    """
    """
    pass


class TestXMIModel(unittest.TestCase):
    """
    """
    pass


class TestXMIClass(unittest.TestCase):
    """
    """
    pass


class TestXMIInterface(unittest.TestCase):
    """
    """
    pass


class TestXMIMethodParameter(unittest.TestCase):
    """
    """
    pass


class TestXMIMethod(unittest.TestCase):
    """
    """
    pass


class TestXMIAttribute(unittest.TestCase):
    """
    """
    pass


class TestXMIAssocEnd(unittest.TestCase):
    """
    """
    pass


class TestXMIAssociation(unittest.TestCase):
    """
    """
    pass


class TestXMIAssociationClass(unittest.TestCase):
    """
    """
    pass


class TestXMIAbstraction(unittest.TestCase):
    """
    """
    pass


class TestXMIDependency(unittest.TestCase):
    """
    """
    pass


class TestXMIStateContainer(unittest.TestCase):
    """
    """
    pass


class TestXMIStateMachine(unittest.TestCase):
    """
    """
    pass


class TestXMIStateTransition(unittest.TestCase):
    """
    """
    pass


class TestXMIAction(unittest.TestCase):
    """
    """
    pass


class TestXMIGuard(unittest.TestCase):
    """
    """
    pass


class TestXMIState(unittest.TestCase):
    """
    """
    pass


class TestXMICompositeState(unittest.TestCase):
    """
    """
    pass


class TestXMIDiagram(unittest.TestCase):
    """
    """
    pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestXMI1_0))
    return suite

if __name__ == '__main__':
    unittest.main()
