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
from archgenxml.TaggedValueSupport import tgvRegistry
from archgenxml import loginitializer
loginitializer.addConsoleLogging()
import logging
log = logging.getLogger("argouml")

outfile = sys.argv[1:] or 'argouml_profile.xmi'

## Base file construction for ArgoUMl profile
## variable: {stereotypes, datatypes, definitions}
BASE_FILE = """<?xml version="1.0" encoding="utf-8"?>

<!-- ArchGenXML Old logs
     version 0.1 2006/02/24 Pander inintial version
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
<XMI xmlns:UML="org.omg.xmi.namespace.UML" xmi.version="1.2" timestamp="Fri Sep 02 22:10:50 CEST 2005">
  <XMI.header>
    <XMI.documentation>
      <XMI.exporter>UML 1.3 to UML 1.4 stylesheets</XMI.exporter>
      <XMI.exporterVersion>0.3</XMI.exporterVersion>
    </XMI.documentation>
    
  </XMI.header>
  <XMI.content>
    <UML:Model isSpecification="false" isRoot="false" isLeaf="false" isAbstract="false" name="default" xmi.id="-6x--88-11--16-e9dbfe:e2d71a1c1e:-7fff">
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
STEREOTYPE_GENERIC = """        <UML:Stereotype isSpecification="false" isRoot="false" isLeaf="false" isAbstract="false" name="%(name)s" xmi.id="xmi.%(index)d">
          <UML:Stereotype.baseClass>%(type)s</UML:Stereotype.baseClass>
          <UML:ModelElement.namespace>
            <UML:Namespace xmi.idref="-6x--88-11--16-e9dbfe:e2d71a1c1e:-7fff"/>
          </UML:ModelElement.namespace>
        </UML:Stereotype>"""


## Datatypes
## variables: {name, index}
## name is a string
## index is an integer
DATATYPE = """        <UML:DataType isSpecification="false" isRoot="false" isLeaf="false" isAbstract="false" name="%(name)s" xmi.id="xmi.%(index)d">
          <UML:ModelElement.namespace>
            <UML:Namespace xmi.idref="-6x--88-11--16-e9dbfe:e2d71a1c1e:-7fff"/>
          </UML:ModelElement.namespace>
        </UML:DataType>"""

## Tag definition
## variables: {name, index}
## name is a string
## index is an integer
DEFINITION = """        <UML:TagDefinition xmi.id = 'xmi.%(index)d' name = '%(name)s' isSpecification = 'false' tagType = 'String'>
          <UML:ModelElement.namespace>
            <UML:Namespace xmi.idref="-6x--88-11--16-e9dbfe:e2d71a1c1e:-7fff"/>
          </UML:ModelElement.namespace>
          <UML:TagDefinition.multiplicity>
            <UML:Multiplicity xmi.id = 'xmi.%(index)d.1'>
              <UML:Multiplicity.range>
                <UML:MultiplicityRange xmi.id = 'xmi.%(index)d.2' lower = '0' upper = '1'/>
              </UML:Multiplicity.range>
            </UML:Multiplicity>
          </UML:TagDefinition.multiplicity>
        </UML:TagDefinition>"""


def main():
    """
    """
    #datatype_categories = ('datatype',)

    log.info("Starting to generate '%s'." % outfile)

    from archgenxml import zopeimportfixer
    from archgenxml.ArchetypesGenerator import at_uml_profile
    stereotype_categories = at_uml_profile.getCategories()
    stereotypes = []
    index = 300
    for category in stereotype_categories:
        type_ = category
        type_ = type_.capitalize() 
        elements = at_uml_profile.getCategoryElements(category)
        for element in elements:
            name = element['name']
            stereotypes.append(STEREOTYPE_GENERIC % {
                'type': type_,
                'name': name,
                'index': index,
                })
            index = index + 1

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
    index = 360
    for datatype_name in datatype_names:
        datatypes.append(DATATYPE % {
                        'name': datatype_name,
                        'index': index,
                        })
        index = index + 1

    taggedvalue_categories = tgvRegistry.getCategories()
    definitions = []
    index = 400
    for category in taggedvalue_categories:
        for name in tgvRegistry.getCategoryElements(category):
            definitions.append(DEFINITION % {
                'name': name,
                'index': index,
                })
            index = index + 1
    ## One for rules them all
    f = file(outfile, 'w')
    f.write(BASE_FILE % {
        'logs': '',
        'stereotypes': '\n'.join(stereotypes),
        'datatypes': '\n'.join(datatypes),
        'definitions': '\n'.join(definitions),
        })
    f.flush()
    f.readlines
    f.close()



if __name__ == '__main__':
    main()
