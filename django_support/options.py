#This File enables DjanGen to use its own Options.
#its one of the thousand hacks needet to override the
#hard-coded AGX Settings

from OptionParser import AGXOptionParser,OptionGroup
import sys
#import textwrap
#import logging
import codesnippets
import utils
#============================================================================
# ArchGenXML Parsing

usage = "usage: %prog [ options ] <xmi-source-file> [output directory]"
description = """A program for generating Archetypes from XMI files.
The xmi file can either be an exported *.xmi file or a Poseidon or ArgoUML
*.zuml file.
"""

version_string = "%prog " + utils.version()

parser = AGXOptionParser(usage=usage,
                         description=description,
                         version=version_string)

parser.add_option("-o",
                  "--outfile",
                  dest="outfilename",
                  metavar="PATH",
                  help="Output directory in which to put everything",
                  section="GENERAL",
                  default='',
                  )

#----------------------------------------------------------------------------
# Config File options

group = OptionGroup(parser, "Configuration File Options")

group.add_option("-c",
        "--cfg",
        dest="config_file",
        help="Use configuration file.",
        action="load_config",
        type="string",
        )

group.add_option( "--sample-config",
        help="Show sample configuration file.",
        action="sample_config",
        )

parser.add_option_group(group)


#----------------------------------------------------------------------------
# Parsing Options

group = OptionGroup(parser, "Parsing Options")

group.add_option("-t",
                 "--unknown-types-as-string",
                 dest="unknownTypesAsString",
                 type="yesno",
                 help="Treat unknown attribute types as strings (default is 0).",
                 default=0,
                 section="CLASSES",
        )

group.add_option("--generate-packages",
                 help="Name of packages to generate (can specify as comma-separated list, or specify several times)",
                 section="GENERAL",
                 action="append",
                 dest="generate_packages",
                 type="commalist",
                 )

# XXX: When would this be the right option to use, as opposed to
# generate-packages, above? - WJB

group.add_option("-P",
                 "--parse-packages",
                 type="commalist",
                 action="append",
                 metavar="GENERAL",
                 dest="parse_packages",
                 help="Names of packages to scan for classes (can specify "
                 "as comma-separated list, or specify several times). "
                 "FIXME: Leaving this empty probably means that all "
                 "packages are scanned.",
                 section="GENERAL",
                 )

group.add_option("-f",
                 "--force",
                 help="Overwrite existing files? (Default is 1).",
                 default=1,
                 type="yesno",
                 section="GENERAL",
                 )

parser.add_option_group(group)

#----------------------------------------------------------------------------
# Generation Options

group = OptionGroup(parser, "Generation Options")

#group.add_option("--widget-enhancement",
#                 dest="widget_enhancement",
#                 type="yesno",
#                 default=1,
#                 help="Create widgets with default label, label_msgid, description,"
#                 " description_msgid, and i18ndomain (default is 1).",
#                 section="CLASSES",
#                 )

group.add_option("--generate-actions",
                 type='yesno',
                 dest="generateActions",
                 default=1,
                 help="Generate actions (default is 1)",
                 section="CLASSES",
                 )

group.add_option("--default-actions",
                 help="Generate default actions explicitly for each class (default is 0).",
                 dest="generateDefaultActions",
                 type="yesno",
                 default=0,
                 section="CLASSES",
                 ),

group.add_option("--customization-policy",
                 dest="customization_policy",
                 type="yesno",
                 default=0,
                 help="Generate a customization policy (default is 0).",
                 section="GENERAL",
                 )

group.add_option("--rcs-id",
                 dest="rcs_id",
                 type="yesno",
                 help="Add RCS $Id$ tags to the generated file (default is 0).",
                 default=0,
                 section="GENERAL",
                 )

group.add_option("--version-info",
                 dest="version_info",
                 type="yesno",
                 help="Add ArchGenXML version information to the generated file (default is 1).",
                 default=1,
                 section="GENERAL",
                 )

group.add_option("--generated_date",
                 dest="generated_date",
                 type="yesno",
                 help="Add generation date to generated files (default is 0).",
                 default=0,
                 section="GENERAL",
                 )

group.add_option("--strip-html",
                 type="yesno",
                 help="Strip HTML tags from documentation strings, "
                 "handy for UML editors, such as Poseidon, which store HTML "
                 "inside docs (default is 0).",
                 default=0,
                 section="DOCUMENTATION",
                 )

group.add_option("--method-preservation",
                 help="Preserve methods in existing source files (default is 1).",
                 dest="method_preservation",
                 type="yesno",
                 default=1,
                 section="CLASSES",
                 )

group.add_option("--backreferences-support",
                 dest="backreferences_support",
                 type="yesno",
                 help="For references, create a back reference field on the "
                 "referred-to class. Requires ATBackRef product "
                 "(http://www.plone.org/products/atbackref) to work. "
                 "(Default is 0).",
                 section="CLASSES",
                 )

