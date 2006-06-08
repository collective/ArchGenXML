#<dtml-var "klass.getName()">

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.Field import ObjectField,encode,decode
from Products.Archetypes.Registry import registerField
from Products.Archetypes.utils import DisplayList
from Products.Archetypes import config as atconfig
from Products.Archetypes.Widget import *
from Products.Archetypes.Field  import *
from Products.Archetypes.Schema import Schema
try:
    from Products.generator import i18n
except ImportError:
    from Products.Archetypes.generator import i18n
<dtml-if "klass.hasAttributeWithTaggedValue('vocabulary:type','ATVocabularyManager')">
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
</dtml-if>

from Products.<dtml-var "klass.getPackage().getProduct().getCleanName()"> import config

<dtml-var "generator.getProtectedSection(parsed_class,'module-header')">
<dtml-var "generator.generateDependentImports(klass)">
<dtml-var "generator.getImportsByTaggedValues(klass) or ''">
<dtml-if "klass.getTaggedValue('validation_expression')">
from Products.validation.validators import ExpressionValidator
</dtml-if>
<dtml-if "parentname=='CompoundField'">
from Products.CompoundField.CompoundField import CompoundField
######<dtml-var parentname>
<dtml-var "generator.generateArcheSchema(klass, generator.getLocalFieldSpecs(klass))" >
</dtml-if>


class <dtml-var "klass.getCleanName()">(<dtml-if "klass.getGenParents()"><dtml-var "', '.join([p.getCleanName() for p in klass.getGenParents()])"><dtml-else><dtml-var parentname></dtml-if>):
    """<dtml-var "utils.indent(klass.getDocumentation(), 1, skipFirstRow=True, stripBlank=True)">
    """
<dtml-var "generator.getProtectedSection(parsed_class,'class-header',1)">
<dtml-var "generator.generateImplements(klass,[parentname]+[p.getCleanName() for p in klass.getGenParents()])" >

    _properties = <dtml-var parentname>._properties.copy()
    _properties.update({
        'type': '<dtml-var "klass.getCleanName().lower()">',
<dtml-if widgetname>
        'widget':<dtml-var widgetname>,
</dtml-if>
<dtml-let value_classes="klass.getClientDependencyClasses(dependencyStereotypes=['value_class'])">
<dtml-if value_classes>
        'value_class':<dtml-var "value_classes[0].getCleanName()">,
</dtml-if>
</dtml-let>
<dtml-if "klass.getTaggedValue('validation_expression')">
        'validators':(ExpressionValidator('''python:<dtml-var "klass.getTaggedValue('validation_expression')">'''),),
</dtml-if>
<dtml-var "generator.getProtectedSection(parsed_class,'field-properties',2)">
        })

    security  = ClassSecurityInfo()

<dtml-if "parentname=='CompoundField'">
    schema=schema
</dtml-if>

    security.declarePrivate('set')
    security.declarePrivate('get')


<dtml-if "not parsed_class">
    def get(self, instance, **kwargs):
        return <dtml-var parentname>.get(self, instance, **kwargs)

    def getRaw(self, instance, **kwargs):
        return <dtml-var parentname>.getRaw(self, instance, **kwargs)

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        return <dtml-var parentname>.set(self, instance, value, **kwargs)

</dtml-if>
<dtml-in "generator.getMethodsToGenerate(klass)[0]">
<dtml-let m="_['sequence-item']">
<dtml-if "m.getParent().__class__.__name__=='XMIInterface'">
    #from Interface <dtml-var "m.getParent().getName()">:
</dtml-if>
<dtml-if "parsed_class and m.getCleanName() in parsed_class.methods.keys()">
<dtml-var "parsed_class.methods[m.getCleanName()].getSrc()">
<dtml-else>

    def <dtml-var "m.getName()">(self,<dtml-var "', '.join(m.getParamNames())">):
        pass
</dtml-if>
</dtml-let>
</dtml-in>
<dtml-in "generator.getMethodsToGenerate(klass)[1]">
<dtml-var "_['sequence-item'].getSrc()">
</dtml-in>

registerField(<dtml-var "klass.getCleanName()">,
              title='<dtml-var "klass.getTaggedValue('label',klass.getCleanName())">',
              description='<dtml-var "klass.getTaggedValue('description','')">')

<dtml-var "generator.getProtectedSection(parsed_class,'module-footer')">
