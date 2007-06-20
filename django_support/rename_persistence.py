"""Rename Persistence means, that the Class or Methods or stuff like that
can be renamed in the UMl-Diagramm, but it source will stay (in difference to the current
AGX behavior)

For this we create a working copy before the Code generation that contains the old names and sources
Because every Object has an Unique ID, this can be used as independet Idendifier to know
what Object will be which object (If you rename Karl to Heinz it's id will stay)

So we create also after every Code-Generation an ID to Names List which stores
the old name and the parent package id for the id of the object

USAGE:
Just call the Do Method with its args

"""
try:
    from XMIParser import XMIElement
except:
    from ArchgenXML.XMIParser import XMIElement

import xml.dom.minidom
import os, csv

id_list = [{},{}]

def ApplyPersistence(obj, recoursive=False):
    obj.persistence = RenamePersistence(obj)

    if recoursive:
        for elem in obj.getChildren() + obj.getMethodDefs():
            if isinstance(elem, XMIElement):
                ApplyPersistence(elem, True)


class Constants:
    name = 0        #this may NEVER be changed
    parent = 1      # this also

    old = 0
    new = 1

    NoParent = 'No Parent'

    class ObjectNotSupported (Exception):
        pass

class RenamePersistence:
    """ This stores an XMIElements Rename Persistence. It will store
    the old name, parent, and the path (also Filepath) to the old file.

    This Class store the ids current name to the id_list
    """

    name = ''       #stores the old name
    obj = None      #stores the object we refer to
    parent = ''     #stores the parents id
    path = None     #caches the path to the object root, neve call directly



    def __init__(self, obj):
        global id_list

        if not isinstance(obj, XMIElement):
            raise Constants.ObjectNotSupported
                #if not allready done initialiyse the persistence:

        if obj.id in id_list[Constants.new]:
            return True    #allready registered Object

        #getting the old names
        self.obj = obj

        if obj.id in id_list[Constants.old]:
            self.name = id_list[Constants.old][obj.id][Constants.name]
            self.parent = id_list[Constants.old][obj.id][Constants.parent]
        else:
            self.name = obj.name
            if obj.getParent():
                self.parent = obj.getParent().id
            else:
                self.parent = Constants.NoParent

        #storing the new Names for the Future Generations
        if isinstance(obj.getParent(), XMIElement):
            parent_id = obj.getParent().id
        else:
            parent_id = Constants.NoParent

        #if id_list is not correctly initialiced (why ever) do that
        try:
            id_list[Constants.new][obj.id] = [obj.name, parent_id]
        except:
            id_list[Constants.new] = {
                  xmi.id: [obj.name, parent_id]
              }

    def getPath(self):
        global id_list
        #adding self first to the path
        parent = self.obj.id
        #is the path already chached?
        if not self.path:

            self.path = []
            if id_list[Constants.old].get(parent,False):
                while parent and parent != Constants.NoParent:

                    #print('parent: %s' % parent)
                    #add the parent to the path
                    self.path.insert(0, id_list[Constants.old][parent][Constants.name])

                    #switch to the parents' parent

                    parent = id_list[Constants.old][parent][Constants.parent]
            else:
                #if no id_list was found use std.path
                if self.obj.getPackage():
                    #use the path of the package
                    self.path = [p.getName() for p in self.obj.getPackage().getPath()] + [self.obj.name]
                else:
                    #this returns mostly only the name, it's the last Fallback
                    #(only Root Package)
                    self.path = [p.getName() for p in self.obj.getPath()]

        #print "Path : %s" % self.path
        return self.path

    def getFilePath(self):
        return os.path.join(*self.getPath())

    def getModuleName(self):
        """Gets the name of the module the class is in."""

        # Zapped tgv 'module_name' in favour of only 'module'
        # [Reinout, 2006-09-04]
        return self.obj.getTaggedValue('module') or self.name

def InitPersistence(filename):
    global id_list
    #read the id_list
    try:
        reader = csv.reader(open(filename,'rb'))
        for elem in reader:
            if len(elem)>=1:
                id_list[Constants.old][elem[0]]=[elem[1],elem[2]]
    except IOError:
        #the functions getting the sources use the default path/name combination
        #if there is not the wanted id in the dict
        #so we can let this free
        print ('Note: found no id list in the backup')

        id_list=[{},{}]

def ClosePersistence(filename):
    global id_list
    #write the id_list...
    writer = csv.writer(open(filename, "wb"))
    writer.writerows([(e[0],e[1][0],e[1][1]) for e in id_list[Constants.new].iteritems()])

def Do(root, readfrom, writeto):
    InitPersistence(readfrom)
    ApplyPersistence(root, recoursive=True)
    ClosePersistence(writeto)