group.add_option("--default-field-generation",
                 dest="default_field_generation",
                 help="Always generate 'id' and 'title' fields (default is 0).",
                 type="yesno",
                 default=0,
                 section="CLASSES",
                 )

group.add_option("--default-description-generation",
                 dest="default_description_generation",
                 help="Generate the default widget descriptions (default is 0).",
                 type="yesno",
                 default=0,
                 section="CLASSES",
                 )

group.add_option("--default-class-type",
                 dest="default_class_type",
                 help="Changes the default class type from content_class to "
                      "your value. Useful when most of your classes are not "
                      "archetype content.",
                 type="string",
                 default="python_class",
                 section="CLASSES",
                 )

parser.add_option_group(group)

#----------------------------------------------------------------------------
# i18n Options

#group = OptionGroup(parser, "Internationalization Options")
#
#group.add_option("--message-catalog",
#                 dest="build_msgcatalog",
#                 help="Automatically build msgid catalogs (default is 1).",
#                 type="yesno",
#                 default=1,
#                 section="I18N",
#                 )
#
#group.add_option("--i18n-content-support",
#                 help="Support for internationalised archetypes."
#                 "Attributes with a stereotype of 'i18n' "
#                 "or taggedValue of i18n=1 will be multilingual. "
#                 "Possible values for this option are 'linguaplone' "
#                 "and 'i18n-archetypes'.",
#                 type="string",
#                 dest="i18n_content_support",
#                 default='',
#                 section="I18N",
#                 )
#
#parser.add_option_group(group)

#----------------------------------------------------------------------------
# Module information options

group = OptionGroup(parser, "Customization Options",
                    "These options set the defaults for the module information headers."
                    " They can be overriden by taggedValues."
                    )

group.add_option("--module-info-header",
                 dest="module_info_header",
                 default=1,
                 type="yesno",
                 help="Generate module information header",
                 section="DOCUMENTATION",
                 )

group.add_option("--author",
                 type="commalist",
                 action="append",
                 dest="author",
                 help="Set default author value (can specify as comma-separated list, "
                 "or specify several times).",
                 default=[],
                 section="DOCUMENTATION",
                 )

# Added US spelling of email as alternate

group.add_option("--e-mail",
                 "--email",
                 dest="email",
                 help="Set default email (can specify as comma-separated list, "
                 "or specify several times).",
                 type="commalist",
                 action="append",
                 default=[],
                 section="DOCUMENTATION",
                 )

group.add_option("--copyright",
                 dest="copyright",
                 help="Set default copyright",
                 default='',
                 type="string",
                 section="DOCUMENTATION",
                 )

# Added US spelling of license as alternate

group.add_option("--license",
                 "--licence",
                 help="Set default license (default is the GPL).",
                 default='GPL',
                 section="DOCUMENTATION",
                 type="choice",
                 choices=codesnippets.LICENSES.keys(),
                 )

parser.add_option_group(group)



#----------------------------------------------------------------------------
# Permission options

#group = OptionGroup(parser, "Permissions")
#
#group.add_option("--default-creation-permission",
#                 dest="default_creation_permission",
#                 help="Specifies default permission to create content"
#                 " (defaults to 'Add portal content.'). "
#                 "Warning: it used to be 'Add [CREATION_PERMISSION] content', "
#                 "so with the 'Add' and 'content' automatically added.",
#                 default="Add portal content",
#                 type="string",
#                 section="CLASSES",
#                 )
##XXX handle creation_permission the right way.
#
#group.add_option("--default-creation-roles",
#                 dest="creation_roles",
#                 help="Specifies the default roles that creates content",
#                 default="python:('Manager','Owner')",
#                 type="string",
#                 section="CLASSES",
#                 )
#
#group.add_option("--detailed-creation-permissions",
#                 type="yesno",
#                 help="Separate creation permissions per class (defaults to no)",
#                 default=0,
#                 section="CLASSES",
#                 dest="detailed_creation_permissions",
#                 )
#
#parser.add_option_group(group)

#----------------------------------------------------------------------------
# Storage Options

#group = OptionGroup(parser, "Storage Options")
#
#group.add_option("--ape-support",
#                 dest="ape_support",
#                 type="yesno",
#                 help="Generate configuration and generators for APE (default is 0).",
#                 section="STORAGE",
#                 default=0,
#                 )
#
#group.add_option("--sql-storage-support",
#                 dest="sql_storage_support",
#                 type="yesno",
#                 help="FIXME: not sure it this is used. (default is 0)",
#                 section="CLASSES",
#                 default=0,
#                 )
#
#parser.add_option_group(group)

#----------------------------------------------------------------------------
# Relation Options

group = OptionGroup(parser, "Relations")

