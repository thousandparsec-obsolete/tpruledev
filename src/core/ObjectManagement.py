"""
ObjectManagement.py
Storage and tracking of game objects. Specifically,
these classes are the model and the controller of
our object data.

The view is a custom tree control.
"""

import os, wx
from ConfigParser import ConfigParser

class ObjectDatabase(object):
    """Object database stores and tracks game objects"""
    
    def __init__(self, config, tree=None):
        self.config = config
        self.tree = tree
        self.objects = {}
        self.object_modules = {}
        self.save_location = config.get('Current Project', 'project_directory') + "persistence/"
        return
        
    def setSaveLocation(self, save_location):
        """
        probably don't need this anymore
        """
        self.save_location = save_location
        
    def setTreeRoot(self, tree):
        self.tree = tree            

    def initObjectTypes(self):
        #print "Trying to initialize object types"
        object_modules = {}
        for name in self.config.get('Object Types', 'types').split(', '):
            name = name.strip()
            object_modules[name] = __import__("game_objects." + name, globals(), locals(), [''])
        return object_modules

    def loadObjectsFromStorage(self):
        #print "Trying to dynamically load objects from storage"
        self.object_modules = self.initObjectTypes()
        for name, module in self.object_modules.iteritems():
            print "Loading objects of type: " + name
            self.objects[name] = []
            persistence_dir = self.save_location + name
            files = os.listdir(persistence_dir)
            for f in files:
                #print "Loading File: ", f
                self.objects[name].append(module.Object(file=persistence_dir + "/" + f))
            #print "Object list:"
            #for o in self.objects[name]:
            #    print o
        self.tree.populateTree()

    def add(self, obj_type, obj):
        if not self.objects.has_key(obj_type):
            self.objects[obj_type] = []
        self.objects[obj_type].append(obj)

    def remove(self, obj_type, obj):
        try:
            self.objects[obj_type].remove(obj)
        except:
            #no such object - so...uh...through an exception, hey?
            print "No such object to be removed."

#define the events pertaining to the game object database
BASE_EVENT          = 0
HIGHLIGHT_EVENT     = 1
ADD_EVENT           = 2
REMOVE_EVENT        = 3
    
class GameObjectEvent(object):
    type = BASE_EVENT
    
    def __init__(self, type):
        self.type = type
        
class ObjectHighlightEvent(GameObjectEvent):
    def __init__(self, objects):
        GameObjectEvent.__init(HIGHLIGHT_EVENT)
        self.objects = objects
        
class ObjectAddEvent(GameObjectEvent):
    def __init__(self, objects):
        GameObjectEvent.__init(ADD_EVENT)
        self.objects = objects

class ObjectRemoveEvent(GameObjectEvent):
    def __init__(self, objects):
        GameObjectEvent.__init(REMOVE_EVENT)
        self.objects = objects


class GameObjectTree(wx.TreeCtrl):
    def __init__(self, parent, object_types=None, persistence_dir=None, id=-1,
                    pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE,
                    validator=wx.DefaultValidator, name=wx.TreeCtrlNameStr):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        
        self.odb = ObjectDatabase()
        
        #if passed a list of object types and a persistence
        # directory then we can initialize our tree without
        # further ado
        if object_types and persistence_dir:
            self.object_types = object_types            
            self.persistence_dir = persistence_dir
            self.InitializeTree()
            
    def SetObjectTypes(self, types):
        self.object_types = types
        
    def SetPersistenceDirectory(self, pdir):
        self.persistence_dir = pdir
        
    def AddObject(self, type, name):
        pass
        
    def RemoveObject(self, type, name):
        pass
        
    def InitializeTree(self):
        if not self.object_types or not self.persistence_dir:
            #fail and throw exception
            return
        else:
            pass            


class GameObjectTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TR_DEFAULT_STYLE, validator=wx.DefaultValidator, name=wx.TreeCtrlNameStr):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        self.compare_function = lambda x, y: 0
        
    def populateTree(self):
        """
        fills the treectrl in the main window with
        the objects loaded from persistence
        """
       #TODO add a check here for a non-None tree

        root = self.GetRootItem()
        for name, module in self.object_modules.iteritems():
            main_node = self.AppendItem(root, name)
            self.SetPyData(main_node, module)

            for obj in self.objects[name]:
                object_node = self.AppendItem(main_node, obj.name)
                self.SetPyData(object_node, obj)
        
    def HighlightObjects(self, objects):
        """
        highlights the given objects in the tree
        objects is a hash with keys that are the object types
        and values of object names to highlight
        """
        return
        
    def ClearHighlight(self):
        """
        clears all highlighting from objects in the tree
        """
        return

    def SortChildrenByFunction(self, item, func):
        self.compare_function = func
        self.SortChildren(item)
        #default operation leaves ordering intact
        self.compare_function = lambda x, y: 0

    def OnCompareItems(self, item1, item2):
        """
        This particular OnCompareItems function passes the PyData objects of
        the nodes to be compared to the function provided as a comparison technique.
        """
        if self.compare_function:
            return self.compare_function(self.GetPyData(item1), self.GetPyData(item2))
        else:
            return 0
