
import sys, os.path, time, string
import getopt
from xml.sax import saxexts, saxlib, saxutils
from xml.sax import handler

from utils import mapName

from xml.dom import minidom

#tag constants

def getAttributeValue(domElement,tagName=None,recursive=0):
    el=domElement
    if tagName:
        el=getElementByTagName(domElement,tagName,recursive=recursive)
    return el.firstChild.nodeValue

class XMI1_0:
    # XMI version specific stuff goes there
    STATEMACHINE = 'Behavioral_Elements.State_Machines.StateMachine'
    STATE = 'Behavioral_Elements.State_Machines.State'
    TRANSITION='Behavioral_Elements.State_Machines.Transition'
    # each TRANSITION has (in its defn) a TRIGGER which is an EVENT
    EVENT = 'Behavioral_Elements.State_Machines.SignalEvent'
    # and a TARGET (and its SOURCE) which has a STATE
    SOURCE = 'Behavioral_Elements.State_Machines.Transition.source'
    TARGET = 'Behavioral_Elements.State_Machines.Transition.target'
    # ACTIONBODY gives us the rate of the transition
    ACTIONBODY = 'Foundation.Data_Types.Expression.body'

    # STATEs and EVENTs both have NAMEs
    NAME = 'Foundation.Core.ModelElement.name'

    #Collaboration stuff: a
    COLLAB = 'Behavioral_Elements.Collaborations.Collaboration'
    # has some
    CR = 'Behavioral_Elements.Collaborations.ClassifierRole'
    # each of which has a
    BASE = 'Behavioral_Elements.Collaborations.ClassifierRole.base'
    # which we will assume to be a CLASS, collapsing otherwise
    CLASS = 'Foundation.Core.Class'

    # To match up a CR with the right start state,  we look out for the context
    CONTEXT = 'Behavioral_Elements.State_Machines.StateMachine.context'
    MODEL='Model_Management.Model'
    MULTIPLICITY='Foundation.Core.StructuralFeature.multiplicity'
    MULT_MIN='Foundation.Data_Types.MultiplicityRange.lower'
    MULT_MAX='Foundation.Data_Types.MultiplicityRange.upper'
    ATTRIBUTE='Foundation.Core.Attribute'
    DATATYPE='Foundation.Core.DataType'
    FEATURE='Foundation.Core.Classifier.feature'
    TYPE='Foundation.Core.StructuralFeature.type'
    ASSOCEND_PARTICIPANT=CLASSIFIER='Foundation.Core.Classifier'
    ASSOCIATION='Foundation.Core.Association'
    AGGREGATION='Foundation.Core.AssociationEnd.aggregation'
    ASSOCEND='Foundation.Core.AssociationEnd'
    ASSOCENDTYPE='Foundation.Core.AssociationEnd.type'

    METHOD="Foundation.Core.Operation"
    METHODPARAMETER="Foundation.Core.Parameter"

    aggregates=['composite','aggregate']

    def getName(self,domElement):
        try:
            return str(getAttributeValue(domElement,self.NAME))
        except:
            return None

    def getAssocEndParticipantId(self,el):
        return getElementByTagName(getElementByTagName(el,self.ASSOCENDTYPE),self.CLASSIFIER).getAttribute('xmi.idref')

    def isAssocEndAggregation(self,el):
        aggs=el.getElementsByTagName(XMI.AGGREGATION)        
        return aggs and aggs[0].getAttribute('xmi.value') in self.aggregates        
    
    def getMultiplicity(self,el):
        mult_min=int(getAttributeValue(el,self.MULT_MIN,recursive=1))
        mult_max=int(getAttributeValue(el,self.MULT_MAX,recursive=1))
        return (mult_min,mult_max)
        
    def buildRelations(self, doc, objects):
        #XXX: needs refactoring
        rels=doc.getElementsByTagName(XMI.ASSOCIATION)
        for rel in rels:
            master=None
            detail=None
            ends=rel.getElementsByTagName(XMI.ASSOCEND)
            #assert len(ends)==2
            if len(ends) != 2:
                #print 'association with != 2 ends found'
                continue

            if self.isAssocEndAggregation(ends[0]) :
                master=ends[0]
                detail=ends[1]
            if self.isAssocEndAggregation(ends[1]) :
                master=ends[1]
                detail=ends[0]

            if master: #ok weve found an aggregation
                masterid=self.getAssocEndParticipantId(master)
                detailid=self.getAssocEndParticipantId(detail)

                #print 'master,detail:',master,detail
                m=objects[masterid]
                d=objects[detailid]
                m.addSubType(d)
            else: #its an assoc, lets model it as association
                
                assoc=XMIAssociation(rel)
                assoc.fromEnd.obj.addAssocTo(assoc)
                assoc.toEnd.obj.addAssocFrom(assoc)

