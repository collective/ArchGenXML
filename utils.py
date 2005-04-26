import sys, os.path, time
import getopt
from types import StringTypes

NameTable = {
    'class': 'klass',
    'import': 'emport'
    }

def makeFile(outFileName,force=1):
    outFile = None
    if (not force) and os.path.exists(outFileName):
        return None
    elif (force=='ask') and os.path.exists(outFileName):
        reply = raw_input('File %s exists.  Overwrite? (y/n): ' % outFileName)
        if reply == 'y':
            outFile = open(outFileName, 'w')
        else:
            return None
    else:
        outFile = open(outFileName, 'w')
    return outFile

def readFile(fn):
    try:
        file = open(fn, 'r')
        res=file.read()
        file.close()
        return res
    except IOError:
        return None

def makeDir(outFileName,force=1):
    outFile = None
    if (not force) and os.path.exists(outFileName):
        reply = raw_input('File %s exists.  Overwrite? (y/n): ' % outFileName)
        if reply == 'y':
            os.mkdir(outFileName)
    else:
        if not os.path.exists(outFileName):
            os.mkdir(outFileName)



def mapName(oldName):
    #global NameTable
    newName = oldName

    if NameTable:
        if oldName in NameTable.keys():
            newName = NameTable[oldName]
    return newName.replace('-','_')

def readTemplate(fn):
    templdir=os.path.join(sys.path[0],'templates')
    templ=open(os.path.join(templdir,fn)).read()

    return templ


def indent(s,indent,prepend='',skipFirstRow=0):
    rows=s.split('\n')
    if skipFirstRow:
        lines=[rows[0]]+['    '*indent + prepend + l for l in rows[1:]]
    else:
        try:
            lines=['    '*indent + prepend + l for l in rows]
        except:
            import pdb;pdb.set_trace()

    return '\n'.join(lines)

def getExpression(s):
    '''
    interprets an expression (for permission settings and other taggedValues)
    if an exp is a string it will be kept, if not it will be enclosed by quotes
    if an exp starts with python: it will be not quoted
    '''

    if s is None:
        s=''

    s=s.strip()

    if s and (s[0]=='"' and s[-1]=='"' or s[0]=="'" and s[-1]=="'"):
        return s
    else:
        if s.startswith('python:'):
            return s[7:]
        else:
            # Quote in """ if the string contains " or a newline, else use "
            if '"' in s or '\n' in s:
                return '"""%s"""' % s
            else:
                return '"%s"' % s

def isTGVTrue(tgv):
    return toBoolean(tgv) 

def isTGVFalse(tgv):
    return not toBoolean(tgv) 

def toBoolean(v):
    if type(v) in (StringTypes):
        v=v.lower().strip()
    if v in (0,'0','false',False):
        return False
    if v in (1,'1','true',True):
        return True
    if v:
        return True
    return False

def cleanName(name):
    return name.replace(' ','_').replace('.','_').replace('/','_')

# begin code copy
# copied from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061 :
def wrap(text, width):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line[line.rfind('\n')+1:])
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )

# end code copy

try:
    from ConfigParser import SafeConfigParser as ConfigParser
except:
    from ConfigParser import ConfigParser


# key: (cmdlinekey?, shortcutkey?, cfg-file-key? -> 0 or section-name, internal settings-key, type)

## FIXME: ALL THIS OPTIONS NEED A MAJOR CLEANUP!

