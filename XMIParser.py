-----------------------------------------------------------------------------
# Name:        XMIParser.py
# Purpose:
#
# Author:      Philipp Auersperg
#
# Created:     2003/19/07
# RCS-ID:      $Id: XMIParser.py,v 1.64 2004/04/13 14:35:38 xiru Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys, os.path, time, string
import getopt

from utils import mapName

from xml.dom import minidom
try:
    from stripogram import html2text
except ImportError:
    def html2text(s,*args,**kwargs):
        return s

#tag constants


class XMI1_0:
    XMI_CONTENT="XMI.content"
    OWNED_ELEMENT="Foundation.Core.Namespace.ownedElement"
    
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
    PARAM_DEFAULT="Foundation.Core.Parameter.defaultValue"
    EXPRESSION="Foundation.Data_Types.Expression"
    EXPRESSION_BODY="Foundation.Data_Types.Expression.body"

    GENERALIZATION="Foundation.Core.Generalization"
    GEN_CHILD="Foundation.Core.Generalization.child"
    GEN_PARENT="Foundation.Core.Generalization.parent"
    GEN_ELEMENT="Foundation.Core.GeneralizableElement"

    TAGGED_VALUE_MODEL="Foundation.Core.ModelElement.taggedValue"
    TAGGED_VALUE="Foundation.Extension_Mechanisms.TaggedValue"
    TAGGED_VALUE_TAG="Foundation.Extension_Mechanisms.TaggedValue.tag"
    TAGGED_VALUE_VALUE="Foundation.Extension_Mechanisms.TaggedValue.value"

    ATTRIBUTE_INIT_VALUE="Foundation.Core.Attribute.initialValue"
    STEREOTYPE="Foundation.Extension_Mechanisms.Stereotype"
    STEREOTYPE_MODELELEMENT="Foundation.Extension_Mechanisms.Stereotype.extendedElement"
    MODELELEMENT="Foundation.Core.ModelElement"
    ISABSTRACT="Foundation.Core.GeneralizableElement.isAbstract"
    INTERFACE="Foundation.Core.Interface"
    ABSTRACTION="Foundation.Core.Abstraction"
    DEP_CLIENT="Foundation.Core.Dependency.client"
    DEP_SUPPLIER="Foundation.Core.Dependency.supplier"
    
    aggregates=['composite','aggregate']

    
    def getName(self,domElement):
        try:
            return str(getAttributeValue(domElement,self.NAME)).strip()
        except:
            return None
    
    def getId(self,domElement):
        return domElement.getAttribute('xmi.id').strip()

    def getAssocEndParticipantId(self,el):
        assocend=getElementByTagName(el,self.ASSOCEND_PARTICIPANT,None)
        
        if not assocend:
            assocend=getElementByTagName(el,self.ASSOCENDTYPE,None)

        if not assocend:
            return None

        classifier=getElementByTagName(assocend,self.CLASSIFIER,None)
        if not classifier:
            classifier=getElementByTagName(assocend,self.CLASS,None)

        if not classifier:
            print 'No assocEnd participant found  for: ',XMI.getId(el)
            return None
                
        return classifier.getAttribute('xmi.idref')

    def isAssocEndAggregation(self,el):
        aggs=el.getElementsByTagName(XMI.AGGREGATION)
        return aggs and aggs[0].getAttribute('xmi.value') in self.aggregates

    def getAssocEndAggregation(self,el):
        aggs=el.getElementsByTagName(XMI.AGGREGATION)
        if not aggs:
            return None
        return aggs[0].getAttribute('xmi.value')

    def getMultiplicity(self,el):
        mult_min=int(getAttributeValue(el,self.MULT_MIN,default=0,recursive=1))
        mult_max=int(getAttributeValue(el,self.MULT_MAX,default=-1,recursive=1))
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
                m=objects.get(masterid,None)
                d=objects.get(detailid,None)

                if not m:
                    print 'Warning: Master Object not found for aggregation relation: id=%s' % (XMI.getId(master))
                    continue

                if not d:
                    print 'Warning: Child Object not found for aggregation relation: parent=%s' % (m.getName())
                    continue
                    
                try:
                    m.addSubType(d)
                except KeyError:
                    print 'Warning: Child Object not found for aggregation relation:Child :%s(%s), parent=%s' % (d.getId(),d.getName(),XMI.getName(m))
                    continue

                assoc=XMIAssociation(rel)
                assoc.fromEnd.obj.addAssocFrom(assoc)
                assoc.toEnd.obj.addAssocTo(assoc)

            else: #its an assoc, lets model it as association
                try:
                    assoc=XMIAssociation(rel)
                except KeyError:
                    print 'Warning: Child Object not found for aggregation:%s, parent=%s' % (XMI.getId(rel),XMI.getName(master))
                    continue

                if getattr(assoc.fromEnd,'obj',None) and getattr(assoc.toEnd,'obj',None):
                    assoc.fromEnd.obj.addAssocFrom(assoc)
                    assoc.toEnd.obj.addAssocTo(assoc)
                else:
                    print 'Warning:Association has no ends:',assoc.getId()


    def buildGeneralizations(self,doc,objects):
        gens=doc.getElementsByTagName(XMI.GENERALIZATION)

        for gen in gens:
            if not self.getId(gen):continue
            try:
                par0=getElementByTagName   (gen,self.GEN_PARENT,recursive=1)
                child0=getElementByTagName (gen,self.GEN_CHILD,recursive=1)
                try:
                    #par=objects[getElementByTagName(par0,self.GEN_ELEMENT).getAttribute('xmi.idref')]
                    par=objects[getSubElement(par0).getAttribute('xmi.idref')]
                except KeyError:
                    print 'Warning: Parent Object not found for generalization relation:%s, parent %s' % (XMI.getId(gen),XMI.getName(par0))
                    continue
                
                #child=objects[getElementByTagName(child0,self.GEN_ELEMENT).getAttribute('xmi.idref')]
                child=objects[getSubElement(child0).getAttribute('xmi.idref')]

                par.addGenChild(child)
                child.addGenParent(par)
            except IndexError:
                print 'gen: index error for generalization:%s'%self.getId(gen)
                raise
                pass

    def buildRealizations(self,doc,objects):
        abs=doc.getElementsByTagName(XMI.ABSTRACTION)

        for ab in abs:
            if not self.getId(ab):continue
            abstraction=XMIAbstraction(ab)
            if not abstraction.hasStereoType('realize'):
                print 'skip dep:',abstraction.getStereoType()
                continue
            try:
                try:
                    par0=getElementByTagName   (ab,self.DEP_SUPPLIER,recursive=1)
                    par=objects[getSubElement(par0,ignoremult=1).getAttribute('xmi.idref')]
                #    continue
                except KeyError:
                    print 'Warning: Parent Object not found for realization relation:%s, parent %s' % (XMI.getId(ab),XMI.getName(par0))
                    continue
                
                #child=objects[getElementByTagName(child0,self.REALIZATION_ELEMENT).getAttribute('xmi.idref')]
                try:
                    child0=getElementByTagName (ab,self.DEP_CLIENT,recursive=1)
                    child_xmid=getSubElement(child0,ignoremult=1).getAttribute('xmi.idref')
                    child=objects[child_xmid]
                except KeyError:
                    print 'Warning: Child element for realization relation not found, parent name + child xmi.id given:',par.getName()

                par.addRealizationChild(child)
                child.addRealizationParent(par)
            except IndexError:
                print 'ab: index error for dependencies:%s'%self.getId(ab)
                raise

    def getExpressionBody(self,element):
        exp = getElementByTagName(element,XMI.EXPRESSION_BODY,recursive=1,default=None)
        if exp and exp.firstChild:
            return exp.firstChild.nodeValue
        else:
            return None

    def getTaggedValue(self,el):
        #print 'getTaggedValue:',el
        tagname=getAttributeValue(el,XMI.TAGGED_VALUE_TAG,recursive=0)
        tagvalue=getAttributeValue(el,XMI.TAGGED_VALUE_VALUE,recursive=0)
        return tagname,tagvalue

    def collectTagDefinitions(self,el):
        ''' dummy function, only needed in xmi >=1.1'''
        pass

    def calculateStereoType(self,o):
        #in xmi its weird, because all objects to which a
        #stereotype applies are stored in the stereotype
        #while in xmi 1.2 its opposite
        for k in stereotypes.keys():
            st=stereotypes[k]
            els=st.getElementsByTagName(self.MODELELEMENT)
            for el in els:
                if el.getAttribute('xmi.idref')==o.getId():
                    name=self.getName(st)
                    #print 'Stereotype found:',name
                    o.setStereoType(name)

    def calcClassAbstract(self,o):
        abs=getElementByTagName(o.domElement,XMI.ISABSTRACT,None)
        if abs:
            o.isabstract=abs.getAttribute('xmi.value')=='true'
        else:
            o.isabstract=0
            
    def calcDatatype(self,att):
        global datatypes
        typeinfos=att.domElement.getElementsByTagName(XMI.TYPE)
        if len(typeinfos):
            classifiers=typeinfos[0].getElementsByTagName(XMI.CLASSIFIER)
            if len(classifiers):
                typeid=str(classifiers[0].getAttribute('xmi.idref'))
                typeElement=datatypes[typeid]
                #self.type=getAttributeValue(typeElement,XMI.NAME)
                att.type=XMI.getName(typeElement)
                if att.type not in datatypenames: #collect all datatype names (to prevent pure datatype classes from being generated)
                    datatypenames.append(att.type)
                #print 'attribute:'+self.getName(),typeid,self.type
                
    def getPackageElements(self,el):
        ''' gets all package nodes below the current node (only one level)'''
        res=[]
        #in case the el is a document we have to crawl down until we have ownedElements
        ownedElements=getElementByTagName(el,self.OWNED_ELEMENT,default=None)
        if not ownedElements:
            el=getElementByTagName(el,self.MODEL,recursive=1)

        ownedElements=getElementByTagName(el,self.OWNED_ELEMENT)
        res=getElementsByTagName(ownedElements,self.PACKAGE)
        
        return res
        
    def getOwnedElement(self,el):
        return getElementByTagName(el,self.OWNED_ELEMENT)
    
    def getModel(self,doc):
        content=getElementByTagName(doc,XMI.XMI_CONTENT,recursive=1)
        model=getElementByTagName(content,XMI.MODEL,recursive=0)

        return model
        
        
        
