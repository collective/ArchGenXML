#-----------------------------------------------------------------------------
# Name:        XMIParser.py
# Purpose:     
#
# Author:      Philipp Auersperg
#
# Created:     2003/19/07
# RCS-ID:      $Id: XMIParser.py,v 1.12 2003/07/19 11:47:03 zworkb Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys, os.path, time, string
import getopt
from xml.sax import saxexts, saxlib, saxutils
from xml.sax import handler

from utils import mapName

from xml.dom import minidom

#tag constants

def getAttributeValue(domElement,tagName=None,recursive=0):
    el=domElement
    el.normalize()
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
    PACKAGE='Model_Management.Package'
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
    
    GENERALIZATION="Foundation.Core.Generalization"
    GEN_CHILD="Foundation.Core.Generalization.child"
    GEN_PARENT="Foundation.Core.Generalization.parent"
    GEN_ELEMENT="Foundation.Core.GeneralizableElement"
    
    TAGGED_VALUE_MODEL="Foundation.Core.ModelElement.taggedValue"
    TAGGED_VALUE="Foundation.Extension_Mechanisms.TaggedValue"
    TAGGED_VALUE_TAG="Foundation.Extension_Mechanisms.TaggedValue.tag"
    TAGGED_VALUE_VALUE="Foundation.Extension_Mechanisms.TaggedValue.value"
    
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

    def buildGeneralizations(self,doc,objects):
        gens=doc.getElementsByTagName(XMI.GENERALIZATION)
        
        for gen in gens:
            try:
                par0=getElementByTagName   (gen,self.GEN_PARENT)
                child0=getElementByTagName (gen,self.GEN_CHILD)
                par=objects[getElementByTagName(par0,self.GEN_ELEMENT).getAttribute('xmi.idref')]
                child=objects[getElementByTagName(child0,self.GEN_ELEMENT).getAttribute('xmi.idref')]
                
                par.addGenChild(child)
                child.addGenParent(par)
            except IndexError:
                pass


class XMI1_1 (XMI1_0):
    # XMI version specific stuff goes there

    NAME = 'UML:ModelElement.name'
    MODEL = 'UML:Model'
    #Collaboration stuff: a
    COLLAB = 'Behavioral_Elements.Collaborations.Collaboration'
    CLASS = 'UML:Class'
    PACKAGE = 'UML:Package'
    
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

    MULT_MIN='UML:MultiplicityRange.lower'
    MULT_MAX='UML:MultiplicityRange.upper'

    GENERALIZATION="UML:Generalization"
    GEN_CHILD="UML:Generalization.child"
    GEN_PARENT="UML:Generalization.parent"
    GEN_ELEMENT="UML:Class"

    def getName(self,domElement):
        return domElement.getAttribute('name')

        
class XMI1_2 (XMI1_1):
    # XMI version specific stuff goes there

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

def getElementsByTagName(domElement,tagName, recursive=0):
    ''' returns elements by tag name , the only difference 
        to the original getElementsByTagName is, that the optional recursive
        parameter
        '''
        
    if recursive:
        els=domElement.getElementsByTagName(tagName)
    else:
        els=[el for el in domElement.childNodes if str(getattr(el,'tagName',None)) == tagName]
        
    return els

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
        self.id=''
        self.taggedValues={}
        self.subTypes=[]

        if domElement:
            allObjects[domElement.getAttribute('xmi.id')]=self

        self.initFromDOM(domElement)
        self.buildChildren(domElement)

    def parseTaggedValues(self):
        ''' '''
        tgvsm=getElementByTagName(self.domElement,XMI.TAGGED_VALUE_MODEL,default=None,recursive=0)
        
        if tgvsm is None:
            return
        
        tgvs=getElementsByTagName(tgvsm, XMI.TAGGED_VALUE, recursive=0)
        
        try:
            for tgv in tgvs:
                tagname=getAttributeValue(tgv,XMI.TAGGED_VALUE_TAG,recursive=0)
                tagvalue=getAttributeValue(tgv,XMI.TAGGED_VALUE_VALUE,recursive=0)
                self.taggedValues[tagname]=tagvalue
        except:
            pass
        
        
    def initFromDOM(self,domElement):
        if not domElement:
            domElement=self.domElement
        
        if domElement:
            self.id=domElement.getAttribute('xmi.id')
            self.name=XMI.getName(domElement)
            #print 'name:',self.name,self.id
            self.parseTaggedValues()
            
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
    def getName(self): 
        name=str(self.name)
        if self.name:
            return name
        else:
            return self.id
        
    def getCleanName(self): return self.cleanName
    
    def getTaggedValue(self,name,default=''):
        return self.taggedValues.get(name,default)
    
    def getDocumentation(self):
        return self.getTaggedValue('documentation')
    
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
        self.genChildren=[]
        self.genParents=[]
        
        self.type=self.name

    def addGenChild(self,c):
        self.genChildren.append(c)
        
    def addGenParent(self,c):
        self.genParents.append(c)
        
    def getGenChildren(self,recursive=0):
        ''' generalization children '''

        res=self.genChildren

        if recursive:
            for r in res:
                res.extend(r.getGenChildren(1))

        return res

    def getGenChildrenNames(self, recursive=0):
        ''' returns the names of the generalization children '''
        return [o.getName() for o in self.getGenChildren(recursive=recursive) ]
    
    def getGenParents(self):
        ''' generalization parents '''
        return self.genParents
    
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
    
    def isAbstract(self):
        return 0

    def getSubtypeNames(self,recursive=0):
        ''' returns the non-intrinsic subtypes '''

        res = [o.getName() for o in self.subTypes]
        
        if recursive:
            for sc in self.subTypes:
                res.extend([o.getName() for o in sc.getGenChildren(recursive=1)])
        return res
    
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
        #print 'mult;',self.mult,self.getName(),self.id
        
class XMIAssociation (XMIElement):
    fromEnd=None
    toEnd=None

    def initFromDOM(self,domElement=None):
        XMIElement.initFromDOM(self,domElement)
        #print 'Association:',domElement,self.id
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


def buildHierarchy(doc,packagenames):
    """ builds Hierarchy out of the doc """
    global datatypes
    datatypes={}

    buildDataTypes(doc)

    print 'packagenames:', packagenames
    if packagenames: #XXX: TODO support for more than one package
        packages=doc.getElementsByTagName(XMI.PACKAGE)
        for p in packages:
            n=XMI.getName(p)
            print 'package name:',n
            if n in packagenames:
                doc=p
                print 'package found'
                break
        
    buildDataTypes(doc)

    res=XMIElement()

    #try to get the name out of the model
    xmis=doc.getElementsByTagName(XMI.MODEL)
    if len(xmis)==1:
        #print 'model name:',XMI.getName(xmis[0])
        res.setName(XMI.getName(xmis[0]))

    classes=doc.getElementsByTagName(XMI.CLASS)
    for c in classes:
        if 1 or hasClassFeatures(c):
            xc=XMIClass(c)
            print 'Class:',xc.getName(),xc.id
            res.addChild(xc)


    res.annotate()
    XMI.buildRelations(doc,allObjects)
    XMI.buildGeneralizations(doc,allObjects)
    return res


def parse(xschemaFileName=None,xschema=None,packages=[]):
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
            print 'using xmi 1.2+ parser'
            XMI=XMI1_2()
        elif xmiver >= "1.1":
            print 'using xmi 1.1+ parser'
            XMI=XMI1_1()

    except:
        print 'no version info found, taking XMI1_0'
        pass

    root=buildHierarchy(doc,packages)
    return root