class XMI1_2 (XMI1_0):
    # XMI version specific stuff goes there

    NAME = 'UML:ModelElement.name'
    MODEL = 'UML:Model'
    #Collaboration stuff: a
    COLLAB = 'Behavioral_Elements.Collaborations.Collaboration'
    CLASS = 'UML:Class'

    # To match up a CR with the right start state,  we look out for the context
    MULTIPLICITY='UML:StructuralFeature.multiplicity'
    ATTRIBUTE='UML:Attribute'
    DATATYPE='UML:DataType'
    FEATURE='UML:Classifier.feature'
    TYPE='UML:StructuralFeature.type'
    CLASSIFIER='UML:Classifier'
    ASSOCIATION='UML:Association'
    AGGREGATION='UML:AssociationEnd.aggregation'
    ASSOCEND='UML:AssociationEnd'
    ASSOCENDTYPE='UML:AssociationEnd.type'
    ASSOCEND_PARTICIPANT='UML:AssociationEnd.participant'
    METHOD="UML:Operation"
    METHODPARAMETER="UML:Parameter"
    MULTRANGE='UML:MultiplicityRange'

    def getName(self,domElement):
        return domElement.getAttribute('name')

    def getAssocEndParticipantId(self,el):
        return getElementByTagName(getElementByTagName(el,self.ASSOCEND_PARTICIPANT),self.CLASS).getAttribute('xmi.idref')
    
    def isAssocEndAggregation(self,el):
        return str(el.getAttribute('aggregation')) in self.aggregates        
    
    def getMultiplicity(self,el):
        mult_min=int(getElementByTagName(el,self.MULTRANGE,recursive=1).getAttribute('lower'))
        mult_max=int(getElementByTagName(el,self.MULTRANGE,recursive=1).getAttribute('upper'))
        return (mult_min,mult_max)

XMI=XMI1_0()

_marker=[]

allObjects={}


def getElementByTagName(domElement,tagName,default=_marker, recursive=0):
    ''' returns a single element by name and throws an error if more than 1 exist'''
    if recursive:
        els=domElement.getElementsByTagName(tagName)
    else:
        els=[el for el in domElement.childNodes if str(getattr(el,'tagName',None)) == tagName]
        
    if len(els) > 1:
        raise TypeError,'more than 1 element found'

    try:
        return els[0]
    except IndexError:
        if default == _marker:
            raise
        else:
            return default
    def getMethodDefs(self):
        return self.methodDefs

def hasClassFeatures(domClass):

    return len(domClass.getElementsByTagName(XMI.FEATURE)) or           \
                len(domClass.getElementsByTagName(XMI.ATTRIBUTE)) or    \
                len(domClass.getElementsByTagName(XMI.METHOD))

