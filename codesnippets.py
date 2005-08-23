#-----------------------------------------------------------------------------
# Name:        codesnippets.py
# Purpose:     collects all string based code snippets
# Remark:      this and the stuff in templates directory should go somewhere
#              in future into a templating language like DTML
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# RCS-ID:      $Id$
# Copyright:   (c) 2003-2005, BlueDynamics, Austria
# Licence:     GPL
#-----------------------------------------------------------------------------


ACT_TEMPL="""
       {'action':      %(action)s,
        'category':    %(action_category)s,
        'id':          '%(action_id)s',
        'name':        '%(action_label)s',
        'permissions': (%(permission)s,),
        'condition'  : '%(condition)s'
       },
        """

MODIFY_FTI = """\
def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in [%(hideactions)s]:
            a['visible'] = 0
    return fti
"""

ACTIONS_START = """
    actions = %s (
"""

ACTIONS_END = """
    )
"""

DEFAULT_ACTIONS = """
       {'action': 'string:${object_url}/base_edit',
        'category': 'object',
        'id': 'edit',
        'name': 'Edit',
        'permissions': ('Modify portal content',),
       },

       {'action': 'string:${object_url}/base_view',
        'category': 'object',
        'id': 'view',
        'name': 'View',
        'permissions': ('View',),
       },

"""

DEFAULT_ACTIONS_FOLDERISH ="""
       {'action': 'string:${folder_url}/folder_listing',
        'category': 'folder',
        'condition': 'object/isPrincipiaFolderish',
        'id': 'folderlisting',
        'name': 'Folder Listing',
        'permissions': ('View',)
       },

"""

FTI_TEMPL='''\
    filter_content_types       = %(filter_content_types)d
    global_allow               = %(global_allow)d
    allow_discussion           = %(allow_discussion)s
    %(has_content_icon)scontent_icon               = '%(content_icon)s'
    immediate_view             = '%(immediate_view)s'
    default_view               = '%(default_view)s'
    typeDescription            = %(typeDescription)s
    typeDescMsgId              = 'description_edit_%(type_name_lc)s'
'''

TOOL_FTI_TEMPL='''\
    %(has_toolicon)stoolicon                   = '%(toolicon)s'
'''

CLASS_SCHEMA = """\
    schema= %(prefix)s + schema %(postfix)s
"""

SCHEMA_START       = """schema=Schema(("""

SCHEMA_TOOL = """\
        # a tool does not need be editable in id and title
        StringField('id',
            required=0,
            mode="r",
            accessor="getId",
            mutator="setId",
            default='',
        ),
        StringField('title',
            required=1,
            searchable=0,
            default='',
            mode='r',
            accessor='Title',
        ),
"""

TEMPL_APE_HEADER = """
from Products.Archetypes.ApeSupport import constructGateway,constructSerializer

def ApeGateway():
    return constructGateway(%(class_name)s)

def ApeSerializer():
    return constructSerializer(%(class_name)s)

"""

TEMPL_TOOL_HEADER="""
from Products.CMFCore.utils import UniqueObject

    """

CLASS_META_TYPE      = """    meta_type                  = '%s' """
CLASS_PORTAL_TYPE    = """    portal_type                = '%s' """
CLASS_ARCHETYPE_NAME = """    # This name appears in the 'add' box
    archetype_name             = '%s'\n"""
CLASS_IMPLEMENTS     = """    __implements__ = %(baseclass_interfaces)s + (%(realizations)s,)"""
CLASS_IMPLEMENTS_BASE= """    __implements__ = %(baseclass_interfaces)s"""
CLASS_ALLOWED_CONTENT_TYPES      = '''    allowed_content_types      = %s %s'''
CLASS_ALLOWED_CONTENT_INTERFACES = '''    allowed_interfaces = [%s] %s'''
CLASS_RENAME_AFTER_CREATION      = '''    _at_rename_after_creation  = %s \n'''

REGISTER_ARCHTYPE    = """registerType(%s,PROJECTNAME)\n"""

IMPORT_INTERFACE     = """from Interface import Base"""

MODULE_INFO_HEADER = """\
# File: %(filename)s
# %(rcs_id_tag)s
# %(copyright)s
%(date)s# Generator: ArchGenXML Version %(version)s http://sf.net/projects/archetypes/
#
# %(licence)s
#
__author__  = '''%(authorline)s'''
__docformat__ = 'plaintext'

"""

COPYRIGHT  = """Copyright (c) %s by %s"""

GPLTEXT = """\
GNU General Public Licence (GPL)

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA"""

REGISTER_VOCABULARY_ITEM      = """registerVocabularyTerm(%s, '%s')"""
REGISTER_VOCABULARY_CONTAINER = """registerVocabulary(%s)"""

TEMPL_CONSTR_TOOL="""
    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        %s.__init__(self,'%s')
        """

TEMPLATE_HEADER = """\
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *"""

TEMPLATE_HEADER_I18N_I18N_AT = """\
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.I18NArchetypes.public import *
    """

TEMPLATE_HEADER_I18N_LINGUAPLONE = """\
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # Not multilingual
    pass

    """

TEMPLATE_CONFIG_IMPORT = """\
from Products.%(module)s.config import *"""


TEMPL_APECONFIG_BEGIN = """<?xml version="1.0"?>

<!-- Basic Zope 2 configuration for Ape. -->

<configuration>"""

TEMPL_APECONFIG_END   = """</configuration>"""

READMEHIGHEST = """\
Directory 'skins/%s_public':

This skin layer has highest priority, put templates and scripts here that are
supposed to overload existing ones.

I.e. if you want to change want a site-wide change of Archetypes skins
base_edit, base_view, etc or also Plone skins like main_template or
document_view, put it in here."""

READMELOWEST = """\
Directory 'skins/%s':

This skin layer has low priority, put unique templates and scripts here.

I.e. if you to want to create own unique views or forms for your product, this
is the right place."""

CMFMEMBER_IMPORTS = """\
# imports needed by CMFMember
from Products.CMFMember import Member as BaseMember
from Products.CMFMember.MemberPermissions import \\
        VIEW_PUBLIC_PERMISSION, EDIT_ID_PERMISSION, \\
        EDIT_PROPERTIES_PERMISSION, VIEW_OTHER_PERMISSION,  \\
        VIEW_SECURITY_PERMISSION, EDIT_PASSWORD_PERMISSION, \\
        EDIT_SECURITY_PERMISSION, MAIL_PASSWORD_PERMISSION, \\
        ADD_MEMBER_PERMISSION
from AccessControl import ModuleSecurityInfo
"""

CMFMEMBER_ADD = """\

# Generate the add%(prefix)s%(name)s method ourselves so we can do some extra
# initialization, i.e. so we can set an initial password
security = ModuleSecurityInfo('Products.%(module)s.%(prefix)s%(name)s')

security.declareProtected(ADD_MEMBER_PERMISSION, 'add%(prefix)s%(name)s')
def add%(prefix)s%(name)s(self, id, **kwargs):
    o = %(prefix)s%(name)s(id)
    self._setObject(id, o)
    o = getattr(self, id)
    o.initializeArchetype(**kwargs)
    o.getUser()
    o._setPassword(o._generatePassword())

"""
CMFMEMBER_SETUP_IMPORT = """\
from Products.CMFMember.Extensions.toolbox import SetupMember
"""
CMFMEMBER_SETUP_INSTALL = """\
"""
