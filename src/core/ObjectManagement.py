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
import ConfigParser
from ConfigParser import ConfigParser
import RDE
import game_objects.ObjectUtilities

class ObjectDatabase(object):
    """
    The object database stores and tracks game objects. It
    also updates the views that are displaying the game
    objects.
    """
    
    def __init__(self, tree):
        self.config = RDE.GlobalConfig.config
        self.tree = tree
        #hash of object names
        self.objects = {}
        #hash of object modules
        self.object_modules = self.initObjectTypes()
        self.save_location = self.config.get('Current Project', 'persistence_directory')
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
        
    def loadObjectNames(self):
        """
        Loads the names of the objects from persistent storage
        so that we can pupulate out tree of objects.
        """
        #print "Trying to dynamically load objects from storage"
        for name, module in self.object_modules.iteritems():
            print "Loading object names for object type: " + name
            object_dir = self.save_location + name
            #grab the object names from the filenames and use them to populate
            # the lists of objects
            self.objects[name] = [file.partition('.')[0] for file in os.listdir(object_dir)]
            #print "Object list:"
            #for o in self.objects[name]:
            #    print o
        self.tree.InitializeTree()

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
    
    def getObjectTypes(self):
        return self.object_modules.keys()
        
    def getObjectModule(self, type):
        if not self.object_modules.has_key(type):
            raise ValueError('No such object type')
        return self.object_modules[type]
        
    def getObjectsOfType(self, type):
        if not self.objects.has_key(type):
            raise ValueError('No such object type')
        return self.objects[type]

class GameObjectTree(wx.TreeCtrl):
    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize,
                    style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT, validator=wx.DefaultValidator,
                    name=wx.TreeCtrlNameStr):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        self.odb = ObjectDatabase(self)

    def getObjectDatabase(self):
        return self.odb
                 
    def AddObject(self, type, name):
        pass
        
    def RemoveObject(self, type, name):
        pass
        
    def InitializeTree(self):
        self.root_id = self.AddRoot('root')
        self.type_ids = {}
        self.object_ids = {}
        for object_type in self.odb.getObjectTypes():
            self.type_ids[object_type] = self.AppendItem(self.root_id, object_type)
            self.SetPyData(self.type_ids[object_type], DefaultNode(object_type))
            for object_name in self.odb.getObjectsOfType(object_type):
                self.object_ids[object_name] = self.AppendItem(self.type_ids[object_type], object_name)
                self.SetPyData(self.object_ids[object_name],
                               game_objects.ObjectUtilities.ObjectNode(
                                        self.odb.getObjectModule(object_type), object_name))
            
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

    
class DatabaseNode(object):
    def generateEditPanel(self, parent):
        print "Generating DefaultNode panel"
        panel = wx.Panel(parent, wx.ID_ANY)
        panel.SetBackgroundColour('white')
        label = wx.StaticText(panel, wx.ID_ANY, "Default Node Panel")
        return panel    
   
            
class DefaultNode(DatabaseNode):
    def __init__(self, name):
        self.name = name
    
    def generateEditPanel(self, parent):
        print "Generating panel for [%s]" % self.name
        panel = wx.Panel(parent, wx.ID_ANY)
        panel.SetBackgroundColour('white')
        label = wx.StaticText(panel, wx.ID_ANY, "Test panel for value %s" % self.name)
        return panel    
