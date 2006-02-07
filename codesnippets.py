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

ACT_TEMPL = """
       {'action': %(action)s,
        'category': %(action_category)s,
        'id': '%(action_id)s',
        'name': '%(action_label)s',
        'permissions': (%(permission)s,),
        'condition': '%(condition)s'
       },
"""

MODIFY_FTI = """\
def modify_fti(fti):
    # Hide unnecessary tabs (usability enhancement)
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

DEFAULT_ACTIONS_FOLDERISH = """
       {'action': 'string:${folder_url}/folder_listing',
        'category': 'folder',
        'condition': 'object/isPrincipiaFolderish',
        'id': 'folderlisting',
        'name': 'Folder Listing',
        'permissions': ('View',)
       },

"""

FTI_TEMPL = """\
    filter_content_types = %(filter_content_types)d
    global_allow = %(global_allow)d
    allow_discussion = %(allow_discussion)s
    %(has_content_icon)scontent_icon = '%(content_icon)s'
    immediate_view = '%(immediate_view)s'
    default_view = '%(default_view)s'
    suppl_views = %(suppl_views)s
    typeDescription = %(typeDescription)s
    typeDescMsgId = 'description_edit_%(type_name_lc)s'
"""

TOOL_FTI_TEMPL = """\
    %(has_toolicon)stoolicon = '%(toolicon)s'
"""

CLASS_SCHEMA = """\
    schema = %(prefix)s + schema %(postfix)s
"""

SCHEMA_START = """schema = Schema((
"""

SCHEMA_TOOL = """\
        # a tool does not need be editable in id and title
        StringField(
            name='id',
            required=0,
            mode='r',
            accessor='getId',
            mutator='setId',
            default='',
        ),

        StringField(
            name='title',
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

CLASS_META_TYPE = """    meta_type = '%s'"""
CLASS_PORTAL_TYPE = """    portal_type = '%s'"""
CLASS_ARCHETYPE_NAME = """    # This name appears in the 'add' box
    archetype_name = '%s'\n"""
CLASS_IMPLEMENTS = """    __implements__ = %(baseclass_interfaces)s + (%(realizations)s,)"""
CLASS_IMPLEMENTS_BASE = """    __implements__ = %(baseclass_interfaces)s"""
CLASS_ALLOWED_CONTENT_TYPES = '''    allowed_content_types = %s%s'''
CLASS_ALLOWED_CONTENT_INTERFACES = '''    allowed_interfaces = [%s] %s'''
CLASS_RENAME_AFTER_CREATION = '''    _at_rename_after_creation = %s\n'''

REGISTER_ARCHTYPE = """registerType(%s,PROJECTNAME)\n"""

IMPORT_INTERFACE = """from Interface import Base"""

MODULE_INFO_HEADER = '''\
# %(filename_or_id)s
#
# %(copyright)s
%(date)s# Generator: ArchGenXML %(version)s
#            http://plone.org/products/archgenxml
#
# %(license)s
#

__author__ = """%(authorline)s"""
__docformat__ = 'plaintext'

'''

COPYRIGHT = """Copyright (c) %s by %s"""

GPLTEXT = """\
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA."""

LGPLTEXT = """\
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA."""

BSDTEXT = """\
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#
#   * Neither the name of the Plone Foundation nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""

ZPLTEXT = """\
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE."""

DFSLTEXT = """\
# This Program may be used by anyone in accordance with the terms of the 
# German Free Software License
# The License may be obtained under <http://www.d-fsl.org>."""

LICENSES = {

    'GPL': {
        'name': 'GNU General Public License (GPL)',
        'text': GPLTEXT,
    },

    'LGPL': {
        'name': 'GNU Lesser General Public License (LGPL)',
        'text': LGPLTEXT,
    },

    'BSD': {
        'name': 'Berkeley Software Distribution License (BSD)',
        'text': BSDTEXT,
    },

    'ZPL': {
        'name': 'Zope Public License (ZPL)',
        'text': ZPLTEXT,
    },
    'DFSL': {
        'name': 'German Free Software License (D-FSL)',
        'text': DFSLTEXT,
    }

}

REGISTER_VOCABULARY_ITEM = """registerVocabularyTerm(%s, '%s')"""
REGISTER_VOCABULARY_CONTAINER = """registerVocabulary(%s)"""

TEMPL_CONSTR_TOOL = """
    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        %s.__init__(self,'%s')
        """

TEMPLATE_HEADER = """\
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
"""

TEMPLATE_HEADER_I18N_I18N_AT = TEMPLATE_HEADER + """\

from Products.I18NArchetypes.public import *

    """

TEMPLATE_HEADER_I18N_LINGUAPLONE = TEMPLATE_HEADER + """\

try:
    from Products.LinguaPlone.public import *
except ImportError:
    HAS_LINGUAPLONE = False
else:
    HAS_LINGUAPLONE = True

    """

TEMPLATE_CONFIG_IMPORT = """\
from Products.%(module)s.config import *"""


TEMPL_APECONFIG_BEGIN = """<?xml version="1.0"?>

<!-- Basic Zope 2 configuration for Ape. -->

<configuration>"""

TEMPL_APECONFIG_END = """</configuration>"""

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
