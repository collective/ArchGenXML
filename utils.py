
import sys, os.path, time
import getopt

NameTable = {
    'class': 'klass',
    'import': 'emport'
    }

def makeFile(outFileName,force=1):
    outFile = None
    if (not force) and os.path.exists(outFileName):
        return None
    elif (force=='ask') and os.path.exists(outFileName):
        reply = raw_input('File %s exists.  Overwrite? (y/n): ' % outFileName)
        if reply == 'y':
            outFile = open(outFileName, 'w')
        else:
            return None
    else:
        outFile = open(outFileName, 'w')
    return outFile

def makeDir(outFileName,force=1):
    outFile = None
    if (not force) and os.path.exists(outFileName):
        reply = raw_input('File %s exists.  Overwrite? (y/n): ' % outFileName)
        if reply == 'y':
            os.mkdir(outFileName)
    else:
        if not os.path.exists(outFileName):
            os.mkdir(outFileName)



def mapName(oldName):
    #global NameTable
    newName = oldName

    if NameTable:
        if oldName in NameTable.keys():
            newName = NameTable[oldName]
    return newName.replace('-','_')

def indent(s,indent,prepend='',skipFirstRow=0):
    rows=s.split('\n')
    if skipFirstRow:
        lines=[rows[0]]+['    '*indent + prepend + l for l in rows[1:]]
    else:
        lines=['    '*indent + prepend + l for l in rows]
        
    return '\n'.join(lines)

def getExpression(s):
    '''
    interprets an expression (for permission settings and other taggedValues)
    if an exp is a string it will be kept, if not it will be enclosed by quotes
    if an exp starts with python: it will be not quoted
    '''

    s=s.strip()
    if s=='':
        return s
    
    if s[0]=='"' and s[-1]=='"' or s[0]=="'" and s[-1]=="'":
        return s
    else:
        if s.startswith('python:'):
            return s[7:]
        else:
            return "'''%s'''" % s
        
def isTGVTrue(tgv):
    if type(tgv) in (type(''),type(u'')):
        tgv=tgv.lower()
        
    return tgv in (1,'1','true')

def isTGVFalse(tgv):
    if type(tgv) in (type(''),type(u'')):
        tgv=tgv.lower()
        
    return tgv in (0,'0','false')