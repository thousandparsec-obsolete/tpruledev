"""
ObjectManagement.py
Storage and tracking of game objects. Specifically,
these classes are the model and the controller of
our object data.

The view is a custom tree control.
"""

import os, wx
from ConfigParser import ConfigParser

class ObjectDatabase:
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

    def populateTree(self, tree=None):
        """
        fills the treectrl in the main window with
        the objects loaded from persistence
        """
        if (tree):
            self.tree = tree

        #TODO add a check here for a non-None tree

        root = tree.GetRootItem()
        for name, module in self.object_modules.iteritems():
            main_node = tree.AppendItem(root, name)
            tree.SetPyData(main_node, module)

            for obj in self.objects[name]:
                object_node = tree.AppendItem(main_node, obj.name)
                tree.SetPyData(object_node, obj)
            

    def initObjectTypes(self):
        #print "Trying to initialize object types"
        #TODO following line prone to breaking likely...fix it
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


class GameObjectTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TR_DEFAULT_STYLE, validator=wx.DefaultValidator, name=wx.TreeCtrlNameStr):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        self.compare_function = lambda x, y: 0

    def SortChildrenByFunction(self, item, func):
        self.compare_function = func
        self.SortChildren(item)
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