ALLOWED_OPTIONS_MAP = {
    'outfile':                          (0, 'o', 'GENERAL',       'outfilename', 'string'),
    'prefix':                           (0, 'p', 'GENERAL',       'prefix', 'string'),
    'generate-packages=':               (1,  0, 'GENERAL',        'generate_packages', 'commalist'),
    'parse-packages=':                  (1,  0, 'GENERAL',        'parse_packages', 'commalist'),
    'force':                            (0, 'f', 'GENERAL',       'force', 'switchon'),
    'ape':                              (1, 0,   None,            'ape_support', 'switchon'),
    'ape-support':                      (1, 0,   'STORAGE',       'ape_support', 'yesno'), # used in conf-files, no switch here!
    'actions':                          (1, 'a', None     ,       'generateActions', 'switchon'),
    'no-actions':                       (1, 0,   None,            'generateActions', 'switchoff'),
    'generate-actions':                 (0, 0,   'CLASSES',       'generateActions', 'yesno'),
    'default-actions':                  (1, 0,   'CLASSES',       'generateDefaultActions', 'switchon'),
    'creation-permission=':             (1, 0,   'CLASSES',       'creation_permission', 'string'),
    'detailled-creation-permissions=':  (1, 0,   'CLASSES',       'detailled_creation_permissions', 'yesno'),
    'widget-enhancement':               (0, 0,   'CLASSES',       'widget_enhancement', 'switchon'),
    'no-widget-enhancement':            (1, 0,   None,            'widget_enhancement', 'switchoff'),
    'method-preservation':              (1, 0,   'CLASSES',       'method_preservation', 'switchon'),
    'no-method-preservation':           (1, 0,   None,            'method_preservation', 'switchoff'),
    'noclass':                          (1, 'n', 'CLASSES',       'noclass', 'switchon,'),
    'unknown-types-as-string':          (1, 't', 'CLASSES',       'unknownTypesAsString','switchon'),
    'i18n-content-support=':            (1, 0,   'I18N',          'i18n_content_support','string'),
    'i18n':                             (1, 0,   None,            'i18n_support','switchon'),
    'message-catalog':                  (0, 0,   'I18N',          'build_msgcatalog','yesno'),
    'no-message-catalog':               (1, 0,   None,            'build_msgcatalog','switchoff'),
    'module-info-header':               (0, 0,   'DOCUMENTATION', 'module_info_header','yesno'),
    'no-module-info-header':            (1, 0,   None,            'module_info_header','switchoff'),
    'author=':                          (1, 0,   'DOCUMENTATION', 'author', 'string'),
    'e-mail=':                          (1, 0,   'DOCUMENTATION', 'email', 'string'),
    'copyright=':                       (1, 0,   'DOCUMENTATION', 'copyright', 'string'),
    'license=':                         (1, 0,   'DOCUMENTATION', 'license', 'string'),
    'strip-html':                       (1, 0,   'DOCUMENTATION', 'striphtml', 'switchon'),
    'rcs-id':                           (1, 0,   'DOCUMENTATION', 'rcs_id','switchon'),
    'no-rcs-id':                        (1, 0,   'DOCUMENTATION', 'rcs_id','switchoff'),
    'generated-date':                   (1, 0,   'DOCUMENTATION', 'generated_date','switchon'),
    'no-generated-date':                (1, 0,   'DOCUMENTATION', 'generated_date','switchoff'),
    'cfg=':                             (1, 'c', None,            None,'string'),
    'project-configuration=':           (1, 0,   None,            None,'string'),
    'storage=':                         (1, 0,   'GENERAL',       'storage', 'string'),
    'sql-storage-support':              (1, 0,   'CLASSES',       'sql_storage_support', 'switchon'),
    'default-field-generation':         (1, 0,   'CLASSES',       'default_field_generation', 'switchon'),
    'backreferences-support':           (1, 0,   'CLASSES',       'backreferences_support', 'switchon'),
    'relation-implementation=':         (1, 0,   'CLASSES',       'relation_implementation', 'string'),
    'customization-policy':             (1, 0,   'GENERAL',       'customization_policy','switchon'),
    'noclass':                          (1, 0,   'GENERAL',       'noclass','switchon'),
}

