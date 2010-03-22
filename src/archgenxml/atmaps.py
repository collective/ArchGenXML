# -*- coding: utf-8 -*-
#
# File: maps.py
#
# some maps needed by the ArchetypesGenerator
#
# Created:     2007/09/09

STATE_PERMISSION_MAPPING = {
    'access'  : 'Access contents information',
    'view'    : 'View',
    'modify'  : 'Modify portal content',
    'list'    : 'List folder contents',
    'add'     : 'Add portal content',
    'delete'  : 'Delete objects',
    'role'    : 'Change local roles',
    'review'  : 'Review portal content',
    'inactive': 'Access inactive portal content',
}

ACTION_STEREOTYPES = [
    'noaction',
    'action',
    'view',
    'form'
]

DEFAULT_ALIASES_2_5 = [
    {'from': '(Default)', 'to': '(dynamic view)'},
    {'from': 'index.html', 'to': '(dynamic view)'},
    {'from': 'view', 'to': '(selected layout)'},
    {'from': 'edit', 'to': 'base_edit'},
    {'from': 'properties', 'to': 'base_metadata'},
]

DEFAULT_ALIASES_3_0 = [
    {'from': '(Default)', 'to': '(dynamic view)'},
    {'from': 'index.html', 'to': '(dynamic view)'},
    {'from': 'view', 'to': '(selected layout)'},
    {'from': 'edit', 'to': 'base_edit'},
]

DEFAULT_FOLDERISH_ALIASES_2_5 = [
    {'from': '(Default)', 'to': '(dynamic view)'},
    {'from': 'view', 'to': '(selected layout)'},
    {'from': 'edit', 'to': 'base_edit'},
    {'from': 'properties', 'to': 'base_metadata'},
    {'from': 'sharing', 'to': 'folder_localrole_form'},
]

DEFAULT_FOLDERISH_ALIASES_3_0 = [
    {'from': '(Default)', 'to': '(dynamic view)'},
    {'from': 'view', 'to': '(selected layout)'},
    {'from': 'edit', 'to': 'base_edit'},
    {'from': 'sharing', 'to': '@@sharing'},
]

# only for Plone >= 3.0
DEFAULT_FOLDERISH_SUPPL_VIEWS = [
    'folder_summary_view',
    'folder_tabular_view',
    'atct_album_view',
    'folder_listing',
]

DEFAULT_ACTIONS_2_5 = [
    {
        'name': 'View',
        'id': 'view',
        'category': 'object',
        'condition': '',
        'action': 'string:${object_url}/view',
        'permissions': ['View'],
        'visible': 'True',
    },
    {
        'name': 'Edit',
        'id': 'edit',
        'category': 'object',
        'condition': '',
        'action': 'string:${object_url}/edit',
        'permissions': ['Modify portal content'],
        'visible': 'True',
    },
    {
        'name': 'Properties',
        'id': 'metadata',
        'category': 'object',
        'condition': '',
        'action': 'string:${object_url}/properties',
        'permissions': ['Modify portal content'],
        'visible': 'True',
    },
]

DEFAULT_ACTIONS_3_0 = [
    {
        'name': 'View',
        'id': 'view',
        'category': 'object',
        'condition': '',
        'action': 'string:${object_url}/view',
        'permissions': ['View'],
        'visible': 'True',
    },
    {
        'name': 'Edit',
        'id': 'edit',
        'category': 'object',
        'condition': 'not:object/@@plone_lock_info/is_locked_for_current_user',
        'action': 'string:${object_url}/edit',
        'permissions': ['Modify portal content'],
        'visible': 'True',
    },
]

