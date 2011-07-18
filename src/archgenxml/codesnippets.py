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

MODIFY_FTI = u"""\
def modify_fti(fti):
    # Hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in [%(hideactions)s]:
            a['visible'] = 0
    return fti
"""

ACTIONS_START = u"""
    actions = %s (
"""

ACTIONS_END = u"""
    )
"""

DEFAULT_ACTIONS = u"""
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

DEFAULT_ACTIONS_FOLDERISH = u"""
       {'action': 'string:${folder_url}/folder_listing',
        'category': 'folder',
        'condition': 'object/isPrincipiaFolderish',
        'id': 'folderlisting',
        'name': 'Folder Listing',
        'permissions': ('View',)
       },

"""

CLASS_SCHEMA = u"""\
    schema = %(prefix)s + schema %(postfix)s
"""

SCHEMA_START = u"""schema = Schema((
"""

EXTENDER_SCHEMA_START = u"""    schema = ["""

SCHEMA_TOOL = u"""\
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

TEMPL_TOOL_HEADER=u"""
from Products.CMFCore.utils import UniqueObject

    """

CLASS_META_TYPE = u"""    meta_type = '%s'"""
CLASS_FOLDER_TABS = u"""    use_folder_tabs = %s\n"""
CLASS_IMPLEMENTS = u"""    __implements__ = %(baseclass_interfaces)s + (%(realizations)s,)"""
CLASS_IMPLEMENTS_BASE = u"""    __implements__ = %(baseclass_interfaces)s"""
CLASS_ALLOWED_CONTENT_TYPES = u'''    allowed_content_types = %s%s'''
CLASS_ALLOWED_CONTENT_INTERFACES = u'''    allowed_interfaces = [%s] %s'''
CLASS_RENAME_AFTER_CREATION = u'''    _at_rename_after_creation = %s\n'''

REGISTER_ARCHTYPE = u"""registerType(%s, PROJECTNAME)\n"""

IMPORT_INTERFACE = u"""from Interface import Base"""

ENCODING_HEADER = u"""\
# -*- coding: %(encoding)s -*-
"""

MODULE_INFO_HEADER = u'''\
#
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

COPYRIGHT = u"""Copyright (c) %s by %s"""

GPLTEXT = u"""\
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

LGPLTEXT = u"""\
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

AGPLTEXT = u"""\
# This file is part of a program which is free software: you can
# redistribute it and/or modify it under the terms of the
# GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>."""

BSDTEXT = u"""\
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

ZPLTEXT = u"""\
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE."""

DFSLTEXT = u"""\
# This Program may be used by anyone in accordance with the terms of the
# German Free Software License
# The License may be obtained under <http://www.d-fsl.org>."""

LICENSES = {
    # THE AUTHORS OF ARCHGENXML ALLOW TO AUTOMATICALLY RE-LICENCE THE CODE
    # WHILE GENERATION TO ONE OUT OD THE FOLLOWING LICENCES:
    # OTHER OSI-CERTIFED LICENCES ARE ALLOWED TOO, ADD THEM HERE.

    'GPL': {
        'name': u'GNU General Public License (GPL)',
        'text': GPLTEXT,
    },

    'LGPL': {
        'name': u'GNU Lesser General Public License (LGPL)',
        'text': LGPLTEXT,
    },

    'AGPL': {
        'name': u'GNU Affero General Public License (AGPL)',
        'text': AGPLTEXT,
    },

    'BSD': {
        'name': u'Berkeley Software Distribution License (BSD)',
        'text': BSDTEXT,
    },

    'ZPL': {
        'name': u'Zope Public License (ZPL)',
        'text': ZPLTEXT,
    },
    'DFSL': {
        'name': u'German Free Software License (D-FSL)',
        'text': DFSLTEXT,
    },
}

REGISTER_VOCABULARY_ITEM = u"""registerVocabularyTerm(%s, '%s')"""
REGISTER_VOCABULARY_CONTAINER = u"""registerVocabulary(%s)"""

TEMPL_CONSTR_TOOL = u"""
    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        %s.__init__(self,'%s')
        self.setTitle('%s')
"""

TEMPL_POST_EDIT_METHOD_TOOL = u"""
    # tool should not appear in portal_catalog
    def at_post_edit_script(self):
        self.unindexObject()
"""

TEMPLATE_HEADER = u"""\
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
"""

TEMPLATE_HEADER_I18N_I18N_AT = TEMPLATE_HEADER + u"""\

from Products.I18NArchetypes.public import *

"""

TEMPLATE_HEADER_I18N_LINGUAPLONE = TEMPLATE_HEADER + u"""\

try:
    from Products.LinguaPlone.public import *
except ImportError:
    HAS_LINGUAPLONE = False
else:
    HAS_LINGUAPLONE = True

"""

TEMPLATE_CONFIG_IMPORT = u"""\
from Products.%(module)s.config import *

"""

TEMPLATE_CMFDYNAMICVIEWFTI_IMPORT = u"""\
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
"""

REMEMBER_IMPORTS = u"""\
# imports needed by remember
from Products.remember.content.member import BaseMember
from Products.remember.permissions import \\
        VIEW_PUBLIC_PERMISSION, EDIT_ID_PERMISSION, \\
        EDIT_PROPERTIES_PERMISSION, VIEW_OTHER_PERMISSION,  \\
        VIEW_SECURITY_PERMISSION, EDIT_PASSWORD_PERMISSION, \\
        EDIT_SECURITY_PERMISSION, MAIL_PASSWORD_PERMISSION, \\
        ADD_MEMBER_PERMISSION
from AccessControl import ModuleSecurityInfo
"""

REMEMBER_CALL = u"""
    # A member's __call__ should not render itself, this causes recursion
    def __call__(self, *args, **kwargs):
        return self.getId()
        """

ARRAYFIELD = u"""    ArrayField(
%s
%s
    ),

"""

REFERENCEBROWSERWIDGET_IMPORT = u"""\
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
"""

EXTENDFIELDS_FUNCTION = u"""\
from new import classobj
from copy import deepcopy
def extendFields(parentClass,excludedFields=[]):
    ''' returns a list of AT fields which copy those fields from
    parentClass whose names are not present in excludedFields '''
    parentSchema = parentClass.schema
    result = []
    # iterate over the fields of parent class
    for parentField in parentSchema.fields():
        if parentField.getName() in excludedFields:
            continue # skip this one, the adapted class already has it
        parentFieldClass = parentField.__class__
        parentFieldClassName = parentFieldClass.__name__
        # for schema extenders, fields must inherit from ExtensionField, too
        fieldClassName = 'Extended' + parentFieldClassName
        # here is the python magic: let's instantiate a new class !
        fieldClass = classobj(fieldClassName,(ExtensionField,parentFieldClass),{})
        field=fieldClass()
        field.__dict__ = deepcopy(parentField.__dict__) # a bit wild, isn't it ?
        result.append(field)
    return result

"""
