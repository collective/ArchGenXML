
import sys, os.path, time
import getopt
from xml.sax import saxexts, saxlib, saxutils
from xml.sax import handler

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

def indent(s,indent,prepend=''):
    lines=['    '*indent + prepend + l for l in s.split('\n')]
    return '\n'.join(lines)
