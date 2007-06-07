"""
ObjectManagement.py
Storage and tracking of game objects. Specifically,
these classes are the model and the controller of
our object data.

The view is a custom tree control also herein implemented.
The tree is created and added to a window and its
ObjectDatabase is made note of. The object database
is what the rest of the program interacts with.

There is a concious decision to have a relatively tight coupling
between the control/model and the view, but it would be easy
also to make it more loosely coupled.

Yes, I'm heavily influenced by the way Java
does it in Swing. If necessary the decoupling
will be more complete so as to provide different
views.
"""

import os, wx
from ConfigParser import ConfigParser

class ObjectDatabase(object):
    """
    The object database stores and tracks game objects. It
    also updates the views that are displaying the game
    objects.
    """
    
    def __init__(self, config, tree=None):
        self.config = config
        self.tree = tree
        self.objects = {}
        self.object_modules = {}
        self.save_location = config.get('Current Project', 'project_directory') + "persistence/"
        initObjectTypes()
        return

    def setTree(self, tree):
        """
        Sets the tree which is the view...
        this is what we'd want to make into a
        an add function for multiple listening views
        if we wanted to generalize the control.
        """
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

class GameObjectTree(wx.TreeCtrl):
    def __init__(self, parent, object_types=None, persistence_dir=None, id=-1,
                    pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE,
                    validator=wx.DefaultValidator, name=wx.TreeCtrlNameStr):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        
        self.odb = ObjectDatabase(self)
        
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
            
    def HighlightObjects(self, objects):
        """
        highlights the given objects in the tree
        objects is a hash with keys that are the object types
        and values of object names to highlight
        """
        pass
        
    def ClearHighlight(self):
        """
        clears all highlighting from objects in the tree
        """
        pass
    
    #the following methods allow the tree to have its objects
    # sorted using external functions so that objects of a certain
    # type can supply a certain sorting function and be
    # sorted in that way
    def SortChildrenByFunction(self, item, func):
        """
        Sorts the children of item using the function func.
        """
        self.compare_function = func
        self.SortChildren(item)
        #default operation leaves ordering intact
        # so we make sure to set ourselves back to the default
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