def set_setting(okey, value, settings):
    """ set one option """
    yesno={'yes':1, 'y':1, 1:1, '1':1, 'no':None, 'n':None, 0:None, '0':None}
    if ALLOWED_OPTIONS_MAP[okey][3]:
        if ALLOWED_OPTIONS_MAP[okey][4] == 'switchon':
            settings[ALLOWED_OPTIONS_MAP[okey][3]]= 1
        elif ALLOWED_OPTIONS_MAP[okey][4] == 'switchoff':
            settings[ALLOWED_OPTIONS_MAP[okey][3]]= None
        elif ALLOWED_OPTIONS_MAP[okey][4] == 'yesno' and yesno.has_key(value):
            settings[ALLOWED_OPTIONS_MAP[okey][3]]= yesno[value]
        elif ALLOWED_OPTIONS_MAP[okey][4] == 'string':
            settings[ALLOWED_OPTIONS_MAP[okey][3]]= value
        elif ALLOWED_OPTIONS_MAP[okey][4] == 'commalist':
            settings[ALLOWED_OPTIONS_MAP[okey][3]]= value.split(',')
        print "set %s [%s] to %s" % (ALLOWED_OPTIONS_MAP[okey][3],ALLOWED_OPTIONS_MAP[okey][4], value)


def modify_settings(key, value, settings, shortkey=0):
    """ option is an 2-tuple, settings a dict """
    okey= len(key)>2 and key[:2]=='--' and key[2:]
    if okey:
        if not ALLOWED_OPTIONS_MAP.has_key(okey) and ALLOWED_OPTIONS_MAP.has_key(okey+'='):
            okey+='='
        if ALLOWED_OPTIONS_MAP.has_key(okey) and (ALLOWED_OPTIONS_MAP[okey][0] or shortkey):
            settings=set_setting(okey,value,settings)


def read_project_configfile(filename,settings):
    cp = ConfigParser()
    try:
        fname = open(filename,"r")
    except:
        print ARCHGENXML_VERSION_LINE
        print "\nERROR: Can't open project configuration file '%s'!", filename
        sys.exit(2)

    cp.readfp(fname)
    fname.close()

    for key in ALLOWED_OPTIONS_MAP.keys():
        fkey = key[len(key)-1] == '=' and key[:len(key)-1] or key
        if cp.has_option(ALLOWED_OPTIONS_MAP[key][2], fkey):
            set_setting(key, cp.get(ALLOWED_OPTIONS_MAP[key][2], fkey), settings)

##    # print a ugly sample cfg
##    y=['['+ALLOWED_OPTIONS_MAP[key][2]+']\n'+(key[len(key)-1] == '=' and key[:len(key)-1] or key) for key in ALLOWED_OPTIONS_MAP.keys() if ALLOWED_OPTIONS_MAP[key][2]]
##    y.sort()
##    for x in y print x

def read_project_settings(args):
    """ reads options from args and return options array"""
    # this should use sometimes the new advenced python2.3 parser

    # set defaults
    settings={}
    settings['version']=version()
    settings['author'] = None
    settings['email'] = None
    settings['copyright'] = None
    settings['licence'] = None
    settings['module_info_header'] = 1
    settings['creation_permission'] = None
    settings['detailled_creation_permissions'] = None
    settings['widget_enhancement'] = None
    settings['outfilename'] = None
    settings['rcs_id'] = 0
    settings['generated_date'] = 0

    shortoptions = ':'.join([ ALLOWED_OPTIONS_MAP[optkey][1] \
        for optkey in ALLOWED_OPTIONS_MAP.keys() \
        if ALLOWED_OPTIONS_MAP[optkey][1]]
    )
    longoptions = [optkey for optkey in ALLOWED_OPTIONS_MAP.keys() \
        if ALLOWED_OPTIONS_MAP[optkey][0]]

    opts, args = getopt.getopt(args, shortoptions,longoptions)

    prefix = ''

    # first run to get configfile
    for option in opts:
        if option[0] in ['--project-configuration','--cfg','-c'] and option[1]:
            print "Use configfile", option[1]
            read_project_configfile(option[1],settings)

    # second run to overide with commandline parameters
    for option in opts:
        modify_settings(option[0], option[1], settings)
        shortdict = { }
        x=[shortdict.update({ALLOWED_OPTIONS_MAP[key][1]:key}) \
            for key in ALLOWED_OPTIONS_MAP.keys() \
            if ALLOWED_OPTIONS_MAP[key][1]]

        if len(option[0])>1 and option[0][0]=='-' and shortdict.has_key(option[0][1:]):
            modify_settings('--'+shortdict[option[0][1:]], option[1], settings, shortkey=1)
    return settings, args

