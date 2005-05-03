from AccessControl import ClassSecurityInfo
from Products.Archetypes.Widget import TypesWidget

class <dtml-var "klass.getCleanName()">(<dtml-var parentname>):
    _properties = <dtml-var parentname>._properties.copy()
    _properties.update({
        'macro' : '<dtml-var "klass.getName()">',
        'size' : '30',
        'maxlength' : '255',
        })

    security = ClassSecurityInfo()
