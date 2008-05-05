""" Tests for the PyParser.py file

PyParser is a bit hard to test, as everything depends on the loading
of an initial file by PyModule's '__init__()'. Together with the
testcases' being subclasses of eachother, this results in a lot of
tests which are effectively called a number of times with exactly the
same inputs. Ah well.
"""

import unittest
from archgenxml.XMIParser import XMI1_0
from archgenxml.XMIParser import XMI1_1 
from archgenxml.XMIParser import XMI1_2 
from archgenxml.XMIParser import NoObject
from archgenxml.XMIParser import PseudoElement
from archgenxml.XMIParser import XMIElement
from archgenxml.XMIParser import StateMachineContainer
from archgenxml.XMIParser import XMIPackage
from archgenxml.XMIParser import XMIModel
from archgenxml.XMIParser import XMIClass 
from archgenxml.XMIParser import XMIInterface
from archgenxml.XMIParser import XMIMethodParameter
from archgenxml.XMIParser import XMIMethod 
from archgenxml.XMIParser import XMIAttribute 
from archgenxml.XMIParser import XMIAssocEnd 
from archgenxml.XMIParser import XMIAssociation 
from archgenxml.XMIParser import XMIAssociationClass 
from archgenxml.XMIParser import XMIAbstraction
from archgenxml.XMIParser import XMIDependency
from archgenxml.XMIParser import XMIStateMachine
from archgenxml.XMIParser import XMIStateTransition
from archgenxml.XMIParser import XMIAction
from archgenxml.XMIParser import XMIGuard
from archgenxml.XMIParser import XMIState
from archgenxml.XMIParser import XMICompositeState
from archgenxml.XMIParser import XMIDiagram


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
    suite.addTest(unittest.makeSuite(TestXMI1_0))
    suite.addTest(unittest.makeSuite(TestXMI1_1))
    suite.addTest(unittest.makeSuite(TestXMI1_2))
    suite.addTest(unittest.makeSuite(TestNoObject))
    suite.addTest(unittest.makeSuite(TestPseudoElement))
    suite.addTest(unittest.makeSuite(TestXMIElement))
    suite.addTest(unittest.makeSuite(TestStateMachineContainer))
    suite.addTest(unittest.makeSuite(TestXMIPackage))
    suite.addTest(unittest.makeSuite(TestXMIModel))
    suite.addTest(unittest.makeSuite(TestXMIClass))
    suite.addTest(unittest.makeSuite(TestXMIInterface))
    suite.addTest(unittest.makeSuite(TestXMIMethodParameter))
    suite.addTest(unittest.makeSuite(TestXMIMethod))
    suite.addTest(unittest.makeSuite(TestXMIAttribute))
    suite.addTest(unittest.makeSuite(TestXMIAssocEnd))
    suite.addTest(unittest.makeSuite(TestXMIAssociation))
    suite.addTest(unittest.makeSuite(TestXMIAssociationClass))
    suite.addTest(unittest.makeSuite(TestXMIAbstraction))
    suite.addTest(unittest.makeSuite(TestXMIDependency))
    suite.addTest(unittest.makeSuite(TestXMIStateContainer))
    suite.addTest(unittest.makeSuite(TestXMIStateMachine))
    suite.addTest(unittest.makeSuite(TestXMIStateTransition))
    suite.addTest(unittest.makeSuite(TestXMIAction))
    suite.addTest(unittest.makeSuite(TestXMIGuard))
    suite.addTest(unittest.makeSuite(TestXMIState))
    suite.addTest(unittest.makeSuite(TestXMICompositeState))
    suite.addTest(unittest.makeSuite(TestXMIDiagram))
    return suite

if __name__ == '__main__':
    unittest.main()
