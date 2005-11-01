from zope.interface import Interface, Attribute

<dtml-in "classes">
<dtml-let klass="_['sequence-item']">
<dtml-let parents="[p for p in klass.getGenParents() if p.getCleanName() not in ['object', 'dict', 'list']]">
class I<dtml-var "klass.getCleanName()">(<dtml-if "parents"><dtml-var "','.join(['I'+p.getCleanName() for p in parents])"><dtml-else>Interface</dtml-if>):
    """
    """
</dtml-let>
    pass

</dtml-let>
</dtml-in>