class XMIElement:
    def __init__(self, domElement=None,name=''):
        self.domElement=domElement
        self.name = name
        self.cleanName = ''
        self.atts={}
        self.children = []
        self.maxOccurs = 1
        self.complex = 0
        self.type = 'NoneType'
        self.attributeDefs = []
        self.methodDefs=[]

        self.subTypes=[]

        if domElement:
            allObjects[domElement.getAttribute('xmi.id')]=self

        self.initFromDOM(domElement)
        self.buildChildren(domElement)

    def initFromDOM(self,domElement=None):
        if not domElement:
            domElement=self.domElement
            
        if domElement:
            self.name=XMI.getName(domElement)
            mult=getElementByTagName(domElement,XMI.MULTIPLICITY,None)
            if mult:
                maxNodes=mult.getElementsByTagName(XMI.MULT_MAX)
                if maxNodes and len(maxNodes):
                    maxNode=maxNodes[0]
                    self.maxOccurs=int(getAttributeValue(maxNode))
                    if self.maxOccurs==-1:
                        self.maxOccurs=99999

                    #print 'maxOccurs:',self.maxOccurs


    def addChild(self, element):
        self.children.append(element)
    def addSubType(self,st):
        self.subTypes.append(st)

    def getChildren(self): return self.children
    def getName(self): return str(self.name)
    def getCleanName(self): return self.cleanName
    def getUnmappedCleanName(self): return self.unmappedCleanName
    def setName(self, name): self.name = name
    def getAttrs(self): return self.attrs
    def getMaxOccurs(self): return self.maxOccurs
    def getType(self): return self.type
    def isComplex(self): return self.complex
    def addAttributeDefs(self, attrs): self.attributeDefs.append(attrs)
    def getAttributeDefs(self): return self.attributeDefs
    
    def getRef(self):
        return None

    def getRefs(self):
        ''' return all referenced schema names '''

        return [str(c.getRef()) for c in self.getChildren() if c.getRef()]

    def getSubtypeNames(self):
        ''' returns the non-intrinsic subtypes '''
        return [o.getName() for o in self.subTypes]

    def show(self, outfile, level):
        showLevel(outfile, level)
        outfile.write('Name: %s  Type: %s\n' % (self.name, self.type))
        showLevel(outfile, level)
        outfile.write('  - Complex: %d  MaxOccurs: %d\n' % \
            (self.complex, self.maxOccurs))
        showLevel(outfile, level)
        outfile.write('  - Attrs: %s\n' % self.attrs)
        showLevel(outfile, level)
        outfile.write('  - AttributeDefs: %s\n' % self.attributeDefs)
        for key in self.attributeDefs.keys():
            showLevel(outfile, level + 1)
            outfile.write('key: %s  value: %s\n' % \
                (key, self.attributeDefs[key]))
        for child in self.children:
            child.show(outfile, level + 1)

    def addMethodDefs(self,m):
        if m.getName():
            self.methodDefs.append(m)

    def annotate(self):
        # If there is a namespace, replace it with an underscore.
        trans=string.maketrans(':-.', '___')
        if self.name:
            self.unmappedCleanName = str(self.name).translate(trans)
        else:
            self.unmappedCleanName = ''

        self.cleanName = mapName(self.unmappedCleanName)
##        if 'maxOccurs' in self.attrs.keys():
##            max = self.attrs['maxOccurs']
##            if max == 'unbounded':
##                max = 99999
##            else:
##                try:
##                    max = int(self.attrs['maxOccurs'])
##                except ValueError:
##                    sys.stderr.write('*** %s/%s  maxOccurs must be integer or "unbounded".' % \
##                        (element.getName(), child.getName())
##                        )
##                    sys.exit(-1)
##        else:
##            max = 1
##        self.maxOccurs = max

##        if 'type' in self.attrs.keys():
##            type1 = self.attrs['type']
##            if type1 == 'xs:string' or \
##                type1 == 'xs:integer' or \
##                type1 == 'xs:float':
##                self.complex = 0
##            else:
##                self.complex = 1
##            self.type = self.attrs['type']
##        else:
##            self.complex = 1
##            self.type = 'NoneType'
##        # If it does not have a type, then make the type the same as the name.
##        if self.type == 'NoneType' and self.name:
##            self.type = self.name
##        # Do it recursively for all descendents.

##        # refs
##        if 'ref' in self.attrs.keys():
##            self.ref=self.attrs['ref']


        for child in self.children:
            child.annotate()

    def isIntrinsicType(self):
        return str(self.getType()).startswith('xs:')

    def buildChildren(self,domElement):
        pass

    def getMethodDefs(self):
        return self.methodDefs

class XMIClass (XMIElement):
    
    def __init__(self,*args,**kw):
        XMIElement.__init__(self,*args,**kw)
        self.assocsTo=[]
        self.assocsFrom=[]
        self.type=self.name


    def buildChildren(self,domElement):
        for el in domElement.getElementsByTagName(XMI.ATTRIBUTE):
            self.addAttributeDefs(XMIAttribute(el))
        for el in domElement.getElementsByTagName(XMI.METHOD):
            self.addMethodDefs(XMIMethod(el))

    def isComplex(self):
        return 1
    
    def addAssocFrom(self,a):
        self.assocsFrom.append(a)
        
    def addAssocTo(self,a):
        self.assocsTo.append(a)

    def getToAssociations(self):
        return self.assocsTo
    
    def getFromAssociations(self):
        return self.assocsFrom
    
    
