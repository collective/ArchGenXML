#----------------------------------------------------------------------------
# Name:        ArchetypesGenerator.py
# Purpose:     main class generating archetypes code out of an UML-model
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# Copyright:   (c) 2003-2005 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys
import time
import os.path
import logging
from types import StringTypes
from re import match, sub, compile, MULTILINE, DOTALL

import utils
import copy
from odict import odict
from codesnippets import *

from xml.dom import minidom
from zipfile import ZipFile
from StringIO import StringIO

# AGX-specific imports
import PyParser
import XMIParser
from UMLProfile import UMLProfile
from TaggedValueSupport import tgvRegistry

from BaseGenerator import BaseGenerator
from WorkflowGenerator import WorkflowGenerator
from OptionParser import OptionGroup, parser

from documenttemplate.documenttemplate import HTML

from pkg_resources import resource_filename


import config

_marker = []
log = logging.getLogger('generator')

try:
    from i18ndude import catalog as msgcatalog
except ImportError:
    has_i18ndude = False
else:
    has_i18ndude = True

try:
    'abca'.strip('a')
except:
    has_enhanced_strip_support = False
else:
    has_enhanced_strip_support = True

#
# Global variables etc.
#

Elements = []
AlreadyGenerated = []
Force = 0


class DummyModel:

    def __init__(self, name=''):
        self.name = name

    def getName(self):
        return self.name

    getCleanName = getName
    getFilePath = getName
    getModuleFilePath = getName
    getProductModuleName = getName
    getProductName = getName

    def hasStereoType(self, s, umlprofile=None):
        return True

    def getClasses(self, *a, **kw):
        return []

    getInterfaces = getClasses
    getPackages = getClasses
    getStateMachines = getClasses
    getAssociations = getClasses

    def isRoot(self):
        return 1

    def getAnnotation(self, *a, **kw):
        return None

    def getDocumentation(self, **kw):
        return None

    def hasTaggedValue(self, *a, **kw):
        return None

    def getParent(self, *a, **kw):
        return None