"""
TypeMap for Fields, format is
  type: {field: 'Y',
         lines: [key1=value1,key2=value2, ...]
  ...
  }
"""
TYPE_MAP = {
    'string': {
        'field': u'StringField',
        'map': {},
        'index': 'FieldIndex',
    },
    'selection': {
        'field': u'StringField',
        'map': {},
        'index': 'FieldIndex',
    },
    'lines': {
        'field': u'LinesField',
        'map': {},
        'index': 'KeywordIndex',
    },
    'multiselection': {
        'field': u'LinesField',
        'map': {
            u'multiValued': u'1',
        },
        'index': 'KeywordIndex',
    },
    'keywords': {
        'field': u'LinesField',
        'map': {
            u'enforceVocabulary': u'False',
            u'multiValued': u'1',
        },
        'index': 'KeywordIndex',
    },
    'text':  {
        'field': u'TextField',
        'map': {},
        'index': 'ZCTextIndex',
    },
    'richtext': {
        'field': u'TextField',
        'map': {
            u'default_output_type': u"'text/html'",
            u'allowable_content_types': u"('text/plain', 'text/structured'," + \
                                        " 'text/html', 'application/msword',)",
        },
        'index': 'ZCTextIndex',
    },
    'integer': {
        'field': u'IntegerField',
        'map': {},
        'index': 'FieldIndex',
    },
    'float': {
        'field': u'FloatField',
        'map': {},
        'index': 'FieldIndex',
    },
    'fixedpoint': {
        'field': u'FixedPointField',
        'map': {},
        'index': 'FieldIndex',
    },
    'color': {
        'field': u'StringField',
        'map': {},
        'index': 'FieldIndex',
    },
    'country': {
        'field': u'StringField',
        'map': {},
        'index': 'FieldIndex',
    },
    'datagrid': {
        'field': u'DataGridField',
        'map': {},
        'index': None,
    },
    'date': {
        'field': u'DateTimeField',
        'map': {},
        'index': 'DateIndex',
    },
    'image': {
        'field': u'ImageField',
        'map': {
            u'storage': u'AnnotationStorage()', 
        },
        'index': None,
    },
    'file': {
        'field': u'FileField',
        'map': {
            u'storage': u'AttributeStorage()', # XXX
        },
        'index': None,
    },
    'reference': {
        'field': u'ReferenceField',
        'map': {},
        'index': None,
    },
    'relation': {
        'field': u'RelationField',
        'map': {},
        'index': None,
    },
    'backreference': {
        'field': u'BackReferenceField',
        'map': {},
        'index': None,
    },
    'boolean': {
        'field': u'BooleanField',
        'map': {},
        'index': 'FieldIndex',
    },
    'computed': {
        'field': u'ComputedField',
        'map': {},
        'index': None,
    },
    'photo': {
        'field': u'PhotoField',
        'map': {},
        'index': None,
    },
    'generic': {
        'field': None,
        'map': {},
        'index': None,
    },    
    'copy': {
        'field': 'copy',
        'map': {},
        'index': None,
    },
}
TYPE_MAP['rich'] = TYPE_MAP['richtext'] 

WIDGET_MAP = { # only deal with special cases, such as combined field-widgets
    'text': u'TextAreaWidget',
    'rich': u'RichWidget',
    'richtext': u'RichWidget',
    'selection': u'SelectionWidget',
    'multiselection': u'MultiSelectionWidget',
    'keywords': u'KeywordWidget',
    'reference': u'ReferenceBrowserWidget',
    'backreference': u'BackReferenceWidget',
    'BackReference': u'BackReferenceWidget', # deprecated
    'array': u'EnhancedArrayWidget',
#    'file': u'FileWidget',
#    'image': u'ImageWidget',
#    'color': u'ColorPickerWidget',
#    'country': u'CountryWidget',
#    'datagrid': u'DataGridWidget',
#    'date': u'CalendarWidget',
#    'string': u'StringWidget' ,
#    'fixedpoint': u'DecimalWidget' ,
#    'float': u'DecimalWidget',
}

COERCE_MAP = {
    'xs:string': u'string',
    'xs:int': u'integer',
    'xs:integer': u'integer',
    'xs:byte': u'integer',
    'xs:double': u'float',
    'xs:float': u'float',
    'xs:boolean': u'boolean',
    'ofs.image': u'image',
    'ofs.file': u'file',
    'xs:date': u'date',
    'Color': u'color',
    'Country': u'country',
    'DataGrid': u'datagrid',
    'datetime': u'date',
    'list': u'lines',
    'liste': u'lines',
    'image': u'image',
    'int': u'integer',
    'bool': u'boolean',
    'dict': u'string',
    'String': u'string',
    '': u'string',     #
    None: u'string',
}

HIDE_CLASSES = [
    'EARootClass',
    'int',
    'float',
    'boolean',
    'long',
    'bool',
    'void',
    'string',
    'dict',
    'tuple',
    'list',
    'object',
    'integer',
    'java::lang::int',
    'java::lang::string',
    'java::lang::long',
    'java::lang::float',
    'java::lang::void'
]
# Enterprise Architect and other automagically created crap Dummy Class
HIDE_CLASSES += list(TYPE_MAP.keys())+list(COERCE_MAP.keys())

NONSTRING_TGVS = [
    'columns',
    'widget',
    'widget:provideNullValue',
    'widget:allow_brightness',
    'languageIndependent',
    'vocabulary',
    'required',
    'precision', # FIXME: not in TaggedValueSupport
    'storage',
    'enforceVocabulary',
    'multiValued',
    'visible',
    'validators',
    'validation_expression',
    'sizes',
    'original_size',
    'max_size',
    'searchable',
    'widget:show_hm',
    'move:pos',
    'move:top',
    'move:bottom'
    'primary', # FIXME: not in TaggedValueSupport
    'array:widget',
    'array:size', # FIXME: not in TaggedValueSupport
    'widget:starting_year',
    'widget:ending_year',
]