class XMI1_1 (XMI1_0):
    # XMI version specific stuff goes there

    tagDefinitions=None

    NAME = 'UML:ModelElement.name'
    OWNED_ELEMENT="UML:Namespace.ownedElement"

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

    ATTRIBUTE_INIT_VALUE="UML:Attribute.initialValue"
    EXPRESSION="UML:Expression"
    PARAM_DEFAULT="UML:Parameter.defaultValue"

    TAG_DEFINITION="UML:TagDefinition"

    TAGGED_VALUE_MODEL="UML:ModelElement.taggedValue"
    TAGGED_VALUE="UML:TaggedValue"
    TAGGED_VALUE_TAG="UML:TaggedValue.tag"
    TAGGED_VALUE_VALUE="UML:TaggedValue.value"

    MODELELEMENT="UML:ModelElement"
    STEREOTYPE_MODELELEMENT="UML:ModelElement.stereotype"
    
    STEREOTYPE="UML:Stereotype"
    ISABSTRACT="UML:GeneralizableElement.isAbstract"
    INTERFACE="UML:Interface"

    ABSTRACTION="UML:Abstraction"
    DEP_CLIENT="UML:Dependency.client"
    DEP_SUPPLIER="UML:Dependency.supplier"
        
    def getName(self,domElement):
        return domElement.getAttribute('name').strip()

    def getExpressionBody(self,element):
        exp = getElementByTagName(element,XMI.EXPRESSION,recursive=1,default=None)
        if exp:
            return exp.getAttribute('body')
        else:
            return None



