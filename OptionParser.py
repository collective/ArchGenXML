#!/usr/bin/python

# Requires Python 2.3

from optparse import OptionParser, \
        OptionGroup, \
        Option, \
        SUPPRESS_HELP, \
        OptionValueError, \
        TitledHelpFormatter

from ConfigParser import SafeConfigParser as ConfigParser

import textwrap
import sys

#============================================================================
# Custom Parsers

class AGXHelpFormatter(TitledHelpFormatter):
    """Help formatter for ArchGenXML parser."""

    # subclassed to handle YES|NO values
    
    def format_option_strings (self, option):
        """Return a comma-separated list of option strings & metavariables."""

        # Overridden to provide formatting for yesno fields.

        if option.type == 'yesno':
            metavar = "YES|NO"
            short_opts = [sopt + metavar for sopt in option._short_opts]
            long_opts = [lopt + "=" + metavar for lopt in option._long_opts]
        elif option.takes_value():
            metavar = option.metavar or option.dest.upper()
            short_opts = [sopt + metavar for sopt in option._short_opts]
            long_opts = [lopt + "=" + metavar for lopt in option._long_opts]
        else:
            short_opts = option._short_opts
            long_opts = option._long_opts

        if self.short_first:
            opts = short_opts + long_opts
        else:
            opts = long_opts + short_opts

        return ", ".join(opts)

class AGXOption(Option):
    """Option parser option class for ArchGenXML parser."""

    # Subclassed to handle YES|NO fields, commalist fields, and to handle
    # sample_config file action.
    
    def check_yesno(option, opt, value):
        yesno={'yes':1, 'y':1, 1:1, '1':1, 'no':None, 'n':None, 0:None, '0':None}

        if yesno.has_key(value.lower()):
            return yesno[value.lower()]
        else:
            choices=", ".join(map(repr, yesno.keys()))
            raise OptionValueError(
                    "option %s: invalid choice: %r (choose from %s)" % 
                    (opt, value, choices))

                    
    #def check_commalist(option, opt, value):
    #    return value
                   
    def take_action(self, action, dest, opt, value, values, parser):
        """Perform option."""

        # Overridden to provide sample_config option and to handle
        # commalist as a list.

        if action == "sample_config":
            print parser.sample_config()
            sys.exit(0)
        elif action == "load_config":
            parser.read_project_configfile(value, values)
        elif action == "append" and self.type == "commalist":
            value = value.split(",")
            values.ensure_value(dest, []).extend(value)
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)
        
    ATTRS=Option.ATTRS + ['section']
    TYPES=Option.TYPES + ('yesno','commalist')
    ACTIONS=Option.ACTIONS + ('sample_config','load_config',)
    TYPE_CHECKER=Option.TYPE_CHECKER
    TYPE_CHECKER['yesno'] = check_yesno
    #TYPE_CHECKER['commalist'] = check_commalist
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ('load_config',)

class AGXOptionParser(OptionParser):
    """Parser for ArchGenXML.

    Handles special data types (yesno, commalist) and generation of sample
    config file.
    """

    def __init__ (self,
                  usage=None,
                  option_list=None,
                  option_class=Option,
                  version=None,
                  conflict_handler="error",
                  description=None,
                  formatter=None,
                  add_help_option=1,
                  prog=None,
                  config_filename=None):
        return OptionParser.__init__(
                self,
                usage,
                option_list,
                AGXOption,
                version,
                conflict_handler,
                description,
                AGXHelpFormatter(),
                add_help_option,
                prog)
        self.config_filename=config_filename
    
    def get_all_options(self):
        """Return all options, recursing into groups."""

        options = [ o for o in self.option_list ]
        for group in self.option_groups:
            options.extend( [ o for o in group.option_list ] )
        return options


    def options_by_section(self):

        sections = {}
        for o in self.get_all_options():
            section = getattr(o, 'section', None)
            if section:
                sections.setdefault(section, [])
                sections[section].append(o)

        return sections

    def sample_config(self):
        """Sample config file"""

        for section, options in self.options_by_section().items():
            print "\n\n[%s]" % section
            for opt in options:
                if opt.help == SUPPRESS_HELP: continue
                for name in opt._long_opts:
                    if not name: continue
                    name = name[2:]  # get rid of --
                    help_lines = textwrap.wrap(opt.help, 70)
                    print
                    for line in help_lines:
                        print "#", line
                    if opt.action=="store_true" or opt.action=="store_false":
                        print name
                    elif opt.type=="yesno":
                        print "%s:yes|no" % name
                    else:
                        print "%s:%s" % ( name, opt.metavar or opt.dest.upper() )


    def read_project_configfile(self, filename, settings):
        """Read project config file into settings."""

        cp = ConfigParser()
        try:
            fname = open(filename,"r")
        except:
            self.print_version()
            print "\nERROR: Can't open project configuration file '%s'!" % filename
            sys.exit(2)

        cp.readfp(fname)
        fname.close()

        # Collect all options
        
        options = self.get_all_options()

        # Walk through options, checking in config file

        for option in options:
            section = getattr(option, 'section', None)
            if section:
                for name in option._long_opts:
                    if not name:
                        continue
                    name = name[2:]
                    if cp.has_option(section, name):
                        option.process(option, cp.get(section, name), settings, parser)


