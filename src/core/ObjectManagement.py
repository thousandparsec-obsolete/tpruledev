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
import RDE, Nodes
import game_objects.ObjectUtilities

class ObjectDatabase(object):
    """
    The object database stores and tracks game objects. It
    also updates the views that are displaying the game
    objects.
    """
    
    def __init__(self):
        self.config = RDE.GlobalConfig.config
        #hash of object names
        self.objects = {}
        #hash of object modules
        self.object_modules = self.initObjectTypes()
        self.save_location = self.config.get('Current Project', 'persistence_directory')
        self.odb_listeners = []
        return

    def getTree(self, parent, id=wx.ID_ANY):
        tree = GameObjectTree(self, parent, id)
        self.addODBListener(tree)
        return tree
        
    def initObjectTypes(self):
        #print "Trying to initialize object types"
        object_modules = {}
        for name in self.config.get('Object Types', 'types').split(', '):
            name = name.strip()
            object_modules[name] = __import__("game_objects." + name, globals(), locals(), [''])
        return object_modules
        
    def loadObjectNodes(self):
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
            self.objects[name] = [game_objects.ObjectUtilities.ObjectNode(self, filename.partition('.')[0], module) for filename in os.listdir(object_dir)]
            #print "Object list:"
            #for o in self.objects[name]:
            #    print o
        #alert listeners to happy initialization
        self.sendODBEvent(ODBInitialize())

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
            
    def highlight(self, obj_names):
        #todo: this can be so much more elegant
        if isinstance(obj_names, list):
            self.sendODBEvent(ODBHighlight(obj_names))
        else:
            self.sendODBEvent(ODBHighlight([obj_names]))
        
    def unhighlight(self, obj_names):
        #todo: this can be so much more elegant
        if isinstance(obj_names, list):
            self.sendODBEvent(ODBUnHighlight(obj_names))
        else:
            self.sendODBEvent(ODBUnHighlight([obj_names]))
    
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
        
    #listener interface
    def addODBListener(self, listener):
        if not listener in self.odb_listeners:
            self.odb_listeners.append(listener)
    
    def removeODBListener(self, listener):
        if listener in self.odb_listeners:
            self.odb_listeners.remove(listener)
    
    def sendODBEvent(self, event):
        for l in self.odb_listeners:
            l.handleODBEvent(event)


#Object Database even objects
class ODBEvent(object):
    """
    Base Object Database Event object.
    All of the event types are included here.
    """
    #I WANT ENUMS!
    INIT = 1
    ADD = 2
    REMOVE = 3
    MODIFY = 4
    HIGHLIGHT = 5
    UNHIGHLIGHT = 6
    CLEAR_MARKERS = 7

class ODBInitialize(ODBEvent):
    type = ODBEvent.INIT

class ODBAdd(ODBEvent):
    type = ODBEvent.ADD
    
    def __init__(self, names):
        self.names = names

class ODBRemove(ODBEvent):
    type = ODBEvent.REMOVE
    
    def __init__(self, names):
        self.names = names
    
class ODBModify(ODBEvent):
    type = ODBEvent.MODIFY
    
    def __init__(self, names):
        self.names = names

class ODBHighlight(ODBEvent):
    type = ODBEvent.HIGHLIGHT
    
    def __init__(self, names):
        self.names = names
    
class ODBUnHighlight(ODBEvent):
    type = ODBEvent.UNHIGHLIGHT
    
    def __init__(self, names):
        self.names = names
    
class ODBClearMarkers(ODBEvent):
    type = ODBEvent.CLEAR_MARKERS
    
    
class GameObjectTree(wx.TreeCtrl):
    """
    The default display for game objects. Based on
    a wx.TreeCtrl
    """
    
    def __init__(self, parent, id=-1, object_database = None, pos=wx.DefaultPosition, size=wx.DefaultSize,
                    style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT, validator=wx.DefaultValidator,
                    name=wx.TreeCtrlNameStr):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        self.odb = object_database 
        
    def SetObjectDatabase(self, odb):
        self.odb = odb
             
    def AddObject(self, type, name):
        pass
        
    def RemoveObject(self, type, name):
        pass
        
    def handleODBEvent(self, event):
        self.eventDict[event.type](self, event)
        
    def HandleInit(self, event):
        self.InitializeTree()
    
    def HandleAdd(self, event):
        pass
    
    def HandleRemove(self, event):
        pass
    
    def HandleModify(self, event):
        pass
    
    def HandleHighlight(self, event):
        #todo: error handling
        print "Handling highlight"
        for obj_name in event.names:
            print "Highlighting object: ", obj_name
            id = self.object_ids[obj_name]
            self.SetItemBackgroundColour(id, 'RED')
    
    def HandleUnHighlight(self, event):
        #todo: error handling
        print "Handling unhighlight"
        for obj_name in event.names:
            print "Unhighlighting object: ", obj_name
            id = self.object_ids[obj_name]
            self.SetItemBackgroundColour(id, 'WHITE')
    
    def HandleClear(self, event):
        pass
        
    def InitializeTree(self):
        self.root_id = self.AddRoot('root')
        self.type_ids = {}
        self.object_ids = {}
        for object_type in self.odb.getObjectTypes():
            self.type_ids[object_type] = self.AppendItem(self.root_id, object_type)
            self.SetPyData(self.type_ids[object_type], Nodes.DefaultNode(object_type))
            for node in self.odb.getObjectsOfType(object_type):
                object_name = node.name
                self.object_ids[object_name] = self.AppendItem(self.type_ids[object_type], object_name)
                self.SetPyData(self.object_ids[object_name], node)
            
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
            
    eventDict = {ODBEvent.INIT: HandleInit,
                 ODBEvent.ADD: HandleAdd,
                 ODBEvent.REMOVE: HandleRemove,
                 ODBEvent.MODIFY: HandleModify,
                 ODBEvent.HIGHLIGHT: HandleHighlight,
                 ODBEvent.UNHIGHLIGHT: HandleUnHighlight,
                 ODBEvent.CLEAR_MARKERS: HandleClear}