class XMI1_2 (XMI1_1):
    TAGGED_VALUE_VALUE="UML:TaggedValue.dataValue"
    # XMI version specific stuff goes there

    #def getAssocEndParticipantId(self,el):
    #    return getElementByTagName(getElementByTagName(el,self.ASSOCEND_PARTICIPANT),self.CLASS).getAttribute('xmi.idref')

    def isAssocEndAggregation(self,el):
        return str(el.getAttribute('aggregation')) in self.aggregates

    def getAssocEndAggregation(self,el):
        return str(el.getAttribute('aggregation'))

    def getMultiplicity(self,el):
        min=getElementByTagName(el,self.MULTRANGE,default=None,recursive=1)
        max=getElementByTagName(el,self.MULTRANGE,default=None,recursive=1)
        
        if min:
            mult_min=int(min.getAttribute('lower'))
        else:
            mult_min=0
            
        if max:
            mult_max=int(max.getAttribute('upper'))
        else:
            mult_max=-1
            
        return (mult_min,mult_max)

    def getTaggedValue(self,el):
        tdef=getElementByTagName(el,self.TAG_DEFINITION,default=None,recursive=1)
        # fetch the name from the global tagDefinitions (weird)
        tagname=self.tagDefinitions[tdef.getAttribute('xmi.idref')].getAttribute('name')
        tagvalue=getAttributeValue(el,self.TAGGED_VALUE_VALUE)
        return tagname,tagvalue

    def collectTagDefinitions(self,el):
        tagdefs=el.getElementsByTagName(self.TAG_DEFINITION)
        if self.tagDefinitions is None:
            self.tagDefinitions={}

        for t in tagdefs:
            if t.hasAttribute('name'):
                self.tagDefinitions[t.getAttribute('xmi.id')]=t#.getAttribute('name')

        
    def calculateStereoType(self,o):
        #in xmi its weird, because all objects to which a
        #stereotype applies are stored in the stereotype
        #while in xmi 1.2 its opposite

        sts=getElementsByTagName(o.domElement,self.STEREOTYPE_MODELELEMENT,recursive=0)
        for st in sts:
            strefs=getSubElements(st)
            for stref in strefs:
                id=stref.getAttribute('xmi.idref').strip()
                if id:
                    st=stereotypes[id]
                    o.addStereoType(self.getName(st).strip())
                    #print 'stereotype found:',id,self.getName(st),o.getStereoType()
                else:
                    print 'warning: empty stereotype id for class :',o.getName(),o.getId()
                    

    def calcClassAbstract(self,o):
        o.isabstract=o.domElement.hasAttribute('isAbstract') and o.domElement.getAttribute('isAbstract')=='true'
        #print 'xmi12_calcabstract:',o.getName(),o.isAbstract()

    def calcDatatype(self,att):
        global datatypes
        typeinfos=att.domElement.getElementsByTagName(XMI.TYPE)
        if len(typeinfos):
            classifiers=[cn for cn in typeinfos[0].childNodes if cn.nodeType==cn.ELEMENT_NODE] #getElementsByTagName(XMI.CLASS)
            #assert len(classifiers)==1
            if len(classifiers):
                #print 'classifier found for 1.2'
                typeid=str(classifiers[0].getAttribute('xmi.idref'))
                typeElement=datatypes[typeid]
                #self.type=getAttributeValue(typeElement,XMI.NAME)
                att.type=XMI.getName(typeElement)
                if att.type not in datatypenames: #collect all datatype names (to prevent pure datatype classes from being generated)
                    datatypenames.append(att.type)
                #print 'attribute:'+self.getName(),typeid,self.type