group.add_option("--relation-implementation",
                 dest="relation_implementation",
                 help="specifies how relations should be implemented"
                 "(default is 'basic').",
                 type="string",
                 section="CLASSES",
                 default='basic',
                 )

parser.add_option_group(group)

#----------------------------------------------------------------------------
# General Options

group = OptionGroup(parser, "General Options")

group.add_option("--pdb-on-exception",
                 dest="pdb_on_exception",
                 type="yesno",
                 help="Start the pdb in post mortem mode in case of an "
                 "uncaught exception",
                 section="GENERAL",
                 default=0,
                 )

parser.add_option_group(group)

#----------------------------------------------------------------------------
# Deprecated options

#group = OptionGroup(parser, "Deprecated")
#
#group.add_option("--ape",
#                 help="Use --ape-support=1",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--actions",
#                 help="Use --generate-actions=1",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--no-actions",
#                 help="Use --generate-actions=0",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--no-widget-enhancement",
#                 help="Use --widget-enhancement=0",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--no-method-preservation",
#                 help="Use --method-preservation=0",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--no-message-catalog",
#                 help="Use --message-catalog=0",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--no-module-info-header",
#                 help="Use --module-info-header=0",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--no-rcs-id",
#                 help="Use --rcs-id=0",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--no-generated-date",
#                 help="Use --generated-date=0",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--creation-permission",
#                 help="Use --default-creation-permission",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--detailled-creation-permission",
#                 help="Use --detailed-creation-permissions",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--detailed-created-permissions",
#                 type="yesno",
#                 help="Use"
#                 " --detailed-creation-permissions, which generates a"
#                 " slightly different syntax, though.",
#                 default=0,
#                 section="CLASSES",
#                 dest="detailed_created_permissions",
#                 )
#
#group.add_option("--noclass",
#                 help="Never really implemented.",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--no-classes",
#                 dest="noclass",
#                 help="Never really implemented, intention "
#                 "was to generate a plain skeleton. Use an empty "
#                 "UML model instead (with one stub class, archgenxml "
#                 "doesn't like a completely empty model).",
#                 type="yesno",
#                 default=0,
#                 section="CLASSES",
#                 )
#
#group.add_option("--i18n",
#                 help="Use --i18n-content-support",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--project-configuration",
#                 help="Use --cfg",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )
#
#group.add_option("--storage",
#                 help="Really don't know. Perhaps --ape-support?",
#                 action="deprecationwarning",
#                 section="DEPRECATED"
#                 )

parser.add_option_group(group)

#----------------------------------------------------------------------------
# FIXME: Broken/undocumented options

#group = OptionGroup(parser, "Possibly broken options")
#
## FIXME: This feature doesn't seem working currently in ArchGenXML--the
## class def gets the prefix, but nothing else does.
#
#group.add_option("--prefix",
#                 help="Adds PREFIX before each class name (default is '').",
#                 default='',
#                 type="string",
#                 dest="prefix",
#                 section="GENERAL",
#                 )
#
#parser.add_option_group(group)

#Django specific Options
group = OptionGroup(parser, "DjanGenXML Specific")
group.add_option("--i18n-language",
                 help="""Sets if the Labels and help Texts are automatically
                 converted to a language, gettext means that gettext will handle this live
                 !now just 'gettext' works, sorry""",
                 default='gettext',
                 type="string",
                 dest="i18n_language",
                 section="DJANGO I18N",
                 )

group.add_option("--i18n-generate-language-file",
                 help="""Sets if set the Djangen will generate a language File for each
                 application/package in the package Dir !Not implemented yet.""",
                 default='gettext',
                 type="string",
                 dest="i18n_language_file",
                 section="DJANGO I18N",
                 )


group.add_option("--startproject",
                 help="Use the UML-Diagramm to Start a Django-Project instantly. "
                  "Apps are added to the settings.py automatically. "
                  "Values are yes, no and auto (default)",
                 default='auto',
                 type="string",
                 dest="startproject",
                 section="DJANGO",
                 )

group.add_option("--null-is-blank",
                 help="For Assocs: If Bounds are 0..? should they be blank in Admin. (default: yes)",
                 default=1,
                 type="yesno",
                 dest="null_is_blank",
                 section="DJANGO",
                 )
group.add_option("--autodoc",
                 help="Display Automated Documentation of DjangenXML (if set to yes...)\n"
                 "Be shure to add a filename or pseudo-filename. It isn't parsed but needet...\n"
                 "*sing* this i such an early release...\n"
                 "Best use is DjangenXML.py --autodoc=yes x > doc.txt for saving this",
                 default=0,
                 type="yesno",
                 dest="autodoc",
                 section="DJANGO",
                 )

parser.add_option_group(group)

if __name__ == '__main__':
    (settings, args) = parser.parse_args()
    print settings
