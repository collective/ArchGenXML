# very simple module for extracting classes and
# method codes out of a python file


import parser
import pprint
import sys
import types

PROTECTED_BEGIN='##code-section'
PROTECTED_END='##/code-section'


def codeLength(l):
    ''' calculates the length of a method using the code.co_lnotab '''
    res=0
    for i in range(0,len(l),2):
        res += ord(l[i+1])

    return res+1

def extractCode(arr,start,lnotab):
    ''' extracts method code from an array containing the code lines,
        given a start (zero based) and a lnotab '''
    snip=[]
    length = 0

    for i in range(0,len(lnotab),2):
        cl=ord(lnotab[i+1])
        if cl != 255:
            length += cl

    # and now take into account the trailing backslashes
    while arr[start+length].strip() and arr[start+length].strip()[-1]=='\\':
            length += 1
        
    snip = arr[start:start+length+1]
    return '\n'.join(snip)

        
class PyCodeElement:
    module=None
    code=None
    src=None

    def __init__(self,code,module):
        self.code=code
        self.module=module
        
    def getSrc(self):
        return self.src

class PyMethod(PyCodeElement):
    
    def __init__(self,code,module):
        PyCodeElement.__init__(self,code,module)
        
        self.buildMethod()
        
    def buildMethod(self):
        self.name=self.code.co_name
        start=self.code.co_firstlineno
        length=codeLength(self.code.co_lnotab)
        self.src=extractCode(self.module.splittedSource,start-1,self.code.co_lnotab)

    def printit(self):
        print 'method:',self.code.co_name
        print '-------------------------------------------------------'
        print self.src
        print '-------------------------------------------------------'

    def getProtectedSection(self,section):
        return self.module.getProtectedSection(section)
    
class PyClass(PyCodeElement):
    methods={}
    module=None
    
    def __init__(self,code,module):
        PyCodeElement.__init__(self,code,module)
        self.methods={}
        self.name=code.co_name
        self.module=module
        #print 'Class:',self.name
        
        self.buildMethods()
        
    def buildMethods(self):
        meths=[o for o in self.code.co_consts if type(o) == types.CodeType]
        for c in meths:
            name=c.co_name
            self.methods[name]=PyMethod(c,self.module)
            
    def printit(self):
        print '======================================='
        print self.name
        print '======================================='
        
        for m in self.methods.values():
            m.printit()
            
    def getProtectedSection(self,section):
        return self.module.getProtectedSection(section)
    
class PyModule:
    filebuf=None
    splittedSource=None
    ast=None
    code=None
    src=None
    classes={}
    protectedSections={}
    
    
    def __init__(self,file):
        self.classes={}
        #print 'init PyModule:',file
        self.initFromFile(file)
        
    def initFromFile(self,file):
        if type(file) in (type(''),type(u'')):
            self.filebuf=open(file).read()
        else:
            #assume its a file object
            self.filebuf=file.read()
            
        self.splittedSource=self.filebuf.split('\n')
        self.ast=parser.suite(self.filebuf)
        self.code=self.ast.compile()
        self.initFromCode()

    def isItAClass(self,c):
        ''' woooh - heuristic method to check if a code fragment is a class '''
        
        fl=c.co_firstlineno
        if self.splittedSource[fl-1].strip().startswith('class'):
            return 1
        
        res=len([o for o in c.co_consts if type(o) == types.CodeType])
        #print 'Class:####',c.co_name,res,c.co_consts
        return res

        
    def initFromCode(self):
        
        #collect code elements in the class
        codes=[c for c in self.code.co_consts if type(c) == types.CodeType]
        #print 'codes:',codes
        classes=[c for c in codes if self.isItAClass(c)]
        for c in classes:
            klass=PyClass(c,self)
            self.classes[c.co_name]=klass
            
        self.findProtectedSections()
    
    def findProtectedSections(self):
        for i in xrange(0,len(self.splittedSource)):
            line=self.splittedSource[i]
            sline=line.strip()
            if sline.startswith(PROTECTED_BEGIN):
                j=start=i
                sectionname=sline.split()[1]
                try:
                    while not self.splittedSource[j].strip().startswith(PROTECTED_END):
                        j=j+1
                except IndexError:
                    return
                
                end=j
                self.protectedSections[sectionname]='\n'.join(self.splittedSource[start+1:end])
                
                
                
    def getProtectedSection(self,section):
        return self.protectedSections.get(section)

    def printit(self):
        print 'PyModule:',
        for c in self.classes.values():
            c.printit()
            
if __name__=='__main__':
   mod=PyModule(sys.argv[1])
   mod.printit()
   