XMI=XMI1_0()

_marker=[]

allObjects={}

def getSubElements(domElement):
    return [e for e in domElement.childNodes if e.nodeType==e.ELEMENT_NODE]

def getSubElement(domElement,default=_marker,ignoremult=0):
    els=getSubElements(domElement)
    if len(els) > 1 and not ignoremult:
        raise TypeError,'more than 1 element found'

    try:
        return els[0]
    except IndexError:
        if default == _marker:
            raise
        else:
            return default
    

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

def getAttributeValue(domElement,tagName=None,default=_marker,recursive=0):
    el=domElement
    el.normalize()
    if tagName:
        try:
            el=getElementByTagName(domElement,tagName,recursive=recursive)
        except IndexError:
            if default==_marker:
                raise
            else:
                return default

    return el.firstChild.nodeValue

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
        self.stereoTypes=[]
        self.package=None

        if domElement:
            allObjects[domElement.getAttribute('xmi.id')]=self

        self.initFromDOM(domElement)
        self.buildChildren(domElement)

    def getId(self):
        return self.id

    def parseTaggedValues(self):
        ''' '''
        tgvsm=getElementByTagName(self.domElement,XMI.TAGGED_VALUE_MODEL,default=None,recursive=0)
        if tgvsm is None:
            return

        tgvs=getElementsByTagName(tgvsm, XMI.TAGGED_VALUE, recursive=0)
        try:
            for tgv in tgvs:
                tagname,tagvalue=XMI.getTaggedValue(tgv)
                self.taggedValues[tagname]=tagvalue
        except:
            pass

        #print 'taggedValues:',self.__class__,self.getName(),self.getTaggedValues()

    def initFromDOM(self,domElement):
        if not domElement:
            domElement=self.domElement

        if domElement:
            self.id=domElement.getAttribute('xmi.id')
            self.name=XMI.getName(domElement)
            #print 'name:',self.name,self.id
            self.parseTaggedValues()
            self.calculateStereoType()
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
            res=name
        else:
            res=self.id
            
        if type(res) in (type(''),type(u'')):
            res=res.strip()
        return res

    def getCleanName(self): return self.cleanName

    def getTaggedValue(self,name,default=''):
        res=self.taggedValues.get(name,default)
        if type(res) in (type(''),type(u'')):
            res=res.strip()
        return res

    def hasTaggedValue(self,name):
        return self.taggedValues.has_key(name)

    def getTaggedValues(self):
        return self.taggedValues

    def getDocumentation(self,striphtml=0):
        ret = ''
        if striphtml:
            #TODO: create an option on command line to control the page width
            ret = html2text(self.getTaggedValue('documentation'), (), 0, 60) 
        else:
            ret = self.getTaggedValue('documentation')
        return ret.strip()

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
        for child in self.getChildren():
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


        for child in self.getChildren():
            child.annotate()

    def isIntrinsicType(self):
        return str(self.getType()).startswith('xs:')

    def buildChildren(self,domElement):
        pass

    def getMethodDefs(self,recursive=0):
        res=self.methodDefs
        
        if recursive:
            parents=self.getGenParents(recursive=1)
            for p in parents:
                res.extend(p.getMethodDefs())
                
        return res

    def calculateStereoType(self):
        return XMI.calculateStereoType(self)

    def setStereoType(self,st):
        self.stereoTypes=[st]

    def getStereoType(self):
        if self.stereoTypes:
            return self.stereoTypes[0]
        else:
            return None

    def addStereoType(self,st):
        self.stereoTypes.append(st)

    def getStereoTypes(self):
        return self.stereoTypes

    def hasStereoType(self,sts):
        if type(sts) in (type(''),type(u'')):
            sts=[sts]
            
        for st in sts:
            if st in self.getStereoTypes():
                return 1
            
        return 0
    
    def getFullQualifiedName():
        return self.getName()
    
    def getPackage(self):
        ''' returns the package to which this object belongs '''
        return self.package

    def getPath(self):
        return [self.getName()]


