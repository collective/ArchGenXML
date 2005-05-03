#  ReferenceField compatible field for relations.
#
# XXX: Note that self.relationship doesn't make much sense for a
# "Relations field", because it takes away the flexibility to define
# Rulesets at runtime.  Let's consider ways of doing what we want to
# do without using a ReferenceField subclass.

from types import ListType, TupleType, StringTypes
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.Field import ObjectField,encode,decode
from Products.Archetypes.Registry import registerField
from Products.Archetypes.utils import DisplayList
from Products.Archetypes import config as atconfig
from Products.Archetypes.Widget import *


from Products.generator import i18n




<dtml-var "generator.getProtectedSection(parsed_class,'module-header')">

<dtml-var "generator.generateDependentImports(klass)">
class <dtml-var "klass.getCleanName()">(<dtml-if "klass.getGenParents()"><dtml-var "','.join([p.getCleanName() for p in klass.getGenParents()])"><dtml-else>ObjectField</dtml-if>):
    ''' <dtml-var "klass.getDocumentation()">'''

    _properties = <dtml-var parentname>._properties.copy()
    _properties.update({
        'type': '<dtml-var "klass.getCleanName().lower()">',
        'widget':<dtml-var widgetname>
        })

    security  = ClassSecurityInfo()

    security.declarePrivate('set')
    security.declarePrivate('get')
    
<dtml-if "not parsed_class">

    def get(self, instance, **kwargs):
        value = ObjectField.get(self, instance, **kwargs)
        return encode(value, instance, **kwargs)

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        kwargs['field'] = self
        # Remove acquisition wrappers
        value = decode(aq_base(value), instance, **kwargs)
        self.getStorage(instance).set(self.getName(), instance, value, **kwargs)
        
</dtml-if>    



    <dtml-in "generator.getMethodsToGenerate(klass)[0]">
    <dtml-let m="_['sequence-item']">
    <dtml-if "m.getParent().__class__.__name__=='XMIInterface'"> 
    
    #from Interface <dtml-var "m.getParent().getName()">:
    </dtml-if>
    <dtml-if "parsed_class and m.getCleanName() in parsed_class.methods.keys()">

<dtml-var "parsed_class.methods[m.getCleanName()].getSrc()">    
    <dtml-else>

    def <dtml-var "m.getName()">(self,<dtml-var "','.join(m.getParamNames())">):
        pass
    </dtml-if>
    </dtml-let>
    </dtml-in>

    <dtml-in "generator.getMethodsToGenerate(klass)[1]">

<dtml-var "_['sequence-item'].getSrc()">            
    </dtml-in>

        
    

registerField(<dtml-var "klass.getCleanName()">,
              title='<dtml-var "klass.getTaggedValue('label',klass.getCleanName())">',
              description='<dtml-var "klass.getTaggedValue('decription','')">')
