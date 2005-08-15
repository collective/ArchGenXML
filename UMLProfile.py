# [Reinout]: I added some logging just to make sure: this class
# isn't used anywhere in the code. I propose clearing out this
# file and start a StereotypeSupport.py file instead, modelled
# on TaggedValueSupport.py and OptionParser.py.
# We *do* want documented stereotypes! :-)

import logging
log = logging.getLogger('umlprofile')

class ChainedDict(dict):
    ''' chained dict class allows to conatenate dictionaries '''
    
    parent_chain=[]
    
    def __init__(self, parent_chain=[], **kw):
        log.debug("Initializing ChainedDict class.")
        dict.__init__(self,**kw)
        self.parent_chain=parent_chain
        self._keys = []
        
    def __getitem__(self,key):
        if dict.has_key(self,key):
            return dict.__getitem__(self,key)
        
        for p in self.getParentChain():
            if p.has_key(key):
                return p.__getitem__(key)
            
        raise KeyError,key
            
    def getParentChain(self):
        return self.parent_chain
    
    def addToParentChain(self,d):
        self.parent_chain.append(d)

    def __iter__(self):
        return iter(self.keys())

    def clear(self):
        dict.clear(self)
        self._keys = []

    def items(self):
        res=dict.items(self)
        for p in self.getParentChain():
            res.extend(p.items())
            
        return res

    def keys(self):
        res=dict.keys(self)
        for p in self.getParentChain():
            res.extend(p.keys())
            
        return res

    def values(self):
        return map(self.get, self.keys())

    def get(self,key,default=None):
        if dict.has_key(self,key):
            return dict.get(self,key)
        
        for p in self.getParentChain():
            if p.has_key(key):
                return p.get(key)

class ProfileEntry:
    ''' base class '''
    
    def __init__(self,name,entities,**kw):
        log.debug("Initializing ProfileEntry class.")
        self.name=name
        self.entities=entities
        self.__dict__.update(kw)
        
        
    def __repr__(self):
        return '<%s name=%s entities=%s>' %(self.__class__.__name__,self.name,repr(self.entities))
    
    def getName(self):
        return self.name


class TaggedValue(ProfileEntry):
    ''' represents a tagged value with its attributes '''
    
    
class StereoType(ProfileEntry):
    ''' represents a stereotype with its attributes '''
    
class UMLProfile:
    ''' '''
    
    def __init__(self,parents=[]):
        log.debug("Initializing UMLProfile.")
        if type(parents) not in (type(()),type([])):
            parents=[parents]

        # Tagged values are handled by TaggedValueSupport.
        # I modelled that class on OptionParser.py, I didn't know this
        # class existed... [Reinout]
        #self.taggedValues=ChainedDict([p.taggedValues for p in parents])
        self.stereoTypes=ChainedDict([p.stereoTypes for p in parents])
    
    def addStereoType(self, name, entities, **kw):
        log.debug("Adding stereotype '%s' to registry.",
                  name)
        tgv=StereoType(name,entities,**kw)
        self.stereoTypes[name]=tgv
        
    def filterObjects(self,list,entities,**kw):
        res=[]
        #import pdb;pdb.set_trace()
        for item in list:
            
            #if one of the entities aplies, its ok
            if entities:
                ok=0
                for e in entities:
                    if e in item.entities:
                        ok=1
                        continue
                    
                if not ok:
                    continue 
            ok=1
            for k in kw:
                if getattr(item,k,None) != kw[k]:
                    ok=0

            if not ok:
                continue
            
            res.append(item)
        
        return res
    
    def getAllStereoTypes(self):
        return self.stereoTypes.values()
    
    def findStereoTypes(self,entities=[],**kw):
        list=self.getAllStereoTypes()
        return self.filterObjects(list,entities,**kw)
    
    def getStereoType(self,name):
        return self.stereoTypes.get(name,None)
    
    
# test 'em

if __name__=='__main__':
    a={'a1':'a1v','a2':'a2v'}
    ca=ChainedDict([a],ca1='ca1v',ca2='ca2v')
    
    print a
    print ca.keys()
    print ca.get('a1')
    print ca['a2'],ca['ca1']
    
    baseprofile=UMLProfile()
    baseprofile.addStereoType('python_class',['XMIClass'])
    baseprofile.addStereoType('portal_type',['XMIClass'],murf=1)
    baseprofile.addStereoType('view',['XMIMethod'])
    print baseprofile.getAllStereoTypes()


    archprofile=UMLProfile(baseprofile)
    archprofile.addStereoType('cmfmember',['XMIClass'])
    
    print archprofile.findStereoTypes(entities=['XMIClass'])
    print archprofile.findStereoTypes(entities=['XMIMethod'])
    print archprofile.findStereoTypes(entities=['XMIClass'],murf=1)
    