class XMIPackage(XMIElement):
    project=None
    isroot=0

    def __init__(self,el):
        XMIElement.__init__(self,el)
        self.classes=[]
        self.interfaces=[]
        self.packages=[]
        
    def initFromDOM(self,domElement=None):
        self.parentPackage=None
        XMIElement.initFromDOM(self,domElement)
        
    def setParent(self,parent):
        self.parent=parent
        
    def getParent(self):
        return self.parent
    
    def getClasses(self,recursive=0):
        res=[c for c in self.classes]
        return self.classes    
    
    def addClass(self,cl):
        self.classes.append(cl)
        cl.package=self

    def addInterface(self,cl):
        self.interfaces.append(cl)
        cl.package=self
        
    def getInterfaces(self):
        return self.interfaces

    def getChildren(self):
        return self.children+self.getClasses() + self.getPackages() + self.getInterfaces()
    
    def addPackage(self,p):
        self.packages.append(p)
        p.parent=self
        
    def getPackages(self):
        return self.packages
    

    def buildPackages(self):
        packEls=XMI.getPackageElements(self.domElement)
        for p in packEls:
            if XMI.getName(p)=='java':
                continue
            package=XMIPackage(p)
            self.addPackage(package)
            package.buildPackages()

    def buildClasses(self):
        #print 'buildClasses:',self.getFilePath(includeRoot=1)
        ownedElement=XMI.getOwnedElement(self.domElement)
        classes=getElementsByTagName(ownedElement,XMI.CLASS)
        for c in classes:
            xc=XMIClass(c)
            if xc.getName():
                print 'Class:',xc.getName(),xc.id
                self.addClass(xc)
                
        for p in self.getPackages():
            p.buildClasses()

    def buildInterfaces(self):
        #print 'buildInterfaces:',self.getFilePath(includeRoot=1)
        ownedElement=XMI.getOwnedElement(self.domElement)
        classes=getElementsByTagName(ownedElement,XMI.INTERFACE)
        for c in classes:
            xc=XMIInterface(c)
            if xc.getName():
                #print 'Interface:',xc.getName(),xc.id
                self.addInterface(xc)
                
        for p in self.getPackages():
            p.buildInterfaces()
            
    def buildClassesAndInterfaces(self):
        self.buildClasses()
        self.buildInterfaces()            
        
    def isRoot(self):
        return self.isroot or self.hasStereoType(['product','zopeproduct','Product','ZopeProduct'])

    isProduct=isRoot
    
    def getPath(self,includeRoot=1,absolute=0,parent=None):
        res=[]
        o=self
        
        if self.isProduct():
            #products are always handled as top-level
            if includeRoot:
                return [self]
            else:
                return []
        
        while 1:
            if includeRoot:
                res.append(o)
                
            if o.isProduct():
                break
            if not o.getParent():
                break
            if o==parent:
                break

            if not includeRoot:
                res.append(o)
                
            o=o.getParent()
            
        res.reverse()
        return res
    
    def getFilePath(self,includeRoot=1,absolute=0):
        names=[p.getName() for p in self.getPath(includeRoot=includeRoot,absolute=absolute)]
        if not names:
            return ''
        
        res=os.path.join(*names)
        return res
    
    def getRootPackage(self):
        o=self
        while not o.isRoot():
            o=o.getParent()
            
        return o
    
    def getProduct(self):
        o=self
        while not o.isProduct():
            o=o.getParent()
            
        return o

    def getProductName(self):
        return self.getProduct().getName()
    
    def isSubPackageOf(self,parent):
        o=self
        #print 'isSubPackage:',self.getName(),parent.getName()
        while o:
            #print 'compare:',o.getName()
            if o==parent:
                #print 'ys'
                return 1
            
            o=o.getParent()
        
        return 0
    
    def getQualifiedName(self,ref):
        ''' returns the qualified name of tha package, depending of the 
            reference package 'ref' it generates an absolute path or 
            a relative path if the pack(self) is a subpack of 'ref' '''
            
        path=self.getPath(parent=ref)
        return path