ARCHGENXML_VERSION_LINE = """\
ArchGenXML %(version)s
(c) 2003 BlueDynamics GmbH, under GNU General Public License 2.0 or later
"""

def version():
    ver=open(os.path.join(sys.path[0],'version.txt')).read().strip()
    print ARCHGENXML_VERSION_LINE % {'version': ver}
    return ver

USAGE_TEXT = """\
Usage: ArchGenXML.py -o <target>|-c <configfile> [ options ] <xmi-source-file>

OPTIONS:
    -o <target>
        Output file directory path for data  representation classes. Last part
        is used for internal directory namings.

    -P <name1>,<name2>...
        names of packages to parse in source file

    -a --actions
        generates actions (default)

    --no-actions
        do not generates actions

    --method-preservation
        methods in the target sources will be preserved (default)

    --no-method-preservation
        methods in the target sources will be preserved

    -t --unknown-types-as-string
        unknown attribute types will be treated as text

    --ape-support
        generate apeconf.xml and generators for ape (needs Archetypes 1.1+)

    --i18n-support
        support for i18NArchetypes. Attributes with a stereotype 'i18n' or a
        taggedValue 'i18n' set to '1' are multilingual.

    --no-widget-enhancements
        do not create widgets with default label, label_msgid, description,
        description_msgid and i18ndomain.

    --no-message-catalog
        do not automagically create msgid catalogs

    --creation-permission=<perm>
        specifies which permission to create content default:Add [project]
        content

    --detailled-creation-permissions=<boolean>
        seperate creation permissions per class, defaults to 'no'

    --no-module-info-header
        do not generate module info header

    --author=<string>
        set default author string for module info headers, taggedValue will
        override this

    --e-mail=<string>
        set default e-mail adress string for module info headers, taggedValue
        will override this

    --copyright=<string>
        set default copyright string for module info headers, taggedValue will
        override this

    --licence=<string>
        set default licence string for module info-headers, taggedValue will
        override this

    --strip-html
        strips HTML tags from the document strings (e.g. for Poseidon which
        uses HTML inside the entity documentation )

    --no-rcs-id
        skips the addition of an version control ID tag

    --generated-date
        adds the date the file is generated to the file's header

"""

def usage(returncode=-1):
    print USAGE_TEXT
    sys.exit(returncode)

def getFileHeaderInfo(element, generator):
    """ returns and dictionary with all info for the file-header """

    #deal with multiline docstring
    purposeline=('\n').join( \
        (element.getDocumentation(striphtml=self.striphtml,wrap=79) or 'unknown').split('\n') )

    author= self.getOption('author', element, self.author) or 'unknown'

    copyright = COPYRIGHT % \
        (str(time.localtime()[0]),
         self.getOption('copyright', element, self.copyright) or author)

    licence = ('\n# ').join( \
        wrap(self.getOption('license', element, GPLTEXT),77).split('\n') )

    email=self.getOption('email', element, self.email) or 'unknown'
    email=email.split(',')
    email = [i.strip() for i in email]
    email ="<"+">, <".join([i.strip() for i in email])+">"

    fileheaderinfo = {'filename': modulename+'.py',
                      'purpose':  purposeline,
                      'author':   author,
                      'email':    email,
                      'version':  self.version,
                      'date':     time.ctime(),
                      'copyright':'\n# '.join(wrap(copyright,77).split('\n')),
                      'licence':  licence,
    }
