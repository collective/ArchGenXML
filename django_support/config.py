#VERY INCOMPLETE AND MOSTLY UNTESTED YET
##########################################

from web_connect import *


#you can adapt this to your personal cfg-template
#%s will be raplces with the type of the list/dict
cfg_url='http://www.jaak.de/andi/tools/wiki/djangen-cfg-%s'

#Here we use a simple Typelist, for getting the UML Types transformed to Django-DB-Calls
models_typelist = get_dict_from_url(cfg_url % 'types', {
   'string': {'func':'models.CharField','required':['maxlength']},
   'boolean': {'func':'models.BooleanField'},
   'primary_key': {'func':'models.AutoField', 'required':['primary_key.primary_key'], 'done':True},
   'date': {'func':'models.DateField', 'optional':['auto_now']},
   'datetime': {'func':'models.DateTimeField', 'optional': ['auto_now']},
   'email':{'func':'models.EmailField'},
   'funds':{'func':'models.FloatField','required':['funds.max_digits', 'funds.decimal_places']},
   'file': {'func':'models.FileField', 'required':['upload_to']},
   'float': {'func':'models.FloatField', 'required':['max_digits', 'decimal_places']},
   'image': {'func':'models.ImageField', 'required':['upload_to'], 'optional': ['height_field', 'width_field']},
   'int': {'func':'models.IntegerField'},
   'integer': {'func':'models.IntegerField'},
   'percent': {'func':'models.IntegerField'},
   'text': {'func':'models.TextField'},
   'time': {'func': 'models.TimeField', 'optional':['auto_now']},
   'url': {'func':'models.URLField', 'optional':['verify_exists']},
   'xml': {'func':'models.XMLField', 'required':['schema_path']},

})

#Argmuments for the Django Fields, tgv stands for "tagged value" (where the placeholder is readen from)
models_typelist_args = get_dict_from_url(cfg_url % 'arglist' , {
    'maxlength': {'default':128, 'tgv':'maxlength', 'desc':'Sets the max Count of Chars in a CharField'},
    'auto_now': {'default':'False', 'tgv':'auto_now'},
    'upload_to': {'default':'%Y/%m/%d', 'tgv':'upload_to'},
    'max_digits': {'default':10, 'tgv':'max_digits'},
    'decimal_places': {'default':2, 'tgv':'decimal_places'},
    'height_field': {'default':None, 'tgv':'height_field'},
    'width_field': {'default':None, 'tgv':'width_field'},
    'schema_path': {'default':'', 'tgv':'schema_path'},
    'null': {'default':False, 'tgv': 'may_be_null'},
    'blank': {'default':False, 'tgv':'may_be_blank'},
    'choices': {'default':'', 'tgv':'choices'},
    'verify_exists': {'default':True,'tgv':'url_must_exist'},
    'help_text': {'default':'', 'tgv':'documentation', 'translate':'lazy'},
    'verbose_name': {'default':'', 'tgv':'verbose_name', 'translate':'lazy'},
    'unique': {'default':False, 'tgv':'unique'},
    'edit_inline': {'default':False,'tgv':'edit_inline', 'desc':"""Sets if the Object can be edited from the
    related objects page (as edit_inline does in Django)"""},
    'core': {'default':False,'tgv':'core', 'desc':'For objects that are edited inline to a related object.'
        'In the Django admin, if all "core" fields in an inline-edited object are cleared, the object will be deleted.'
        'It is an error to have an inline-editable relation without at least one core=True field.'
        'Please note that each field marked "core" is treated as a required field by the Django admin site.'
        'Essentially, this means you should put core=True on all required fields in your related object that is being edited inline.'
        },

    #Used by Special types, other Settings than Standard.
    #to use also the same param names, we override the param name with 'name'
    'funds.max_digits': {'default':12, 'name':'max_digits'},
    'funds.decimal_places': {'default':2, 'name':'decimal_places'},
    'primary_key.primary_key':{'default':True,'name':'primary_key'},

})
#optional for every Field
models_typelist_optionals = get_list_from_url(cfg_url % 'optional', [
 'null',
 'blank',
 'choices',
 'help_text',
 'verbose_name',
 'core',
 'unique',
 ])

tagged_values = get_dict_from_url(cfg_url % 'tgvs', {
 #Here we list all Tagged Values so the Engine finds them
 #tgvs listed as part of self.models_typelist_args are registeres automatically
 #cats arent pats but categories :)

 'admin': {'cats':['class'], 'desc':"""Sets Content of the admin subclass, for activating a Model in the Class
set it to 'pass'"""},
 'meta': {'cats':['class'], 'desc':"""Sets Content of the meta subclass, for activating a Model in the Class
set it to 'pass'"""},
 'force-code': {'cats':['method'], 'desc':"""Forces that the Code from the Diagramm will be used to override
eventual existing Source-Code in the (allready previously) generated source-files"""},
 'no_inherit': {'cats':['attribute','association'], 'desc':"""A Value of true (default: is false) sets that
the Member will not be inherited by child subclasses."""},
 'import_direct': {'cats':['class'], 'desc':"""A Value of true declares that the Class will be imported via
 import ... , and not from ... import ..."""},
 'import_as': {'cats':['class','package'], 'desc':"""As what will the Module be importet (only for import ... as ...)"""},
 'default': {'cats':['attribute'], 'desc':"""Set the defauls value of an attribute of an <<Module>>"""},
 'code': {'cats':['method'], 'desc':"""If there is no Code in or no existing function, tgc code will make you able to maintain simple code fragments direct in uml"""},
 'documentation': {'cats':['method','class','attribute','association'], 'desc':"""The Doc String"""},
})

#please do not put 'null'  here
#this will be done in self.convertAssocToDjango
models_assoc_optionals_o = get_list_from_url(cfg_url % 'opts_a_o', [
    'blank',
    'edit_inline',
 ])
models_assoc_optionals_m = get_list_from_url(cfg_url % 'opts_a_m', [
    'blank',
#    'edit_inline',
 ])

models_assoc_optionals_from = get_list_from_url(cfg_url % 'opts_a_from', [
     'edit_inine',
])