class XMIModel(XMIPackage):
    isroot=1
    parent=None
    
    def __init__(self,doc):
        self.document=doc
        self.model=XMI.getModel(doc)
        XMIPackage.__init__(self,self.model)
        

class XMIClass (XMIElement):
    package=None
    isinterface=0
    
    def __init__(self,*args,**kw):
        XMIElement.__init__(self,*args,**kw)
        self.assocsTo=[]
        self.assocsFrom=[]
        self.genChildren=[]
        self.genParents=[]
        self.realizationChildren=[]
        self.realizationParents=[]
        self.internalOnly=0
        self.type=self.name
        #self.isabstract=0

    def initFromDOM(self,domElement):
        XMIElement.initFromDOM(self,domElement)
        XMI.calcClassAbstract(self)

    def isInternal(self):
        ''' internal class '''
        return self.internalOnly
    
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

    def getGenParents(self,recursive=0):
        ''' generalization parents '''
        res=self.genParents

        if recursive:
            for r in res:
                res.extend(r.getGenParents(1))
        
        return res

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

    def getToAssociations(self,aggtypes=['none']):
        return [a for a in self.assocsTo if a.fromEnd.aggregation in aggtypes]

    def getFromAssociations(self,aggtypes=['none']):
        return [a for a in self.assocsFrom if a.fromEnd.aggregation in aggtypes]
        #return self.assocsFrom

    def isDependent(self):
        ''' every object to which only composite assocs point shouldnt be created independently '''
        aggs=self.getToAssociations(aggtypes=['aggregate'])
        comps=self.getToAssociations(aggtypes=['composite'])
    
        if comps and not aggs:
            res=1
        else:
            res=0

        # if one of the parents is dependent, count the class as dependent
        for p in self.getGenParents():
            if p.isDependent():
                res=1
                
        return res 

    def isAbstract(self):
        return self.isabstract

    def getSubtypeNames(self,recursive=0):
        ''' returns the non-intrinsic subtypes '''

        res = [o.getName() for o in self.subTypes if not o.isAbstract()]

        if recursive:
            for sc in self.subTypes:
                res.extend([o.getName() for o in sc.getGenChildren(recursive=1)])
        return res
    
    def isI18N(self):
        ''' if at least one method is I18N the class has to be treated as i18N '''
        for a in self.getAttributeDefs():
            if a.isI18N():
                return 1
        
        return 0
    
    def getPackage(self):
        return self.package
    
    def getRootPackage(self):
        return self.getPackage().getRootPackage()
    
    def isInterface(self):
        #print 'interface:',self.getName(),self.getStereoType()
        return self.isinterface  or self.getStereoType()=='interface' 
        # the second branch is for older XMI engines where interface is just a stereotype of a class


    # for relization stuff
    def addRealizationChild(self,c):
        self.realizationChildren.append(c)

    def addRealizationParent(self,c):
        self.realizationParents.append(c)

    def getRealizationChildren(self,recursive=0):
        ''' realization children '''

        res=self.realizationChildren

        if recursive:
            for r in res:
                res.extend(r.getRealizationChildren(1))

        return res

    def getRealizationChildrenNames(self, recursive=0):
        ''' returns the names of the realization children '''
        return [o.getName() for o in self.getRealizationChildren(recursive=recursive) ]

    def getRealizationParents(self):
        ''' generalization parents '''
        return self.realizationParents

    def getQualifiedModulePath(self,ref):
        ''' returns the qualified name of the class, depending of the 
            reference package 'ref' it generates an absolute path or 
            a relative path if the pack(self) is a subpack of 'ref' 
            if it belongs to a different root package it even needs a 'Products.'
            '''
            
        package=self.getPackage()
        
        if package.isSubPackageOf(ref):
            path=package.getPath(includeRoot=0,parent=ref)
        else:
            path=package.getPath(includeRoot=1,parent=ref)
            
        path.append(self)

        return path
    
    def getQualifiedModuleName(self,ref):
        path=self.getQualifiedModulePath(ref)
        res= '.'.join([p.getName() for p in path if p])
        if self.package.getProduct() != ref.getProduct():
            res='Products.'+res
        
        return res

    
    def getQualifiedName(self,ref):
        path=self.getQualifiedModulePath(ref)
        path.append(self)
        res='.'.join([p.getName() for p in path if p])
        if self.package.getProduct() != ref.getProduct():
            res='Products.'+res
        return res
        
