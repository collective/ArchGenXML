#!/usr/bin/env python
# -*- coding: utf-8 -*-
## ArchGenXML
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Generate argouml_profile.xmi from TaggedValueSupport.py
"""
__version__ = "$Revision:  $"
# $Source:  $
# $Id:  $
__docformat__ = 'restructuredtext'

import sys
import os.path
from datetime import datetime
from archgenxml.TaggedValueSupport import tgvRegistry
from archgenxml import loginitializer
loginitializer.addConsoleLogging()
import logging
log = logging.getLogger("argouml")

outfile = sys.argv[1:] or 'archgenxml_profile.xmi'

try:
    import uuid
except ImportError:
    import uuidfrompy252 as uuid

# This uuid was generated initially by uuid.uuid4()
NAMESPACE_AGX = uuid.UUID('{342db3ca-4022-4992-a166-c38c7db692f8}')

def new_uuid(s):
    """Return always the same string uuid for the given string 's'
    """
    return str(uuid.uuid5(NAMESPACE_AGX, s))

## Base file construction for ArgoUML profile
## variable: {stereotypes, datatypes, definitions}
BASE_FILE = """<?xml version = '1.0' encoding = 'UTF-8' ?>

<!-- ArchGenXML Old logs
     version 0.1 2006/02/24 Pander initial version
     version 0.2 2006/03/03 Pander completed stereotypes and data types
     version 0.3 2006/03/03 Pander completed tag definitions
     version 0.4 2006/03/06 Pander improved data types
     version 0.5 2006/03/17 Pander added tag definition i18ncontent
     version 0.6 2006/03/25 Pander fixed duplicate id for tag definition i18ncontent
     version 0.7 2006/03/25 Pander added default:widget:Reference, widget:size
     version 0.8 2006/08/02 Pander added widget:maxlength
     version 0.9 2006/08/28 Pander added for widget: rows, cols, divider, append_only, format, future_years, starting_year, ending_year, show_ymd, show_hm, thousands_commas, whole_dollars, dollars_and_cents, addable, allow_file_upload
     version 1.0 2006/08/28 Pander added languageIndependent
     version 1.1 2006/0?/?? Pander added storage
     version 1.2 2007/01/22 Pander added widget:visible
     version 1.3 2007/02/19 Xiru added access, Modify
     version 1.4 2007/02/19 Pander renamed allowed_content_types into allowable_content_types, added default_content_type and default_output_type
     version 1.5 2007/03/01 Pander added columns, allow_empty_rows, widget:auto_insert, widget:columns
     version 1.6 2007/03/05 Pander added data type datagrid, country and color and tagged values widget:provideNullValue, widget:nullValueTitle, widget:omitCountries and allow_brightness
     version 1.7 2007/03/14 Encolpe added allowed_types for ReferenceField
     version 1.8 2007/03/23 Encolpe added relationship for ReferenceField
     version 1.9 2007/03/28 Pander added default_page_type
     version 1.10 2007/04/06 Encolpe fixed renaming allowed_content_types into allowable_content_types: they are not used in the same semantic
     Now this profile is generated with ArgoUMLProfileGenerator.py script
-->
<XMI xmi.version = '1.2' xmlns:UML = 'org.omg.xmi.namespace.UML' timestamp = '%(timestamp)s'>
  <XMI.header>
    <XMI.documentation>
      <XMI.exporter>ArgoUMLProfileGenerator.py</XMI.exporter>
      <XMI.exporterVersion>0.5</XMI.exporterVersion>
    </XMI.documentation>
    <XMI.metamodel xmi.name="UML" xmi.version="1.4"/>
  </XMI.header>
  <XMI.content>
    <UML:Model xmi.id = '342db3ca-4022-4992-a166-c38c7db692f8' name = 'AGXProfile'
      isSpecification = 'false' isRoot = 'false' isLeaf = 'false' isAbstract = 'false'>
      <UML:Namespace.ownedElement>

	<!-- Stereotypes for ArchGenXML -->
%(stereotypes)s

	<!-- Data types for ArchGenXML -->
%(datatypes)s

	<!-- Tag definitions for ArchGenXML -->
%(definitions)s
      </UML:Namespace.ownedElement>
    </UML:Model>
  </XMI.content>
</XMI>
"""


## Stereotypes
## variables: {type, name, index}
## type is a string between: Model, Package, Interface, Class or Operation
## name is a string
## index is an integer
STEREOTYPE_GENERIC = """        <UML:Stereotype xmi.id = '%(uuid)s' name = '%(name)s'
          isSpecification = 'false' isRoot = 'false' isLeaf = 'false' isAbstract = 'false'>
          <UML:Stereotype.baseClass>%(type)s</UML:Stereotype.baseClass>
        </UML:Stereotype>"""


## Datatypes
## variables: {name, index}
## name is a string
## index is an integer
DATATYPE = """        <UML:DataType xmi.id = '%(uuid)s' name = '%(name)s'
          isSpecification = 'false' isRoot = 'false' isLeaf = 'false' isAbstract = 'false'/>"""

## Tag definition
## variables: {name, index}
## name is a string
## index is an integer
DEFINITION = """        <UML:TagDefinition xmi.id = '%(uuid)s' name = '%(name)s'
          isSpecification = 'false' tagType = 'String'>
          <UML:TagDefinition.multiplicity>
            <UML:Multiplicity xmi.id = '%(uuid1)s'>
              <UML:Multiplicity.range>
                <UML:MultiplicityRange xmi.id = '%(uuid2)s' lower = '0'
                  upper = '1'/>
              </UML:Multiplicity.range>
            </UML:Multiplicity>
          </UML:TagDefinition.multiplicity>
        </UML:TagDefinition>"""


def main():
    """
    """

    log.info("Starting to generate '%s'." % outfile)

    from archgenxml.ArchetypesGenerator import at_uml_profile
    stereotype_categories = at_uml_profile.getCategories()
    stereotypes = []
    for category in stereotype_categories:
        type_ = category
        type_ = type_.capitalize() 
        elements = at_uml_profile.getCategoryElements(category)
        for element in elements:
            name = element['name']
            stereotypes.append(STEREOTYPE_GENERIC % {
                'type': type_,
                'name': name,
                'uuid': new_uuid(type_ + name),
                })

    datatype_names = [
        'backreference',
        'boolean',
        'color',
        'computed',
        'country',
        'copy',
        'datagrid',
        'date',
        'file',
        'fixedpoint',
        'float',
        'generic',
        'image',
        'int',
        'lines',
        'multiselection',
        'keywords',
        'photo',
        'reference',
        'relation',
        'richtext',
        'selection',
        'string',
        'text',
        'void',
        ]
    datatypes = []
    for datatype_name in datatype_names:
        datatypes.append(DATATYPE % {
                        'name': datatype_name,
                        'uuid': new_uuid(datatype_name),
                        })

    taggedvalue_categories = tgvRegistry.getCategories()
    definitions = {}
    for category in taggedvalue_categories:
        for name in tgvRegistry.getCategoryElements(category):
            if name in definitions:
                continue
            definitions[name] = DEFINITION % {
                'name': name,
                'uuid': new_uuid(name),
                'uuid1': new_uuid(name + '.1'),
                'uuid2': new_uuid(name + '.2'),
                }
    ## One for rules them all
    f = file(outfile, 'w')
    f.write(BASE_FILE % {
        'timestamp': datetime.now().ctime(),
        'stereotypes': '\n'.join(stereotypes),
        'datatypes': '\n'.join(datatypes),
        'definitions': '\n'.join(definitions.values()),
        })
    f.flush()
    f.close()


if __name__ == '__main__':
    main()