#============================================================================
# ArchGenXML Parsing


usage = "usage: %prog [ options ] <xmi-source-file>"
description = "A program for generating Archetypes from XMI files."

parser = AGXOptionParser(usage=usage, description=description, version="%prog 1.0")



parser.add_option("-o", 
        "--outfile",
        dest="outfilename", 
        metavar="PATH", 
        help="Package directory to create",
        section="GENERAL",
        )

group = OptionGroup(parser, "Configuration File Options")

group.add_option("-c", 
        "--cfg", 
        dest="config_file",
        help="Use configuration file",
        action="load_config",
        type="string",
        )

group.add_option( "--sample-config", 
        help="View sample configuration file.",
        action="sample_config",
        )

parser.add_option_group(group)

parser.add_option("-P", 
        "--parse-packages",
        type="commalist",
        action="append", 
        metavar="PACKAGE", 
        help="Name of packages to parse in source file (can specify several times)",
        section="GENERAL",
        )

parser.add_option("--method-preservation", 
        help="Methods in the target source will be preserved (default)", 
        default=1,
        dest="method_preservation",
        action="store_true",
        section="CLASSES",
        )

parser.add_option("--no-method-preservation", 
        help="Methods in the target source will not be preserved", 
        dest="method_preservation",
        action="store_false",
        section="CLASSES",
        )

parser.add_option("-t",
        "--unknown-types-as-string", 
        dest="unknownTypesAsString",
        help="Unknown attribute types will be treated as strings", 
        action="store_true",
        section="CLASSES",
        )

#----------------------------------------------------------------------------
# Generation Options

group = OptionGroup(parser, "Generation Options")

group.add_option("--widget-enhancement", 
        dest="widget_enhancement", 
        action="store_true", 
        default=True, 
        help="Do not create widgets with default label, label_msgid, description,"
             " description_msgid, and i18ndomain",
        section="CLASSES",
        )

group.add_option("--no-widget-enhancement", 
        dest="widget_enhancement", 
        action="store_false", 
        help="Do not create widgets with default label, label_msgid, description,"
             " description_msgid, and i18ndomain",
        )


group.add_option("-a", 
        "--actions", 
        dest="generateActions",
        default=True,
        help="Generate actions (default)",
        )

group.add_option("--no-actions", 
        help="Do not generate actions",
        dest="generateActions",
        )

group.add_option("--generate-actions", 
        type='yesno',
        dest="generateActions",
        help="",
        section="CLASSES",
        )

group.add_option("--default-actions",
        help="Generate default actions explicitly for each class",
        dest="generateDefaultActions",
        action="store_true",
        section="CLASSES",
        ),

group.add_option("--customization-policy",
        dest="customization_policy",
        action="store_true",
        help="FIXME",
        section="GENERAL",
        )

group.add_option("--strip-html", 
        action="store_true", 
        help="Strip HTML tags from documentation strings"
             " (for UML editors, such as Poseidon, which store HTML inside docs.)",
        section="DOCUMENTATION",
        )


parser.add_option_group(group)


#----------------------------------------------------------------------------
# i18n Options

group = OptionGroup(parser, "Internationalization Options")

