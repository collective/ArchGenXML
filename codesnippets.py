#-----------------------------------------------------------------------------
# Name:        codesnippets.py
# Purpose:     collects all string based code snippets
# Remark:      this and the stuff in templates directory should go somewhere 
#              in future into a templating language like DTML
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# RCS-ID:      $Id: codesnippets.py,v 1.4 2004/05/23 14:21:08 yenzenz Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------


ACT_TEMPL="""
       {'action':      %(action)s,
        'category':    %(action_category)s,
        'id':          '%(action_id)s',
        'name':        '%(action_label)s',
        'permissions': (%(permission)s,),
        'condition'  : '%(condition)s'},
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
    actions= %s (
        """
        
ACTIONS_END = """
          )
        """
        
DEFAULT_ACTIONS = """
           {'action': 'string:${object_url}/portal_form/base_edit',
          'category': 'object',
          'id': 'edit',
          'name': 'Edit',
          'permissions': ('Manage portal content',)},

           {'action': 'string:${object_url}/base_view',
          'category': 'object',
          'id': 'view',
          'name': 'View',
          'permissions': ('View',)},

        """
        
DEFAULT_ACTIONS_FOLDERISH ="""
           {'action': 'folder_listing',
          'category': 'object',
          'id': 'folder_listing',
          'name': 'Folder Listing',
          'permissions': ('View',)},

        """
        
FTI_TEMPL="""

    # uncomment lines below when you need
    factory_type_information={
        'allowed_content_types':%(subtypes)s %(parentsubtypes)s,
        'allow_discussion': %(discussion)s,
        %(has_content_icon)s'content_icon':'%(content_icon)s',
        'immediate_view':'%(immediate_view)s',
        'global_allow':%(global_allow)d,
        'filter_content_types':%(filter_content_types)d,
        }

        """
        
SCHEMA_START_DEFAULT = """    schema=BaseSchema %s + Schema(("""
SCHEMA_START_I18N    = """    schema=I18NBaseSchema %s + Schema(("""
SCHEMA_START_TGV     = """    schema=%s %s + Schema(("""

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
    
CLASS_PORTAL_TYPE    = """    portal_type = meta_type = '%s' """
CLASS_ARCHETYPE_NAME = """    archetype_name = '%s'   #this name appears in the 'add' box """
CLASS_IMPLEMENTS     = """    __implements__ = %(baseclass_interfaces)s + (%(realizations)s,)"""

REGISTER_ARCHTYPE    = """registerType(%s)\n"""

IMPORT_INTERFACE     = """from Interface import Base"""

MODULE_INFO_HEADER = """\
# File: %(filename)s 
\"""\\
%(purpose)s 

RCS-ID $Id: codesnippets.py,v 1.4 2004/05/23 14:21:08 yenzenz Exp $
\"""
# %(copyright)s
#
# Generated: %(date)s 
# Generator: ArchGenXML Version %(version)s http://sf.net/projects/archetypes/
#
# %(licence)s
#
__author__  = '%(author)s <%(email)s>'
__docformat__ = 'plaintext'

"""

COPYRIGHT  = """Copyright (c) %s by %s"""

GPLTEXT = """\
GNU General Public Licence (GPL)

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA"""

REGISTER_VOCABULARY_ITEM      = """registerVocabularyItem(%s, '%s')"""
REGISTER_VOCABULARY_CONTAINER = """registerVocabulary(%s)"""

TEMPL_CONSTR_TOOL="""
    # tool-constructors have no id argument, the id is fixed
    def __init__(self):
        %s.__init__(self,'%s')
        """

TEMPL_TOOLINIT="""
    tools=[%s]
    utils.ToolInit( PROJECTNAME+' Tools',
                tools = tools,
                product_name = PROJECTNAME,
                icon='tool.gif'
                ).initialize( context )"""

TEMPL_CONFIGLET_INSTALL="""
    portal_control_panel.registerConfiglet( '%(tool_name)s' #id of your Product
        , '%(configlet_title)s' # Title of your Product
        , 'string:${portal_url}/%(configlet_url)s/'
        , '%(configlet_condition)s' # a condition
        , 'Manage portal' # access permission
        , '%(configlet_section)s' # section to which the configlet should be added: (Plone,Products,Members)
        , 1 # visibility
        , '%(tool_name)sID'
        , '%(configlet_icon)s' # icon in control_panel
        , '%(configlet_description)s'
        , None
        )
    # set title of tool:
    tool=getToolByName(self, '%(tool_instance)s')
    tool.title='%(configlet_title)s'

    # dont allow tool listed as content in navtree
    try:
        idx=self.portal_properties.navtree_properties.metaTypesNotToList.index('%(tool_name)s')
        self.portal_properties.navtree_properties._p_changed=1        
    except ValueError:
        self.portal_properties.navtree_properties.metaTypesNotToList.append('%(tool_name)s')
    except:
        raise"""

TEMPL_CONFIGLET_UNINSTALL="""
    portal_control_panel.unregisterConfiglet('%(tool_name)s')

    # remove prodcut from navtree properties
    try:
        self.portal_properties.navtree_properties.metaTypesNotToList.remove('%(tool_name)s')
        self.portal_properties.navtree_properties._p_changed=1        
    except ValueError:
        pass
    except:
        raise"""

TEMPL_DETAILLED_CREATION_PERMISSIONS="""
    # and now give it some extra permissions so that i
    # can control them on a per class limit
    for i in range(0,len(content_types)):
        perm='Add '+ capitalize(ftis[i]['id'])+'s'
        methname='add'+capitalize(ftis[i]['id'])
        meta_type = ftis[i]['meta_type']

        context.registerClass(
            meta_type=meta_type,
            constructors = (
                            getattr(locals()[meta_type],'add'+capitalize(meta_type)),
                               )
            , permission = perm
            )
"""

    
TEMPLATE_HEADER = """\
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
"""

TEMPLATE_HEADER_I18N_I18N_AT = """\
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.I18NArchetypes.public import *

    """

TEMPLATE_HEADER_I18N_LINGUAPLONE = """\
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # Not multilingual
    pass

    """


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











