#!/usr/bin/python

# Requires Python 2.3

# Created by: ????????
# Updated and integrated with agx by Reinout van Rees, Zest software.

from ConfigParser import SafeConfigParser as ConfigParser

from optparse import Option
from optparse import OptionGroup
from optparse import OptionParser
from optparse import OptionValueError
from optparse import SUPPRESS_HELP
from optparse import TitledHelpFormatter

import sys
import textwrap
import logging
import codesnippets
log = logging.getLogger("options")

#============================================================================
# Custom Parsers

class AGXHelpFormatter(TitledHelpFormatter):
    """Help formatter for ArchGenXML parser.
    """

    # subclassed to handle YES|NO values

    def format_option_strings (self, option):
        """Return a comma-separated list of option strings & metavariables.
        """

        # Overwritten to provide formatting for yesno fields.

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


    def check_commalist(option, opt, value):
        log.debug("Checking commalist value '%s' for option '%s'.",
                  value, opt)
        try:
            value = value.split(",")
            log.debug("We've splitted the value, it is now '%s'.",
                      value)
            return value
        except:
            raise OptionValueError

    def take_action(self, action, dest, opt, value, values, parser):
        """Perform action.
        """

        # Overridden to provide sample_config option and to handle
        # commalist as a list.
        log.debug("Running an action '%s' for option '%s', value '%s'.",
                  action, opt, value)
        if action == "sample_config":
            log.debug("We'll print the sample config and exit.")
            print parser.sample_config()
            sys.exit(0)
        elif action == "load_config":
            log.debug("We'll read in the project's config file '%s'.",
                      value)
            parser.read_project_configfile(value, values)
        elif action == "append" and self.type == "commalist":
            log.debug("We're a commalist and we have to append value '%s'.",
                      value)
            log.debug("Ensuring that option '%s' exists.",
                      dest)
            values.ensure_value(dest, [])
            original_value = getattr(values, dest)
            log.debug("Before adding, the option's value was '%s'.",
                      original_value)
            if original_value == '':
                # Bloody hack, but can't figure out what's wrong.
                log.debug("Don't know why, but our list is an empty string. "
                          "Resetting it to an empty list. (HACK).")
                setattr(values, dest, [])
            values.ensure_value(dest, []).extend(value)
            log.debug("After adding, the option's value is '%s'.",
                      getattr(values, dest))
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)

    # Yes, this needs to be placed right at the end of the class.
    ATTRS = Option.ATTRS + ['section']
    TYPES = Option.TYPES + ('yesno', 'commalist')
    ACTIONS = Option.ACTIONS + ('sample_config', 'load_config',)
    TYPE_CHECKER = Option.TYPE_CHECKER
    TYPE_CHECKER['yesno'] = check_yesno
    TYPE_CHECKER['commalist'] = check_commalist
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
        # XXX: below line doesn't get called because of above return...
        self.config_filename = config_filename

    def get_all_options(self):
        """Return all options, recursing into groups.
        """

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
        """Print sample config file.
        """

        for section, options in self.options_by_section().items():
            print "[%s]" % section
            for opt in options:
                if opt.help == SUPPRESS_HELP:
                    continue
                for name in opt._long_opts:
                    if not name:
                        continue
                    name = name[2:]  # get rid of --
                    help_lines = textwrap.wrap(opt.help, 70)

                    for line in help_lines:
                        print "## %s" % line
                    if opt.action == "store_true":
                        if opt.default == 1:
                            print '%s' % name
                        else:
                            print '#%s' % name
                    elif opt.action == "store_false":
                        if opt.default == 0:
                            print '%s' % name
                        else:
                            print '#%s' % name
                    elif opt.type=="yesno":
                        # Restrict this to the default value
                        print "#%s: yes" % name
                        print "#%s: no" % name
                    else:
                        if opt.default != 'NODEFAULT':
                            print "%s: %s" % (name, opt.default)
                        else:
                            print "#%s: " % name
                    # Blank line
                    print
            # Blank line
            print

    def read_project_configfile(self, filename, settings):
        """Read project config file into settings.
        """

        log.debug("Trying to read the config file '%s'",
                  filename)
        config_parser = ConfigParser()
        try:
            fname = open(filename, 'r')
        except:
            self.print_version()
            log.error("Can't open project configuration file '%s'.",
                      filename)
            sys.exit(2)

        config_parser.readfp(fname)
        fname.close()

        # Collect all options

        options = self.get_all_options()
        log.debug("Options we read from the config file: %r.",
                  options)

        # Walk through options, checking in config file

        for option in options:
            section = getattr(option, 'section', None)
            if section:
                for name in option._long_opts:
                    if not name:
                        continue
                    name = name[2:]
                    if config_parser.has_option(section, name):
                        option.process(option, config_parser.get(section, name), settings, parser)


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