class XMIInterface(XMIClass):
    isinterface=1
    pass


class XMIMethodParameter(XMIElement):
    default=None
    has_default=0

    def getDefault(self):
        return self.default

    def hasDefault(self):
        return self.has_default

    def findDefault(self):
        defparam=getElementByTagName(self.domElement,XMI.PARAM_DEFAULT,None)
        #print defparam
        if defparam:
            default=XMI.getExpressionBody(defparam)
            if default :
                self.default=default
                self.has_default=1
                #print 'default:',repr(self.default)

    def initFromDOM(self,domElement):
        XMIElement.initFromDOM(self,domElement)
        if domElement:
            self.findDefault()

    def getExpression(self):
        ''' returns the param name and param=default expr if a default is defined '''
        if self.getDefault():
            return "%s=%s" % (self.getName(),self.getDefault())
        else:
            return self.getName()

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

    def getParamExpressions(self):
        ''' returns the param names or paramname=default for each param in a list '''
        return [p.getExpression() for p in self.params]

    def addParameter(self,p):
        if p.getName() != 'return':
            self.params.append(p)

class XMIAttribute (XMIElement):
    default=None
    has_default=0

    def getDefault(self):
        return self.default

    def hasDefault(self):
        return self.has_default

    def calcType(self):
        return XMI.calcDatatype(self)

    def findDefault(self):
        initval=getElementByTagName(self.domElement,XMI.ATTRIBUTE_INIT_VALUE,None)
        if initval:
            default=XMI.getExpressionBody(initval)
            if default :
                self.default=default
                self.has_default=1
                #print 'default:',repr(self.default)

    def initFromDOM(self,domElement):
        XMIElement.initFromDOM(self,domElement)
        if domElement:
            self.calcType()
            self.findDefault()
            
    def isI18N(self):
        ''' with a stereotype 'i18N' or the taggedValue i18n=='1' an attribute is treated as i18n'''
        return self.getStereoType()=='i18n' or self.getTaggedValue('i18n') =='1'