class XMIMethodParameter(XMIElement):
    pass

class XMIMethod (XMIElement):
    params=[]
    def findParameters(self):
        self.params=[]
        parElements=self.domElement.getElementsByTagName(XMI.METHODPARAMETER)
        for p in parElements:
            self.addParameter(XMIMethodParameter(p))
            #print self.params

    def initFromDOM(self,domElement):
        XMIElement.initFromDOM(self,domElement)
        if domElement:
            self.findParameters()

    def getParams(self):
        return self.params

    def getParamNames(self):
        return [p.getName() for p in self.params]

    def addParameter(self,p):
        if p.getName() != 'return':
            self.params.append(p)

class XMIAttribute (XMIElement):
    def calcType(self):
        global datatypes
        typeinfos=self.domElement.getElementsByTagName(XMI.TYPE)
        if len(typeinfos):
            classifiers=typeinfos[0].getElementsByTagName(XMI.CLASSIFIER)
            if len(classifiers):
                typeid=str(classifiers[0].getAttribute('xmi.idref'))
                typeElement=datatypes[typeid]
                #self.type=getAttributeValue(typeElement,XMI.NAME)
                self.type=XMI.getName(typeElement)
                #print 'attribute:'+self.getName(),typeid,self.type

    def initFromDOM(self,domElement):
        XMIElement.initFromDOM(self,domElement)
        if domElement:
            self.calcType()

class XMIAssocEnd (XMIElement):
    def initFromDOM(self,el):
        XMIElement.initFromDOM(self,el)
        pid=XMI.getAssocEndParticipantId(el)
        self.obj=allObjects[pid]
        self.mult=XMI.getMultiplicity(el)
        #print 'mult;',self.mult,self.getName()
        
class XMIAssociation (XMIElement):
    fromEnd=None
    toEnd=None

    def initFromDOM(self,domElement=None):
        XMIElement.initFromDOM(self,domElement)
        ends=self.domElement.getElementsByTagName(XMI.ASSOCEND)
        assert len(ends)==2
        #if len(ends) != 2:

        #print 'trying assoc'
        self.fromEnd=XMIAssocEnd(ends[0])
        self.toEnd=XMIAssocEnd(ends[1])
    

def buildDataTypes(doc):
    global datatypes
    dts=doc.getElementsByTagName(XMI.DATATYPE)

    for dt in dts:
        datatypes[str(dt.getAttribute('xmi.id'))]=dt

    classes=[c for c in doc.getElementsByTagName(XMI.CLASS) ]

    for dt in classes:
        datatypes[str(dt.getAttribute('xmi.id'))]=dt


def buildHierarchy(doc):
    """ builds Hierarchy out of the doc """
    global datatypes
    datatypes={}
    buildDataTypes(doc)

    res=XMIElement()

    #try to get the name out of the model
    xmis=doc.getElementsByTagName(XMI.MODEL)
    if len(xmis)==1:
        print 'model name:',XMI.getName(xmis[0])
        res.setName(XMI.getName(xmis[0]))

    classes=doc.getElementsByTagName(XMI.CLASS)
    #print 'classes:',classes
    for c in classes:
        if hasClassFeatures(c):
            xc=XMIClass(c)
            print 'Class:',xc.getName()
            res.addChild(xc)

    res.annotate()
    XMI.buildRelations(doc,allObjects)
    return res


def parse(xschemaFileName=None,xschema=None):
    """ """
    global XMI

    if xschemaFileName:
        doc=minidom.parse(xschemaFileName)
    else:
        doc=minidom.parseString(xschema)

    try:
        xmi=doc.getElementsByTagName('XMI')[0]
        xmiver=str(xmi.getAttribute('xmi.version'))
        print 'XMI version:', xmiver
        if xmiver >= "1.2":
            print 'using xmi 1.2 parser'
            XMI=XMI1_2()

    except:
        print 'no version info found, taking XMI1_0'
        pass

    root=buildHierarchy(doc)
    return root