group.add_option("--widget-enhancement",
                 dest="widget_enhancement",
                 type="yesno",
                 default=1,
                 help="Create widgets with default label, label_msgid, description,"
                 " description_msgid, and i18ndomain (default is 1).",
                 section="CLASSES",
                 )

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

group.add_option("--rcs_id",
                 dest="rcs_id",
                 type="yesno",
                 help="Add RCS $Id$ tags to the generated file (default is 0).",
                 default=0,
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
                 "referred-to class. Requires ATBackRef product to work. "
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

group.add_option("--no-classes",
                 dest="noclass",
                 help="Don't generate classes, so create an empty "
                 "project with skin dir and so (default is 0).",
                 type="yesno",
                 default=0,
                 section="CLASSES",
                 )

parser.add_option_group(group)

#----------------------------------------------------------------------------
# i18n Options

group = OptionGroup(parser, "Internationalization Options")

group.add_option("--message-catalog",
                 dest="build_msgcatalog",
                 help="Automatically build msgid catalogs (default is 1).",
                 type="yesno",
                 default=1,
                 section="I18N",
                 )

group.add_option("--i18n-content-support",
                 help="Support for i18NArchetypes. Attributes with a stereotype of 'i18n'"
                 " or taggedValue of i18n=1 will be multilingual (default is 0).",
                 type="yesno",
                 dest="i18n_content_support",
                 default=0,
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
                 default='',
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
                 default='',
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
                 help="Set default licence (default is the GPL).",
                 default=codesnippets.GPLTEXT,
                 section="DOCUMENTATION",
                 type="string", #xxx stringlist? 
                 )

parser.add_option_group(group)



#----------------------------------------------------------------------------
# Permission options

group = OptionGroup(parser, "Permissions")

group.add_option("--default-creation-permission",
                 dest="default_creation_permission",
                 help="Specifies default permission to create content"
                 " (defaults to 'Add portal content.'). "
                 "Warning: it used to be 'Add [CREATION_PERMISSION] content', "
                 "so with the 'Add' and 'content' automatically added.",
                 default="Add portal content",
                 type="string",
                 section="CLASSES",
                 )
#XXX handle creation_permission the right way.

group.add_option("--detailed-created-permissions",
                 type="yesno",
                 help="Separate creation permissions per class (defaults to no)",
                 default=0,
                 section="CLASSES",
                 dest="detailed_creation_permissions",
                 )



parser.add_option_group(group)

#----------------------------------------------------------------------------
# Storage Options

group = OptionGroup(parser, "Storage Options")

group.add_option("--ape-support",
                 dest="ape_support",
                 type="yesno",
                 help="Generate configuration and generators for APE (default is 0).",
                 section="STORAGE",
                 default=0,
                 )

group.add_option("--sql-storage-support",
                 dest="sql_storage_support",
                 type="yesno",
                 help="FIXME: not sure it this is used. (default is 0)",
                 section="CLASSES",
                 default=0,
                 )

parser.add_option_group(group)

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
# FIXME: Broken/undocumented options

group = OptionGroup(parser, "Possibly broken options")

# FIXME: This feature doesn't seem working currently in ArchGenXML--the
# class def gets the prefix, but nothing else does.

group.add_option("--prefix",
                 help="Adds PREFIX before each class name (default is '').",
                 default='',
                 type="string",
                 dest="prefix",
                 section="GENERAL",
                 )

parser.add_option_group(group)

if __name__ == '__main__':
    (settings, args) = parser.parse_args()
    print settings
