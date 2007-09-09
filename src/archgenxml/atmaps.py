# -*- coding: utf-8 -*-
#
# File: maps.py
#
# some maps needed by the ArchetypesGenerator
#
# Created:     2007/09/09

"""
TypeMap for Fields, format is
  type: {field: 'Y',
         lines: [key1=value1,key2=value2, ...]
  ...
  }
"""
typeMap= {
    'string': {'field': u'StringField',
               'map': {},
               },
    'text':  {'field': u'TextField',
              'map': {},
              },
    'richtext': {'field': u'TextField',
                 'map': {u'default_output_type': u"'text/html'",
                         u'allowable_content_types': u"('text/plain', 'text/structured', 'text/html', 'application/msword',)",
                         },
                 },
    'selection': {'field': u'StringField',
                  'map': {},
                  },
    'multiselection': {'field': u'LinesField',
                       'map': {u'multiValued': u'1',
                               },
                       },
    'integer': {'field': u'IntegerField',
                'map': {},
                },
    'float': {'field': u'FloatField',
              'map': {},
              },
    'fixedpoint': {'field': u'FixedPointField',
                   'map': {},
                   },
    'lines': {'field': u'LinesField',
             'map': {},
             },
    'color': {'field': u'StringField',
             'map': {},
             },
    'country': {'field': u'StringField',
             'map': {},
             },
    'datagrid': {'field': u'DataGridField',
             'map': {},
             },
    'date': {'field': u'DateTimeField',
             'map': {},
             },
    'image': {'field': u'ImageField',
              'map': {u'storage': u'AttributeStorage()',
                      },
              },
    'file': {'field': u'FileField',
             'map': {u'storage': u'AttributeStorage()',
                     },
             },
    'reference': {'field': u'ReferenceField',
                  'map': {},
                  },
    'relation': {'field': u'RelationField',
                 'map': {},
                 },
    'backreference': {'field': u'BackReferenceField',
                      'map': {},
                      },
    'boolean': {'field': u'BooleanField',
                'map': {},
                },
    'computed': {'field': u'ComputedField',
                 'map': {},
                 },
    'photo': {'field': u'PhotoField',
              'map': {},
              },
    'generic': {'field': u'%(type)sField',
                'map': {},
                },
    }

widgetMap={
    'string': u'StringWidget' ,
    'fixedpoint': u'DecimalWidget' ,
    'float': u'DecimalWidget',
    'text': u'TextAreaWidget',
    'richtext': u'RichWidget',
    'file': u'FileWidget',
    'image': u'ImageWidget',
    'color': u'ColorPickerWidget',
    'country': u'CountryWidget',
    'datagrid': u'DataGridWidget',
    'date': u'CalendarWidget',
    'selection': u'SelectionWidget',
    'multiselection': u'MultiSelectionWidget',
    'BackReference': u'BackReferenceWidget'
}

coerceMap={
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

hide_classes=['EARootClass','int','float','boolean','long','bool',
    'void','string', 'dict','tuple','list','object','integer',
    'java::lang::int','java::lang::string','java::lang::long',
    'java::lang::float','java::lang::void']+\
    list(typeMap.keys())+list(coerceMap.keys()) # Enterprise Architect and other automagically created crap Dummy Class