group.add_option("--message-catalog",
        dest="build_msgcatalog",
        help="Automatically build msgid catalogs",
        type="yesno",
        default=1,
        section="I18N",
        )

group.add_option("--no-message-catalog", 
        dest="build_msgcatalog", 
        help="Do not automatically create msgid catalogs",
        )

group.add_option("--i18n-support", 
        help="Support for i18NArchetypes. Attributes with a stereotype of 'i18n'"
             " or taggedValue of 'i18n'=1 will be multilingual.",
        )

group.add_option("--i18n-content-support",
        dest="i18n_content_support",
        help="FIXME",
        section="I18N",
        )

parser.add_option_group(group)


#----------------------------------------------------------------------------
# Module information options

group = OptionGroup(parser, "Customization Options", 
        "These options set the defaults for the module information headers."
        " They can be overriden by taggedValues."
        )

group.add_option("--module-info-header",
        dest="module_info_header",
        action="store",
        default=1,
        type="yesno",
        help="Generate module information header",
        section="DOCUMENTATION",
        )

group.add_option("--no-module-info-header", 
        dest="module_info_header", 
        help="Do not generate module information header",
        action="store_false",
        )

group.add_option("--author", 
        help="Set default author value",
        section="DOCUMENTATION",
        )

# Added US spelling of email as alternate

group.add_option("--e-mail", 
        "--email", 
        dest="email",
        help="Set default email",
        section="DOCUMENTATION",
        )

group.add_option("--copyright", 
        help="Set default copyright",
        section="DOCUMENATION",
        )

# Added US spelling of license as alternate

group.add_option("--license", 
        "--licence", 
        help="Set default licence.",
        section="DOCUMENTATION",
        )

parser.add_option_group(group)



#----------------------------------------------------------------------------
# Permission options

group = OptionGroup(parser, "Permissions")

group.add_option("--creation-permission", 
        dest="creation_permission", 
        help='Specifies permission to create content'
             ' (defaults to "Add [project] content.")',
        section="CLASSES",
        )

group.add_option("--detailed-created-permissions", 
        action="store_true", 
        help="Separate creation permissions per class (defaults to no)",
        section="CLASSES",
        )

# This was a typo, and should be deprecated.

group.add_option("--detailled-creation-permissions", 
        action="store", 
        type="yesno",
        help=SUPPRESS_HELP,
        section="CLASSES",
        )

parser.add_option_group(group)

#----------------------------------------------------------------------------
# FIXME: Storage Options

group = OptionGroup(parser, "Storage Options")

group.add_option("--storage",
        dest="storage",
        help="FIXME",
        section="GENERAL",
        )


group.add_option("--ape", 
        dest="ape_support", 
        action="store_true", 
        help="Generate configuration and generators for APE",
        )

group.add_option("--ape-support", 
        dest="ape_support", 
        action="store", 
        type="yesno",
        help="Generate configuration and generators for APE",
        section="STORAGE",
        metavar="yes|no"
        )
group.add_option("--sql-storage-support",
        dest="sql_storage_support",
        help="FIXME",
        action="store_true",
        section="CLASSES",
        )

parser.add_option_group(group)

#----------------------------------------------------------------------------
# FIXME: Broken/undocumented options

group = OptionGroup(parser, "Broken/Undocumented Options")

# FIXME: This feature doesn't seem working currently in ArchGenXML--the
# class def gets the prefix, but nothing else does.

group.add_option("--prefix",
        help="Adds PREFIX before each class name",
        section="GENERAL",
        )

group.add_option("--generate-packages",
        help="FIXME",
        section="GENERAL",
        type="commalist",
        )

group.add_option("-f", 
        "--force",
        help="FIXME",
        section="GENERAL",
        )

group.add_option("-n",
        "--noclass",
        action="store_true",
        help="FIXME",
        section="CLASSES",
        )
group.add_option("--project-configuration",
        help="FIXME",
        )

group.add_option("--default-field-generation",
        dest="default_field_generation",
        help="FIXME",
        action="store_true",
        section="CLASSES",
        )

group.add_option("--backreferences-support",
        dest="backreferences_support",
        action="store_true",
        help="FIXME",
        section="CLASSES",
        )


parser.add_option_group(group)

(settings, args) = parser.parse_args()
#parser.read_project_configfile("/tmp/config", settings)
print settings
