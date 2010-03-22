# File: ParserTest.py
"""\
Purpose

"""
# Copyright (c) 2005 by Zest software 2005
#
# Generator: ArchGenXML Version 1.4 devel 1 http://plone.org/products/archgenxml
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
__author__  = '''Reinout van Rees <r.van.rees@zestsoftware.nl>'''
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *




from Products.MyProduct.config import *

##code-section module-header #fill in your manual code here
someTest = 'Some value'
##/code-section module-header

schema= Schema((
    StringField('parserAttribute',
        widget=StringWidget(
            label='Parserattribute',
            label_msgid='Parsertest_label_parserAttribute',
            description='Enter a value for parserAttribute.',
            description_msgid='Parsertest_help_parserAttribute',
            i18n_domain='Parsertest',
        ),
    ),
    
),
)

##code-section after-schema #fill in your manual code here
someTest = 'Some value'

def someMethod():
    pass

def oneLineMethod(): pass

##/code-section after-schema

class ParserTest(BaseContent):
    """ Doctest line 1

    Doctest line 2
    """
    security = ClassSecurityInfo()


    # This name appears in the 'add' box
    archetype_name             = 'ParserTest'
    portal_type = meta_type    = 'ParserTest' 

    allowed_content_types      = [] 
    filter_content_types       = 1
    global_allow               = 1
    allow_discussion           = 0
    #content_icon               = 'ParserTest.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    typeDescription            = "ParserTest"
    typeDescMsgId              = 'description_edit_parsertest'

    schema = BaseSchema + \
             schema

    ##code-section class-header #fill in your manual code here
    someTest = 'Some value'
    ##/code-section class-header


    #Methods

    security.declarePublic('parserMethod')
    def parserMethod(self):
        """
        
        """
        
        pass

    #Manually created methods

    security.declarePublic('parserMethod2')
    def parserMethod2(self):
        """
        
        """
        
        pass

registerType(ParserTest,PROJECTNAME)
# end of class ParserTest

##code-section module-footer #fill in your manual code here
someTest = 'Some value'
##/code-section module-footer