class XMIAssocEnd (XMIElement):
    def initFromDOM(self,el):
        XMIElement.initFromDOM(self,el)
        pid=XMI.getAssocEndParticipantId(el)
        if pid:
            self.obj=allObjects[pid]
            self.mult=XMI.getMultiplicity(el)
            self.aggregation=XMI.getAssocEndAggregation(el)
        else:
            print 'Association end missing for association end:'+self.getId()
        #print 'aggreg:',self.aggregation


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

class XMIAbstraction(XMIElement):
    pass
        
def buildDataTypes(doc):
    global datatypes
    
    dts=doc.getElementsByTagName(XMI.DATATYPE)

    for dt in dts:
        datatypes[str(dt.getAttribute('xmi.id'))]=dt

    classes=[c for c in doc.getElementsByTagName(XMI.CLASS) ]

    for dt in classes:
        datatypes[str(dt.getAttribute('xmi.id'))]=dt

    interfaces=[c for c in doc.getElementsByTagName(XMI.INTERFACE) ]

    for dt in interfaces:
        datatypes[str(dt.getAttribute('xmi.id'))]=dt

    XMI.collectTagDefinitions(doc)

def buildStereoTypes(doc):
    global stereotypes
    sts=doc.getElementsByTagName(XMI.STEREOTYPE)

    for st in sts:
        id=st.getAttribute('xmi.id')
        if not id:continue
        stereotypes[str(id)]=st
        #print 'stereotype:',id,XMI.getName(st)

def buildHierarchy(doc,packagenames):
    """ builds Hierarchy out of the doc """
    global datatypes
    global stereotypes
    global datatypenames
    global packages
    
    
    datatypes={}
    stereotypes={}
    datatypenames=['int','void','string',]

    #doc=res.model

    buildDataTypes(doc)
    buildStereoTypes(doc)
    res=XMIModel(doc)

    print 'packagenames:', packagenames
    packageElements=doc.getElementsByTagName(XMI.PACKAGE)
    if packagenames: #XXX: TODO support for more than one package
        packageElements=doc.getElementsByTagName(XMI.PACKAGE)
        for p in packageElements:
            n=XMI.getName(p)
            print 'package name:',n
            if n in packagenames:
                doc=p
                print 'package found'
                break

    buildDataTypes(doc)

    res.buildPackages()
    res.buildClassesAndInterfaces()

    print 'res:',res.getName()
    
    #pure datatype classes should not be generated!
    #print 'datatypenames:',datatypenames
    for c in res.getClasses(recursive=1):
        if c.getName() in datatypenames:
            c.internalOnly=1
            print 'internal class (not generated):',c.getName()
            
    res.annotate()
    XMI.buildRelations(doc,allObjects)
    XMI.buildGeneralizations(doc,allObjects)
    XMI.buildRealizations(doc,allObjects)
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