class DjangoGenerator(BaseGenerator):

    generator_generator = 'django'
    default_class_type = 'python_class'
    default_interface_type = 'z3'

    uml_profile = UMLProfile()

    uml_profile.addStereoType(
        'Model', ['XMIClass'],
        dispatching=1,
        template='model.py',
        generator='generateDjangoModel',
        description='A django DB Model will create a models.py')

    uml_profile.addStereoType(
        'Module', ['XMIClass'],
        dispatching=1,
        template='module.py',
        generator='generateDjangoAdditional',
        description='Doesn\'t generate a Class but a module with the Classes Members as Vars/Functions')

    uml_profile.addStereoType(
        'Choice', ['XMIClass'],
        dispatching=1,
        generator='generateDjangoAdditional',
        template='choice.py',
        description='Generates a touple that can be used as arg for the choise'
        'parameter... use attributes name as id and value tgv as title. I THINK THIS DOESN\'T WORK YET')

    uml_profile.addStereoType('python_class', ['XMIClass'],
        dispatching=1,
        generator='generatePythonClass',
        template='../../templates/python_class.py',
        description='Generate this class as a plain python class (with some additional stuff in it)')

    uml_profile.addStereoType(
        'Test', ['XMIClass'],
        description='This will generate an Unit Test, no great implementation yet.  I THINK THIS DOESN\'T WORK YET',
        generator='generateDjangoAdditional',
        template='test.py')

    uml_profile.addStereoType(
        'stub', ['XMIClass', 'XMIModel', 'XMIPackage'],
        description='Prevents a class/package/model from being generated'+\
        'Can be used in combination with "import_from" and a Dependency'\
        'to import external Libarys')

    uml_profile.addStereoType(
        'meta', ['XMIAttribute'],
        description='Attribute will be added to the mate class... NOT SUPPORTED YET')
    uml_profile.addStereoType(
        'Represenation', ['XMIAttribute'],
        description='Generates a self.__str__() (if not allready exist) that returns the attributes Value')


    # The defaults here are already handled by OptionParser
    # (And we want only a single authorative source of information :-)

    # force = 1
    # unknownTypesAsString = 0
    # generateActions = 1
    # generateDefaultActions = 0
    # prefix = ''
    # parse_packages = [] # Packages to scan for classes
    # generate_packages = [] # Packages to be generated
    # noclass = 0 # If set no module is reverse engineered,
    #             # just an empty project + skin is created
    # ape_support = 0 # Generate APE config and serializers/gateways?
    # method_preservation = 1 # Should the method bodies be preserved?
    # i18n_content_support = 0

    build_msgcatalog = 1
    striphtml = 0

    reservedAtts = ['id']
    portal_tools = () #preserved for the BaseGenerator (I call that "Backward Compatibility" :)
    variable_schema = 'variable_schema'

    #Types that are Stored in the models.py
    model_stereotypes=['Model']
    choice_stereotypes=['Choice']

    #stored in views.py (just the methods)
    modules_stereotypes=['Module']

    #unit test:
    test_stereotypes=['Test']

    ownfile_types=('model','test','choice')

    implements={}
    file_opened={}
    models_first=None
    models_path=''
    model_meta=['meta']

    model_method_names=[]

    model_representation_st='Representation'
    model_representation=None





    stub_stereotypes = ['odStub','stub','typedef']
    python_stereotype = ['python', 'python_class']
    folder_stereotype = ['folder', 'ordered', 'large', 'btree']
    import_stereotypes=['import']

    i18n_at = ['i18n', 'i18n-at']
    generate_datatypes = []

    hide_classes = ()



    left_slots = []
    right_slots = []

    # Should be 'Products.' be prepended to all absolute paths?
    force_plugin_root = 1

    customization_policy = 0
    backreferences_support = 0

    # Contains the parsed sources by class names (for preserving method codes) and func names
    parsed_class_sources = {}
    parsed_func_sources = {}

    # Contains the parsed sources (for preserving method codes)
    parsed_sources = []

    # TaggedValues that are not strings, e.g. widget or vocabulary
    nonstring_tgvs = ['widget', 'vocabulary', 'required', 'precision',
                      'storage', 'enforceVocabulary', 'multiValued',
                      'visible', 'validators', 'validation_expression',
                      'sizes', 'original_size', 'max_size', 'searchable',
                      'show_hm', 'move:pos', 'move:top', 'move:bottom']

    msgcatstack = []

    # ATVM: collects all used vocabularies in the format:
    # { productsname: (name, meta_type) }
    # If metatype is None, it defaults to SimpleVocabulary.
    vocabularymap = {}

    # If a reference has the same name as another _and_
    # its source object is the same, we want only one ReferenceWidget
    # _unless_ we have a tagged value 'single' on the reference
    reference_groups = []

    # for each class an own permission can be defined, how should be able to add
    # it. It default to "Add Portal Content" and
    creation_permissions = []

    # the stack is needed to remind permissions while a subproduct is generated
    creation_permission_stack = []



    def __init__(self, xschemaFileName, **kwargs):

        self.templateDir = resource_filename(__name__, "templates")

        log.debug("Initializing DjangoGenerator. "
                  "We're being passed a file '%s' and keyword "
                  "arguments %r.", xschemaFileName, kwargs)
        self.xschemaFileName = xschemaFileName
        self.__dict__.update(kwargs)
        log.debug("After copying over the keyword arguments (read: "
                  "OptionParser's options), outfilename is '%s'.",
                  self.outfilename)
        if self.outfilename:
            # Remove trailing delimiters on purpose
            if self.outfilename[-1] in ('/','\\'):
                self.outfilename = self.outfilename[:-1]
            log.debug("Stripped off the eventual trailing slashes: '%s'.",
                      self.outfilename)

            # Split off the parent directory part so that
            # we can call ArchgenXML.py -o /tmp/prod prod.xmi
            path = os.path.split(self.outfilename)
            self.targetRoot = path[0]
            log.debug("Targetroot is set to everything except the last "
                      "directory in the outfilename: %s.", self.targetRoot)
        else:
            log.debug("Outfilename hasn't been set. Setting "
                      "targetroot to the current directory.")
            self.targetRoot = '.'
        log.debug("Initialization finished.")

        self.__dict__.update(config.__dict__)

        self.initI18n()

        self.initTaggedValues()

        #do not parse - do doc
        if self.autodoc:
            self.parseAndGenerate=self.autoDoc


    def __setattr__(self, name, value):
        if name=='default_class_type':
            log.warning('default_class_type set to: %s', value)
            raise typeError
        else:
            self.__dict__[name]=value

    def autoDoc(self):
        """Here Djangen Document itself...
        Straigt to the output
        """

        print """Welcome to the DjangenXML
Here is some simple Information...

DjangenXML will generate Django/Python Code from your UML-Diagramms.


You have to use stereotypes and
tagged values in your diagramm to say Djangen what to do.

e.g. to create the models
class Blog(models.Model):
    title=models.CharField(max_length=128)

    class Admin:
        pass

class Entry(models.Model):
    title=models.CharField(max_length=128)
    content=models.CharField(max_length=1024)

    blog=models.ForeignKey('Blog',null=True,blank=True,
    related_name=entries)

    Admin: pass

you have to create a Diagramm:
+----------------+              +-----------------+
| <<Model>>      |              | <<Model>>       |
| Blog           | 1       1..* | Entry           |
+----------------+--------------+-----------------+
|title=string    | blog  entries| title=string    |
|                |              | content=string  |
+----------------+              +-----------------+
|tgv:admin='pass'|              | tgv:admin='pass'|
+----------------+              +-----------------+

There are much more things you can add... but please see the
detailed Doc...

Djangen will automatically create your Project if
Django is installed. But YOU have to install the apps
at this time. packages will create a folder which can be used
as app add models inside this package will be stored in a models.py
in this folder.

I allready tested it on an bigger Diagramm... but
of course there will be many bugs... please report them to
andikoerner@gmx.de

DjangenXML is licenced under GPL and will soon become part of
the ArchGenXML Project where it is developed from.

The aim of DjangenXML is to provide you a Develop support Utility not
just for Code generation, but for the complete Project maitenance.
Design you Project and the Documetation, even the Django-Admin-Strings
in UML, write the few line of code.
Refactor in UML, change Doc, regenerate, your Code will stay (until you
rename its Method or class... to avoid this rename it first
in the source... sorry)
So, you can evolve your Project step by Step in UML, and also avoid
much (de)bugging.
It's wonderfull to concentrate on the things that make us happy...

Testet with ArgoUML Diagramm...
for more Info, Djangen is at this time a fork of ArchGenXML
sp look at it's docs for more Info...

List of available Stereotypes:
----------------------------------
        """
        print self.uml_profile.documentation()

        print """List of available Types of Members
----------------------------------
       """
        for key in self.models_typelist:
            print "%s -- %s" % (key,self.models_typelist[key].get('desc',
                                      'Represents '+self.models_typelist[key].get('func','Unknown')))
            print ""

        print """List of available Tagged Values:
----------------------------------
        """
        print tgvRegistry.documentation()

    def initI18n(self):
        #The Table for i18n
        self.i18ntable={
           #'de':{'':''}
        }

    def initTaggedValues(self):
        """This Function takes the Configurable List of
        tagged Values an registers them. So that the tgvregistry doesn't argue"""

        for key in self.tagged_values.keys():
            tgv=self.tagged_values[key]
            for category in tgv['cats']:
                tgvRegistry.addTaggedValue(category=category, tagname=key, explanation=tgv['desc'])

        for item in self.models_typelist_args.keys():
            if self.models_typelist_args.get(item,{}).get('tgv'):
                tgvRegistry.addTaggedValue(category='association',
                                           tagname=self.models_typelist_args.get(item,{}).get('tgv',''),
                                           explanation=self.models_typelist_args.get(item,{}).get('desc',
                                                  'Argument %s' % item))
                tgvRegistry.addTaggedValue(category='attribute',
                                           tagname=self.models_typelist_args.get(item,{}).get('tgv',''),
                                           explanation=self.models_typelist_args.get(item,{}).get('desc',
                                                  'Represents Argument "%s"' % item))

    def makeFile(self, fn, force=1, binary=0):
        log.debug("Calling makeFile to create '%s'.", fn)
        ffn = os.path.join(self.targetRoot, fn)
        log.debug("Together with the targetroot that means '%s'.", ffn)
        return utils.makeFile(ffn, force=force, binary=binary)

    def readFile(self,fn):
        ffn = os.path.join(self.targetRoot, fn)
        return utils.readFile(ffn)

    def makeDir(self, fn, force=1):
        log.debug("Calling makeDir to create '%s'.", fn)
        ffn = os.path.join(self.targetRoot, fn)
        log.debug("Together with the targetroot that means '%s'.", ffn)
        return utils.makeDir(ffn, force=force)

    def AddImplement(self, module, implement, type='model', import_as=None):
        """Adds an entry to the implementation list.

        Checks if same module or if the Entry allready exists in the list"""
        if module==self.models_path:
            return ''
        if not module:
        	return ''


        if not type in self.ownfile_types:
            #print instead of adding
            return self.printImplement(module, [(implement, import_as)])
        else:
            if not self.implements.setdefault(type,{}).setdefault(module,[]).count((implement,import_as)):
               self.implements[type][module].append((implement,import_as))
               return ''

    def getElementType(self,element):
        s=None
        if element.hasStereoType(self.model_stereotypes, umlprofile=self.uml_profile): s= 'model'
        if element.hasStereoType(self.choice_stereotypes, umlprofile=self.uml_profile): s= 'choice'
        if element.hasStereoType(self.stub_stereotypes, umlprofile=self.uml_profile): s= 'stub'
        if element.hasStereoType(self.test_stereotypes, umlprofile=self.uml_profile): s= 'test'
        if element.hasStereoType(self.modules_stereotypes, umlprofile=self.uml_profile): s= 'module'
        return s

    def printImplement(self, module, implements):
        s = ''
        direct=False
        i_list=[imp for imp,imp_as in implements]
        as_list=[imp_as for imp,imp_as in implements]


        if i_list.count(None):
            s += "import %s" % (module)



            if as_list[i_list.index(None)]:
                s+= ' as %s' % as_list[i_list.index(None)]

            while i_list.count(None):
                del as_list[i_list.index(None)]
                del i_list[i_list.index(None)]



        if len(i_list)>0:
            s += "from %s import %s" % (module, ', '.join(i_list))

        return s

    def initOptions(self):
        #there is no possibility to store the options here.
        #they must be stored in the Optionsparser.py
        #shit...
        #so we get Dependencys
        pass

    def FormatString(self, value):
        if hasattr(value,'find') and value.find(os.linesep)>-1:
            return '"""%s"""' % value
        else:
            return "'%s'" % value


    def translate(self, text, lazy=False, gettext=True):
        lang = self.getOption('i18n_language', self.current_package)

        if lang in self.i18ntable:
            if self.i18ntable[lang].get(text, False):
                return self.FormatString(self.i18ntable[lang][text])
            else:
                log.warn('I18N: String "%s" not in Dictionary of "%s"' % (text, lang))
                return text

        if self.i18n_language_file:
            pass

        if gettext:
            if lang=='gettext':

                if lazy:
                    return 'gettext_lazy(%s)' % self.FormatString(text)
                else:
                    return '_(%s)' % self.FormatString(text)
            else:
                log.warn('I18N: Language not found: "%s"' % lang)


        return text


    def getAtts(self,klass):
        """At this time django has no generalisation. so we include the parents manually"""

        list=[]

        for p in klass.getGenParents():
         	list += self.getAtts(p)

        for e in klass.getAttributeDefs():
        	for ee in list:
        		if ee.getCleanName() != e.getCleanName() and not e.getTaggedValue('no_inherit', False):
        			list.append(e)
        			break

        	if len(list)==0:
        		list.append(e)

        return list

    def getAssocs(self, klass):

        list=[]

        for p in klass.getGenParents():
         	list += self.getAssocs(p)


        assocs=[]
        for e in klass.getFromAssociations(aggtypes=['none','aggregation','composite']):
            for ee in list:
                if ee.toEnd.getName() != e.toEnd.getName() and not e.getTaggedValue('no_inherit',False):
                    e.inherited_from=klass
                    assocs.append(e)

                    break

            if len(list)==0:
                e.inherited_from=klass
            	assocs.append(e)


        as2=[]

        #walking and preparsing the assocs.
        #looking on inheritance
        for assoc in list:
            assoc=copy.copy(assoc)
            #if this assoc is inherited.
            #make it 'mine'
            if assoc.fromEnd.getTarget() == assoc.inherited_from:
                #we have to modify the assoc
                assoc.fromEnd=copy.copy(assoc.fromEnd)
                assoc.fromEnd.obj=klass
            #if the assoc is a relation with itself
            #or a parental relation with itself
            if assoc.toEnd.getTarget() == assoc.inherited_from:
                #we have to modify the assoc
                assoc.toEnd=copy.copy(assoc.toEnd)
                assoc.toEnd.obj=klass

            as2.append(assoc)



        return as2+assocs

    def getMethods(self,klass):
        list=[]

        for p in klass.getGenParents():
             list += self.getMethods(p)

        for e in self.getMethodsToGenerate(klass)[0]:
            for ee in list:
                if ee.getCleanName() != e.getCleanName():
                    e.inherited_from=klass
                    list.append(e)
                    self.model_method_names.append(e.getName())
                    break

            if len(list)==0:
                e.inherited_from=klass
                list.append(e)
                self.model_method_names.append(e.getName())

        return list

    def getMethodNames(self,klass):
		return self.model_method_names

    def getDocFor(self,m, indent=2):
        """Creates the Standart-Documentation of an XMIElement"""

        #Documentation (even Code) can be international...
        s = self.translate(m.getDocumentation(), gettext=False) ;

        #Remove UML Only Documetation
        r=compile('{uml.*?}',MULTILINE|DOTALL)
        source= sub(r,'', s)

        if m.__class__.__name__ == 'XMIMethod':
            args=['%s -- %s' % (p.getName(), p.getTaggedValue('documentation','No Doc available'))
                           for p in m.getParams()]
            if len(args):
                s+= 'Params:\n'+'\n'.join(args)

        s='"""%s\n"""' % s

        s=utils.indent(s, indent, skipFirstRow=True, stripBlank=True)

        return s

    def getMethodHeader(self, func):
        params=self.getParamList(func)

        if not func.getParent().type == 'module' :
            if params:
                return 'def %s(self, %s):' % (func.getName(), params)
            else:
                return 'def %s(self):' % (func.getName())
        else:
            return 'def %s(%s):' % (func.getName(), params)


        #    def <dtml-var "m.getName()">(self<dtml-if param>, <dtml-var param></dtml-if>):

    def getMethodSource(self, methods, func, indent=2, source=False):
        """Returns the Sourcecode for a Method

        Returns also Source of inherited Methods (in Django is at this time no inheritance)
        And replaces the in Code Documentation with the Documentation in the Diagramm

        """
        if not source:
            if func.getCleanName() in methods.keys():
                source=methods[func.getCleanName()].getSrc()
            else:
                source=m.inherited_from.parsed_class.methods[func.getCleanName()].getSrc()

        r=compile('def .*?:',MULTILINE|DOTALL)
        source= sub(r,self.getMethodHeader(func), source, count=1)

        r=compile('""".*?"""',MULTILINE|DOTALL)
        source= sub(r,self.getDocFor(func, indent), source, count=1)

        return source;

    def GetDjangoArgs(self, keylist, att, optional=False, argslist=None, element=None):
        """Parses the function for tgvs for optinal or required args for
        the functions code generation.
        """
        args=[]
        if argslist is None: argslist = self.models_typelist_args

        for item in keylist:
            if argslist.get(item,{}).get('tgv'):
                value = att.getTaggedValue(argslist.get(item,{}).get('tgv'),argslist.get(item,{}).get('default',''))
            else:
               value = argslist.get(item,{}).get('default','')
            if not optional or value != argslist.get(item,{}).get('default',''):
                log.debug('<%s> - <%s>', value, argslist.get(item,{}).get('default',''))
                #differ internal Names from Names in the resulting Source
                name = argslist.get(item,{}).get('name',item)
                if argslist.get(item,{}).get('translate',False):
                    value = self.translate(value, True, att)
                if argslist.get(item,{}).get('format',False):
                    value = argslist.get(item,{}).get('format',False) % value
                if argslist.get(item,{}).get('format_string',False):
                    value = self.FormatString(value)

                args.append('%s=%s' % (name,value))
        return args


    def convertAssocToDjango(self, assoc):
        """Converts an UML Assoc to an Django compatible Assoc"""
        def getEndName(assoc):
            if assoc.toEnd.getTarget().getPackage().getName() == \
            assoc.fromEnd.getTarget().getPackage().getName() and not \
            assoc.toEnd.getTarget().getTaggedValue('import_from', False):
                s = "'%s'"
            else:
                s ='%s'

            if assoc.toEnd.getTarget().getCleanName() == assoc.fromEnd.getTarget().getCleanName():
                return "'self'"
            else:
                return s % assoc.toEnd.getTarget().getCleanName()
        out=''
        args=[]
        if assoc.toEnd.getLowerBound()==0:
            args.append('null=True')
            if self.null_is_blank:
                args.append('blank=True')

        if assoc.fromEnd.isNavigable:
            args.append("related_name='" + assoc.fromEnd.getName() +"'")

        if assoc.toEnd.getUpperBound() == 1:
            #We have a OneTo... Relation
            args+=self.GetDjangoArgs(self.models_assoc_optionals_o, assoc, optional=True)
            args+=self.GetDjangoArgs(self.models_assoc_optionals_from, assoc.fromEnd, optional=True)

            if assoc.fromEnd.getUpperBound() == 1 and assoc.fromEnd.isNavigable:
                #We have a One to One Relation
                out = 'models.OneToOneField('
            else:
                out = 'models.ForeignKey('
        else:
            args+=self.GetDjangoArgs(self.models_assoc_optionals_m, assoc, optional=True)
            args+=self.GetDjangoArgs(self.models_assoc_optionals_from, assoc.fromEnd, optional=True)

            out = 'models.ManyToManyField('

        #complete the Function
        out += getEndName(assoc)
        if len(args):
            out += ', '
        out     += ', '.join(args) + \
            ')'

        #Django supports just one-to-many, not many-to-one Relation...
        #So the User should optimie his UML-Diagramm
        if assoc.fromEnd.getUpperBound() == 1 and assoc.toEnd.getUpperBound() > 1 and assoc.fromEnd.isNavigable:
            out += '#NOTE: This Association has the WRONG DIRECTION for being used optimal in Django, please do a "turn-arround"' \
                    "Relation: from %s, to %s in Assoc %s" % (assoc.fromEnd.getUpperBound(), assoc.toEnd.getUpperBound(), assoc.getName())
            log.warn("Assoc %s has the wrong direction(from %s, to %s) please change the direction of the Assoc" % (assoc.getName(), assoc.fromEnd.getUpperBound(), assoc.toEnd.getUpperBound()))
        return out
    def getParamList(self,m):
        params=[]
        for p in m.getParams():
            if p.hasDefault():
                params.append('%s=%s' %  (p.getName(), p.getDefault()))
            else:
                params.append(p.getName())

        return ', '.join(params)

    def convertAttToDjango(self, att, klass):
        """Converts an UML Attribute to an Django like one.

        Uses therefore the self.models_typelist from above.
        """
        notexist='None #NOTE: UNKNOWN DATATYPE: %s'
        out=''
        type=att.type.lower()
        if att.hasStereoType(self.model_meta, umlprofile=self.uml_profile):
            out=att.type
        else:
            args=self.GetDjangoArgs(self.models_typelist.get(type,{}).get('required',[]), att)
            args+=self.GetDjangoArgs(self.models_typelist.get(type,{}).get('optional',[])+self.models_typelist_optionals, att, optional=True)
            if self.models_typelist.has_key(type):
                if not self.models_typelist[type].get('done',False):
                    out=self.models_typelist[type]['func'] + '(' + ', '.join(args) + ')'
                else:
                    out=self.models_typelist[type]['func']
            else:
                out=notexist % att.type
                log.warn("the Datatype %s (of Attribute %s of Models %s) doesn't exist as Django Database Field. Will be declared as 'None'" \
                         % (att.type, att.getCleanName(), klass.getCleanName()))

        if att.hasStereoType(self.model_representation_st, umlprofile=self.uml_profile):
            self.model_representation=att

        return out

    def NormPackageName(self, p):
        path = [path_elem.getModuleName() for path_elem in p.getQualifiedModulePath(
                  None,
                  forcePluginRoot=self.force_plugin_root,
                  includeRoot=0,
                ) if path_elem][1:]  #get the Import path as list
        if p.type in self.ownfile_types:
            path[-1]=p.type+'s'
        return '.'.join(path)

    def generateDependentImports(self, element):
        outfile = StringIO()
        package = element.getPackage()

        #We split the imports if we have a model
        if element.type in self.ownfile_types:
            for iface in self.getAggregatedInterfaces(element):
                self.AddImplement(iface.getQualifiedModuleName(forcePluginRoot=True)[1:],iface.getCleanName(), outfile=outfile)

        # Imports for stub-association classes
        importLines = []

        #Parents and Realisation
        parents = element.getGenParents()
        parents += element.getRealizationParents()
        parents += element.getClientDependencyClasses(includeParents=True)
        #Relations
        parents += [e.toEnd.getTarget() for e in
                    self.getAssocs(element)
                    if e.toEnd.getTarget()]

        for p in parents:
            p.type = self.getElementType(p)
            if p.type=='stub':
                # Import a module that is not explained in Detail at the Diagram
                # or imported from an external lib
                if p.getTaggedValue('import_from',False):
                    if p.getTaggedValue('import_direct', False):
                        print >>outfile, self.AddImplement(p.getTaggedValue('import_from'), None, type=element.type, import_as=p.getTaggedValue('import_as', p.getCleanName()))
                    else:
                        print >>outfile, self.AddImplement(p.getTaggedValue('import_from'), p.getName(), type=element.type)
            else:
                if p.type=='module' or p.getTaggedValue('import_direct', False):
                    print >>outfile, self.AddImplement(
                       self.NormPackageName(p), None, type=element.type, import_as=p.getTaggedValue('import_as',p.getCleanName()))
                else:
                    print >>outfile, self.AddImplement(
                        self.NormPackageName(p), p.getName(), type=element.type)


        assocs = element.getFromAssociations()
        element.hasAssocClass = 0
        for p in assocs:
            if getattr(p,'isAssociationClass',0):
                # get import_from and add it to importLines
                module = p.getTaggedValue('import_from', None)
                if module:
                    importLine = (module, p.getName())
                    importLines.append(importLine)
                element.hasAssocClass = 1
                break

        if self.backreferences_support:
            bassocs = element.getToAssociations()
            for p in bassocs:
                if getattr(p, 'isAssociationClass', 0):
                    element.hasAssocClass = 1
                    break

        if element.hasAssocClass:
            for line in importLines:
                model, implement = line
                self.AddImplement(model, implement)

        return outfile.getvalue().strip()

    def generateAdditionalImports(self, element):
        outfile = StringIO()
        return outfile.getvalue()


    def getImportsByTaggedValues(self, element):
        # imports by tagged values
        additionalImports=self.getOption('imports', element, default=None,
                                         aggregate=True)
        return additionalImports

    def generateMethods(self, outfile, element, mode='class'):
        print >> outfile,'    # Methods'

        generatedMethods = []
        allmethnames = [m.getName() for m in element.getMethodDefs(recursive=1)]

        for m in element.getMethodDefs():
            self.generateMethod(outfile, m, element, mode=mode)
            allmethnames.append(m.getName())
            generatedMethods.append(m)

        for interface in element.getRealizationParents():
            meths = [m for m in interface.getMethodDefs(recursive=1)
                     if m.getName() not in allmethnames]
            # We don't want to extra generate methods
            # that are already defined in the class
            if meths:
                print >> outfile, '\n    # Methods from Interface %s' % \
                      interface.getName()
                for m in meths:
                    self.generateMethod(outfile, m, element, mode=mode)
                    allmethnames.append(m.getName())
                    generatedMethods.append(m)

        # Contains _all_ generated method names
        method_names = [m.getName() for m in generatedMethods]

        #if __init__ has to be generated for tools i want _not_ __init__ to be preserved
        #if it is added to method_names it wont be recognized as a manual method (hacky but works)
        if element.hasStereoType(self.portal_tools, umlprofile=self.uml_profile) and '__init__' not in method_names:
            method_names.append('__init__')

        #as __init__ above if at_post_edit_script has to be generated for tools
        #I want _not_ at_post_edit_script to be preserved (hacky but works)
        #if it is added to method_names it wont be recognized as a manual method
        if element.hasStereoType(self.portal_tools, umlprofile=self.uml_profile) \
           and 'at_post_edit_script' not in method_names:
            method_names.append('at_post_edit_script')

        if self.method_preservation:
            log.debug("We are to preserve methods, so we're looking for manual methods.")
            cl = self.parsed_class_sources.get(element.getPackage().getFilePath()+'/'+element.name, None)
            if cl:
                log.debug("The class has the following methods: %r.", cl.methods.keys())
                manual_methods = [mt for mt in cl.methods.values() if mt.name not in method_names]
                log.debug("Found the following manual methods: %r.", manual_methods)
                if manual_methods:
                    print >> outfile, '\n    # Manually created methods\n'

                for mt in manual_methods:
                    declaration = cl.getProtectionDeclaration(mt.getName())
                    if declaration:
                        print >> outfile, declaration
                    print >> outfile, mt.src
                print >> outfile


    def generateMethod(self, outfile, m, klass, mode='class'):
        #ignore actions and views here because they are generated separately
        if m.hasStereoType(['action', 'view', 'form', 'portlet_view',
                            'portlet'], umlprofile=self.uml_profile):
            return

        wrt = outfile.write
        paramstr = ''
        params = m.getParamExpressions()
        if params:
            paramstr = ',' + ','.join(params)

        print >> outfile

        if mode == 'class':
            declaration = self.generateMethodSecurityDeclaration(m)
            if declaration:
                print >> outfile, declaration

        cls = self.parsed_class_sources.get(klass.getPackage().getFilePath() +
                                            '/' + klass.getName(), None)
        if cls:
            method_code = cls.methods.get(m.getName())
        else:
            method_code = None

        if self.method_preservation and method_code:
            wrt(method_code.src)
            # Holly hack: methods ending with a 'pass' command doesn't have
            # an extra blank line after reparsing the code, so we add it
            if method_code.src.split('\n')[-1].strip() == 'pass':
                print >> outfile
        else:
            if mode=='class':
                print >> outfile, '    def %s(self%s):' % (m.getName(), paramstr)
            elif mode=='interface':
                print >> outfile, '    def %s(%s):' % (m.getName(), paramstr[1:])

            code = m.taggedValues.get('code', '')
            doc = m.getDocumentation(striphtml=self.strip_html)
            if doc is not None:
                print >> outfile, utils.indent('"""%s\n"""' % doc, 2,
                                               stripBlank=True)
            if code and mode == 'class':
                print >> outfile, utils.indent('\n'+code, 2)
            else:
                print >> outfile, utils.indent('pass', 2)

	if m.isStatic():
            print >> outfile, '    %s = staticmethod(%s)\n' % (m.getName(),m.getName())

    def generateBaseTestcaseClass(self,element,template):
        log.debug('write runalltests.py and framework.py')
        runalltests=self.readTemplate('tests/runalltests.py')
        framework=self.readTemplate('tests/framework.py')

        log.debug('generate base testcase class')
        of=self.makeFile(os.path.join(element.getPackage().getFilePath(),'runalltests.py'))
        of.write(runalltests)
        of.close()

        of=self.makeFile(os.path.join(element.getPackage().getFilePath(),'framework.py'))
        of.write(framework)
        of.close()

        return self.generateTestcaseClass(element,template)

    def generateDocTestcaseClass(self,element,template ):
        #write runalltests.py and framework.py
        testdoc_t=self.readTemplate('tests/testdoc.txt')
        testdoc=HTML(testdoc_t,{'klass':element })()


        testname=element.getTaggedValue('doctest_name') or element.getCleanName()
        self.makeDir(os.path.join(element.getPackage().getProduct().getFilePath(),'doc'))
        docfile=os.path.join(element.getPackage().getProduct().getFilePath(),'doc','%s.txt' % testname)
        if not self.readFile(docfile):
            of=self.makeFile(docfile)
            of.write(testdoc)
            of.close()

        init='#'
        of=self.makeFile(os.path.join(element.getPackage().getProduct().getFilePath(),'doc','__init__.py' ))

        of.write(init)
        of.close()


        return self.generateTestcaseClass(element,template,testname=testname)

    def generateTestcaseClass(self,element,template,**kw):
        log.info("%sGenerating testcase '%s'.",
                 '    '*self.infoind, element.getName())

        assert element.hasStereoType('plone_testcase', umlprofile=self.uml_profile) or element.getCleanName().startswith('test'), \
            "names of test classes _must_ start with 'test', but this class is named '%s'" % element.getCleanName()

        assert element.getPackage().getCleanName() == 'tests', \
            "testcase classes only make sense inside a package called 'tests' \
                 but this class is named '%s' and located in package '%s'" % (element.getCleanName(),element.getPackage().getCleanName())

        if element.getGenParents():
            parent = element.getGenParents()[0]
        else:
            parent = None

        return BaseGenerator.generatePythonClass(self, element, template, parent=parent, nolog=True, **kw)

    def getAggregatedInterfaces(self,element,includeBases=1):
        res = element.getAggregatedClasses(recursive=0,filter=['interface'])
        if includeBases:
            for b in element.getGenParents(recursive=1):
                res.extend(self.getAggregatedInterfaces(b,includeBases=0))

        return res

    def generateDjangoModel(self, element, template, nolog=False, **kw):
        self.model_representation=None

        if not nolog:
            log.info("%sGenerating Django Model '%s'.",
                     ' '*4*self.infoind,
                     element.getName())

        templ = self.readTemplate(template)
        d = {
            'klass': element,
            'generator': self,
            'parsed_class': element.parsed_class,
            'builtins': __builtins__,
            'utils': utils,
        }
        d.update(__builtins__)
        d.update(kw)
        res = HTML(templ, d)()
        return res

    def generateDjangoAdditional(self, element, template, nolog=False, **kw):
        if not nolog:
            log.info("%sGenerating Django Additional '%s'.",
                     ' '*4*self.infoind,
                     element.getName())

        templ = self.readTemplate(template)
        d = {
            'klass': element,
            'generator': self,
            'parsed_class': element.parsed_class,
            'parsed_funcs': element.parsed_funcs,
            'parsed_mod': element.parsed_mod,
            'builtins': __builtins__,
            'utils': utils,
        }

        #log.info(element.parsed_funcs)

        d.update(__builtins__)
        d.update(kw)
        res = HTML(templ, d)()
        return res

    def generateHeader(self, element):
        outfile=StringIO()

        s1 = TEMPLATE_HEADER

        outfile.write(s1)

        genparentsstereotype = element.getRealizationParents()
        hasz3parent = False
        for gpst in genparentsstereotype:
            if gpst.hasStereoType('z3'):
                hasz3parent = True
                break
        if hasz3parent or element.hasStereoType('z3'):
            outfile.write('import zope\n')

        return outfile.getvalue()

    def generateStdFilesForPackage(self, package):
        """Generate the standard files for a non-root package"""

        # Generate an __init__.py
        self.generatePackageInitPy(package)

    def updateVersionForProduct(self, package):
        """Increment the build number in verion.txt"""

        build=1
        versionbase='0.1'
        fp=os.path.join(package.getFilePath(),'version.txt')
        vertext=self.readFile(fp)
        if vertext:
            versionbase=vertext=vertext.strip()
            parsed=vertext.split(' ')
            if parsed.count('build'):
                ind=parsed.index('build')
                try:
                    build=int(parsed[ind+1]) + 1
                except:
                    build=1

                versionbase=' '.join(parsed[:ind])

        version='%s build %d\n' % (versionbase,build)
        of=self.makeFile(fp)
        print >>of,version,
        of.close()


    def generateConfigPy(self, package):
        """ generates: config.py """

        configpath=os.path.join(package.getFilePath(),'config.py')
        parsed_config=self.parsePythonModule(package.getFilePath(), 'config.py')
        creation_permission = self.getOption('creation_permission', package, None)

        if creation_permission:
            default_creation_permission = creation_permission
        else:
            default_creation_permission = self.default_creation_permission

        roles = []
        creation_roles = []
        for perm in self.creation_permissions:
            if not perm[1] in roles and perm[2] is not None:
                roles.append(perm[1])
                creation_roles.append( (perm[1], perm[2]) )

        # prepare (d)TML varibles
        d={'package'                    : package,
           'generator'                  : self,
           'builtins'                   : __builtins__,
           'utils'                      : utils,
           'default_creation_permission': default_creation_permission,
           'creation_permissions'       : self.creation_permissions,
           'creation_roles'             : creation_roles,
           'parsed_config'              : parsed_config,
        }
        d.update(__builtins__)

        templ=self.readTemplate('config.py')
        dtml=HTML(templ,d)
        res=dtml()

        of=self.makeFile(configpath)
        of.write(res)
        of.close()

        return

    def generateProductInitPy(self, package):
        """ Generate __init__.py at product root from the DTML template"""

        # prepare DTML varibles
        d={'generator'                     : self,
           'utils'                         : utils,
           'package'                       : package,
           'product_name'                  : package.getProductName (),
        }

        templ=self.readTemplate('__init_django__.py')
        dtml=HTML(templ,d)
        res=dtml()

        of=self.makeFile(os.path.join(package.getFilePath(),'__init__.py'))
        of.write(res)
        of.close()

        return

    def generatePackageInitPy(self, package):
        """ Generate __init__.py for packages from the DTML template"""

        # Get the names of packages and classes to import
        packageImports = [m.getModuleName () for m in package.getAnnotation('generatedPackages') or []]
        classImports   = [m.getModuleName () for m in package.generatedModules]

        # Get the preserved code sections
        parsed = self.parsePythonModule(package.getFilePath (), '__init__.py')
        headerCode = self.getProtectedSection(parsed, 'init-module-header')
        footerCode = self.getProtectedSection(parsed, 'init-module-footer')

        # Prepare DTML varibles
        d={'generator'                     : self,
           'package'                       : package,
           'utils'                         : utils,
           'package_imports'               : packageImports,
           'class_imports'                 : classImports,
           'protected_module_header'       : headerCode,
           'protected_module_footer'       : footerCode,
           }

        templ=self.readTemplate('__init_package_django__.py')
        dtml=HTML(templ,d)
        res=dtml()

        of=self.makeFile(os.path.join(package.getFilePath(),'__init__.py'))
        of.write(res)
        of.close()

        return


    def generateStdFilesForProduct(self, package):
        """Generate __init__.py,  various support files and and the skins
        directory. The result is a QuickInstaller installable product
        """

        target = package.getFilePath ()

        # remove trailing slash
        if target[-1] in ('/','\\'):
            target=target[:-1]

        templdir=os.path.join(sys.path[0],'templates')

        # Generate a refresh.txt for the product
        of=self.makeFile(os.path.join(package.getFilePath(),'refresh.txt'))
        of.close()

        # Increment version.txt build number
        self.updateVersionForProduct(package)

        # Generate product root __init__.py
        self.generateProductInitPy(package)



        # Generate config.py from template
        #We will use this later for the auto-configuration of the app
        #self.generateConfigPy(package)

    def generateStdFiles(self, package):
        if package.isRoot():
            self.generateStdFilesForProduct(package)
        else:
            self.generateStdFilesForPackage(package)

    def getGeneratedClasses(self,package):
        classes=package.getAnnotation('generatedClasses') or []
        for p in package.getPackages():
            if not p.isProduct():
                classes.extend(self.getGeneratedClasses(p))
        res=[]
        for c in classes:
            if c not in res:
                res.append(c)
        return res

    def generatePackage(self, package, recursive=1):
        log.debug("Generating package %s.",
                  package)
        if package.hasStereoType(self.stub_stereotypes, umlprofile=self.uml_profile):
            log.debug("It's a stub stereotyped package, skipping.")
            return
        package.generatedModules = []
        if package.getName().lower().startswith('java') or not package.getName():
            #to suppress these unneccesary implicit created java packages (ArgoUML and Poseidon)
            log.debug("Ignoring unneeded package '%s'.",
                      package.getName())
            return

        self.makeDir(package.getFilePath())
        self.implements={}
        self.implements.setdefault('models',{})
        self.implements.setdefault('choices',{})
        self.implements.setdefault('tests',{})
        self.file_opened={}
        self.current_package=package

        #we have a 'precompiler' here.
        #this checks if all associations are in the right
        #directions (Django supports just one Direction in ForeignKeys
        for element in package.getClasses()+package.getInterfaces():
            element.type = self.getElementType(element)

            if element.type=='model':
                assocs = element.getFromAssociations(aggtypes=['none','aggregation','composite'])
                for assoc in assocs:
                    if assoc.fromEnd.getUpperBound() == 1 and assoc.toEnd.getUpperBound() > 1 and assoc.fromEnd.isNavigable:
                        log.info('\t\t\tAssoc %s: wrong direction, fixed.' % assoc.getName())
                        assoc.toEnd.assocsFrom.append(copy.copy(assoc))
                        element.assocsTo.append(copy.copy(assoc))
                        del(assoc)

        for element in package.getClasses()+package.getInterfaces():

            #skip stub and internal classes
            if element.isInternal() or element.getName() in self.hide_classes \
               or element.getName().lower().startswith('java::'): # Enterprise Architect fix!
                log.debug("Ignoring unnecessary class '%s'.",
                          element.getName())
                continue
            if element.hasStereoType(self.stub_stereotypes, umlprofile=self.uml_profile):
                log.debug("Ignoring stub class '%s'.",
                          element.getName())
                continue

            #testin if have a Django-Model or something like this


            module=element.getModuleName()
            package.generatedModules.append(element)
            if element.type in self.ownfile_types:
                outfilepath=os.path.join(package.getFilePath(), element.type+'s.py')
            else:
                outfilepath=os.path.join(package.getFilePath(), module+'.py')

            mod=None
            if self.method_preservation:
                filename = os.path.join(self.targetRoot, outfilepath)
                log.debug("Filename (joined with targetroot) is "
                          "'%s'.", filename)
                try:
                    mod=PyParser.PyModule(filename)
                    log.debug("Existing sources found for element %s: %s.",
                              element.getName(), outfilepath)
                    for c in mod.classes.values():
                        self.parsed_class_sources[package.getFilePath()+'/'+c.name]=c
                    for f in mod.functions.values():
                        self.parsed_func_sources.setdefault(package.getFilePath()+'/'+element.getName(), {})[f.name]=f
                except IOError:
                    log.debug("No source found at %s.",
                              filename)
                    pass
                except:
                    log.critical("Error while reparsing file '%s'.",
                                 outfilepath)
                    raise

            try:
                outfile = StringIO()
                element.parsed_class = self.parsed_class_sources.get(element.getPackage().getFilePath()+'/'+element.name,None)
                element.parsed_funcs = self.parsed_func_sources.get(element.getPackage().getFilePath()+'/'+element.name,None)
                element.parsed_mod = mod
                if element.type in self.ownfile_types:
                    path = [pp.getModuleName() for pp in element.getQualifiedModulePath(
                              None,forcePluginRoot=self.force_plugin_root, includeRoot=0,
                              ) if pp][1:]  #get the Import path as list
                    path[-1]=element.type+'s'    #replace the class name with module name
                                                 #we must do this 'cause in AGX is 1 module per class
                    self.models_path='.'.join(path)

                    if not self.file_opened.get(element.type):
                        #we need to clean the Models File
                        if os.path.exists(outfilepath):
                            os.unlink(outfilepath)

                        self.file_opened.setdefault(element.type,True)

                else:
                    self.models_path = element.getQualifiedModuleName(
                            None,
                            forcePluginRoot=self.force_plugin_root,
                            includeRoot=0,
                        )[1:]



                if not element.isInterface():
                    print >>outfile, self.dispatchXMIClass(element)
                    generated_classes = package.getAnnotation('generatedClasses') or []
                    generated_classes.append(element)
                    package.annotate('generatedClasses', generated_classes)
                else:
                    print >>outfile, self.dispatchXMIInterface(element)
                    generated_interfaces = package.getAnnotation('generatedInterfaces') or []
                    generated_interfaces.append(element)
                    package.annotate('generatedInterfaces', generated_interfaces)



                buf=''
                for filetype in self.ownfile_types:
                    if element.type==filetype and self.file_opened.get(filetype) and os.path.exists(outfilepath):
                        #ArchGenXML isn't designet for more than one Models per File so we need to fix this
                        infile=open(outfilepath,'r')
                        buf = infile.read()


                buf += outfile.getvalue()

                log.debug("The outfile is ready to be written to disk now. "
                          "Loading it with the pyparser just to be sure we're "
                          "not writing broken files to disk.")
                try:
                    PyParser.PyModule(buf, mode='string')
                    log.debug("Nothing wrong with the outfile '%s'.",
                              outfilepath)
                except:
                    log.info(buf)
                    log.critical("There's something wrong with the python code we're about "
                                 "to write to disk. Perhaps a faulty tagged value or a "
                                 "genuine bug in parsing the previous version of the file. "
                                 "The filename is '%s'. For easy debugging, the file is "
                                 "printed above.",
                                 outfilepath)
                    raise
                classfile = self.makeFile(outfilepath)
                # TBD perhaps check if the file is parseable
                print >> classfile, buf
                classfile.close()
            except:
                #roll back the changes
                # and dont swallow the exception
                raise


        #we need to write the imports of the DjangoModels to the models File
        #for simplyness we rewrite it therefore

        for filetype in self.ownfile_types:
            if self.file_opened.get(filetype):
                buf=StringIO()
                print >> buf,self.generateModuleInfoHeader(package)
                if filetype=='model':
                    print >>buf, '\nfrom django.db import models'
                    print >>buf, 'from django.utils.translation import gettext_lazy'
                if filetype=='test':
                    print >>buf, 'import unittest'

                for module, implements in self.implements.get(filetype,{}).items():
                    print >>buf, self.printImplement(module, implements)

                outfilepath=os.path.join(package.getFilePath(), filetype+'s.py')
                infile=open(outfilepath,'r')

                print >> buf, infile.read()
                log.info(buf.getvalue()[2730:2750])
                classfile = self.makeFile(outfilepath)
                print >> classfile, buf.getvalue()
                classfile.close()

        #generate subpackages
        generatedPkg = package.getAnnotation('generatedPackages') or []
        for p in package.getPackages():
            if p.isProduct():
                self.infoind += 1
                self.generateProduct(p)
                self.infoind -= 1
            else:
                log.info("%sGenerating package '%s'.",
                         '    '*self.infoind,
                         p.getName())
                self.infoind += 1
                self.generatePackage(p,recursive=1)
                self.infoind -= 1
                generatedPkg.append(p)
                package.annotate('generatedPackages',generatedPkg)

        self.generateStdFiles(package)

    def generateRelation(self, doc, collection, relname, relid,
            sourcetype=None, targettype=None,
            sourceinterface=None,targetinterface=None,
            sourcecardinality=(None,None),
            targetcardinality=(None,None),
            assocclassname=None,
            inverse_relation_id=None,
            primary=0,
            ):

        ruleset=doc.createElement('Ruleset')
        ruleset.setAttribute('id',relname)
        ruleset.setAttribute('uid',relid)
        collection.appendChild(ruleset)

        #type and interface constraints
        if sourcetype or targettype:
            typeconst=doc.createElement('TypeConstraint')
            typeconst.setAttribute('id','type_constraint')
            ruleset.appendChild(typeconst)

        if sourceinterface or targetinterface:
            ifconst=doc.createElement('InterfaceConstraint')
            ifconst.setAttribute('id','interface_constraint')
            ruleset.appendChild(ifconst)


        if sourcetype:
            el=doc.createElement('allowedSourceType')
            typeconst.appendChild(el)
            el.appendChild(doc.createTextNode(sourcetype))
        if sourceinterface:
            el=doc.createElement('allowedSourceInterface')
            ifconst.appendChild(el)
            el.appendChild(doc.createTextNode(sourceinterface))

        if targettype:
            el=doc.createElement('allowedTargetType')
            typeconst.appendChild(el)
            el.appendChild(doc.createTextNode(targettype))
        if targetinterface:
            ifconst.setAttribute('id','interface_constraint')
            el=doc.createElement('allowedTargetInterface')
            ifconst.appendChild(el)
            el.appendChild(doc.createTextNode(targetinterface))


        #association constraint
        if assocclassname:
            contref = doc.createElement('ContentReference')
            ruleset.appendChild(contref)
            contref.setAttribute('id', 'content_reference')
            pt = doc.createElement('portalType')
            contref.appendChild(pt)
            pt.appendChild(doc.createTextNode(assocclassname))

            pt = doc.createElement('shareWithInverse')
            contref.appendChild(pt)
            pt.appendChild(doc.createTextNode('1'))

            el = doc.createElement('primary')
            el.appendChild(doc.createTextNode(str(primary)))
            contref.appendChild(el)

        #cardinality
        targetcardinality=list(targetcardinality)
        if targetcardinality[0] == -1:
            targetcardinality[0] = None
        if targetcardinality[1] == -1:
            targetcardinality[1] = None

        if targetcardinality != [None, None]:
            const = doc.createElement('CardinalityConstraint')
            ruleset.appendChild(const)
            const.setAttribute('id', 'cardinality')
            if targetcardinality[0]:
                el = doc.createElement('minTargetCardinality')
                const.appendChild(el)
                el.appendChild(doc.createTextNode(str(targetcardinality[0])))
            if targetcardinality[1]:
                el = doc.createElement('maxTargetCardinality')
                const.appendChild(el)
                el.appendChild(doc.createTextNode(str(targetcardinality[1])))

        #create the inverse relation
        if inverse_relation_id:
            const=doc.createElement('InverseImplicator')
            ruleset.appendChild(const)
            const.setAttribute('id','inverse_relation')
            el=doc.createElement('inverseRuleset')
            const.appendChild(el)
            el.setAttribute('uidref',inverse_relation_id)

        return ruleset

    def generateRelations(self, package):
        doc=minidom.Document()
        lib=doc.createElement('RelationsLibrary')
        doc.appendChild(lib)
        coll=doc.createElement('RulesetCollection')
        coll.setAttribute('id',package.getCleanName())
        lib.appendChild(coll)
        package.num_generated_relations=0
        assocs = package.getAssociations(recursive=1)
        processed = [] # xxx hack and workaround, not solution, avoids double
                       # generation of relations
        for assoc in assocs:
            if assoc in processed:
                continue
            processed.append(assoc)
            if self.getOption('relation_implementation',assoc,'basic') != 'relations':
                continue

            source=assoc.fromEnd.obj
            target=assoc.toEnd.obj

            targetcard=list(assoc.toEnd.mult)
            sourcecard=list(assoc.fromEnd.mult)
            sourcecard[0]=None #temporary pragmatic fix
            targetcard[0]=None #temporary pragmatic fix
            #print 'relation:',assoc.getName(),'target cardinality:',targetcard,'sourcecard:',sourcecard
            sourcetype=None
            targettype=None
            sourceinterface=None
            targetinterface=None

            if source.isInterface():
                sourceinterface=source.getCleanName()
            else:
                sourcetype=source.getCleanName()

            if target.isInterface():
                targetinterface=target.getCleanName()
            else:
                targettype=target.getCleanName()

            inverse_relation_name = assoc.getTaggedValue('inverse_relation_name', None)
            if not inverse_relation_name and assoc.fromEnd.isNavigable:
                if self.getOption('old_inverse_relation_name', assoc, None):
                    # BBB
                    inverse_relation_name = '%s_inverse' % assoc.getCleanName()
                else:
                    fromEndName = assoc.fromEnd.getName(ignore_cardinality=1)
                    toEndName = assoc.toEnd.getName(ignore_cardinality=1)
                    if fromEndName == toEndName:
                        inverse_relation_name =  '%s_inv' % assoc.getCleanName()
                    else:
                        inverse_relation_name =  '%s_%s' % (toEndName.lower(), fromEndName.lower())

            assocclassname=getattr(assoc,'isAssociationClass',0) and assoc.getCleanName() or assoc.getTaggedValue('association_class') or self.getOption('association_class',assoc,None)
            self.generateRelation(doc, coll,
                assoc.getCleanName(),
                assoc.getId(),
                sourcetype=sourcetype,
                targettype=targettype,
                sourceinterface=sourceinterface,
                targetinterface=targetinterface,
                sourcecardinality=sourcecard,
                targetcardinality=targetcard,

                assocclassname=assocclassname,
                inverse_relation_id=inverse_relation_name,
                primary=1
                )

            #create the counterrelation
            if inverse_relation_name:
                self.generateRelation(doc, coll,
                    inverse_relation_name,
                    inverse_relation_name,
                    sourcetype=targettype,
                    targettype=sourcetype,
                    sourceinterface=targetinterface,
                    targetinterface=sourceinterface,
                    sourcecardinality=targetcard,
                    targetcardinality=sourcecard,

                    assocclassname=assocclassname,
                    inverse_relation_id=assoc.getId()
                    )

            # ATVM integration - by jensens
            # very special case: create a vocabulary with the association name
            # this is needed for some use-cases, where a association class has
            # use an vocabulary with the name ofthe relation

            if utils.isTGVTrue(self.getOption('association_vocabulary', assoc, '0')):
                # remember this vocab-name and if set its portal_type
                currentproduct = package.getProductName()
                if not currentproduct in self.vocabularymap.keys():
                    self.vocabularymap[currentproduct] = {}
                type = self.getOption('association_vocabularytype', assoc, 'SimpleVocabulary')
                if not assoc.getCleanName() in self.vocabularymap[currentproduct].keys():
                    self.vocabularymap[currentproduct][assoc.getCleanName()] = (
                                                    type,
                                                    'SimpleVocabularyTerm'
                    )
                else:
                    print "warning: vocabulary with name %s defined more than once." % assoc.getCleanName()
                if inverse_relation_name and not inverse_relation_name in self.vocabularymap[currentproduct].keys():
                    self.vocabularymap[currentproduct][inverse_relation_name] = (
                                                    type,
                                                    'SimpleVocabularyTerm'
                    )

            #/ATVM

            package.num_generated_relations += 1

        if package.num_generated_relations:
            of=self.makeFile(os.path.join(package.getFilePath(),'relations.xml'))
            print >>of,doc.toprettyxml()
            of.close()

    def generateProduct(self, root):
        dirMode=0
        outfile=None

        if self.generate_packages and root.getCleanName() not in self.generate_packages:
            log.info("%sSkipping package '%s'.",
                     '    '*self.infoind,
                     root.getCleanName())
            return

        dirMode=1
        if root.hasStereoType(self.stub_stereotypes, umlprofile=self.uml_profile):
            log.debug("Skipping stub Product '%s'.",
                      root.getName())
            return

        log.info("Starting new Product: '%s'.",
                 root.getName())

        # increment indent of output
        self.infoind += 1

        #create the directories
        self.makeDir(root.getFilePath())

        #generate a Django Project if wanted (see Options)

        if self.startproject=='yes' or \
           self.startproject=='auto' and not os.path.exists(root.getCleanName()) :
            log.info("\tCreating Django Project")
            os.system('django-admin.py startproject %s' % root.getCleanName())
            self.startproject='yes';

        package = root
        self.generateRelations(root)
        self.generatePackage(root)

        #start Workflow creation
        #wfg = WorkflowGenerator(package, self)
        #wfg.generateWorkflows()

        # post-creation
        self.infoind -= 1


    def parseAndGenerate(self):

        # and now start off with the class files
        self.generatedModules=[]

        suff = os.path.splitext(self.xschemaFileName)[1].lower()
        log.info("Parsing...")
        if suff.lower() in ('.xmi','.xml'):
            log.debug("Opening xmi...")
            self.root = root= XMIParser.parse(self.xschemaFileName,
                                              packages=self.parse_packages,
                                              generator=self,
                                              generate_datatypes=self.generate_datatypes)
            log.debug("Created a root XMI parser.")
        elif suff.lower() in ('.zargo','.zuml','.zip'):
            log.debug("Opening %s ..." % suff.lower())
            zf=ZipFile(self.xschemaFileName)
            xmis=[n for n in zf.namelist() if os.path.splitext(n)[1].lower()in ['.xmi','.xml']]
            assert(len(xmis)==1)
            buf=zf.read(xmis[0])
            self.root=root=XMIParser.parse(xschema=buf,
                packages=self.parse_packages, generator=self,
                generate_datatypes=self.generate_datatypes)
        else:
            raise TypeError,'input file not of type .xmi, .xml, .zargo, .zuml'

        if self.outfilename:
            log.debug("We've got an self.outfilename: %s.",
                      self.outfilename)
            lastPart = os.path.split(self.outfilename)[1]
            log.debug("We've split off the last directory name: %s.",
                      lastPart)
            root.setName(lastPart)
            log.debug("Set the name of the root generator to that"
                      " directory name.")
        else:
            log.debug("No outfilename present, not changing the "
                      "name of the root generator.")
        log.info("Directory in which we're generating the files: '%s'.",
                 self.outfilename)

        log.info('Generating...')
        if self.method_preservation:
            log.debug('Method bodies will be preserved')
        else:
            log.debug('Method bodies will be overwritten')
        if not has_enhanced_strip_support:
            log.warn("Can't build i18n message catalog. Needs 'python 2.3' or later.")
        if not XMIParser.has_stripogram:
            log.warn("Can't strip html from doc-strings. Module 'stripogram' not found.")
        self.generateProduct(root)
