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
import ConfigParser, bisect
from ConfigParser import ConfigParser
import RDE, Nodes
import game_objects.ObjectUtilities
from core.Exceptions import *

if hasattr(str, 'partition'):
	def partition(str, sep):
		return str.partition(sep)
else:
	def partition(str, sep):
		a, b = str.split(sep, 1)
		return (a, sep, b)

class ObjectDatabase(object):
    """
    The object database stores and tracks game objects. It
    also updates the views that are displaying the game
    objects.
    """
    
    highlighted = []
    emphasized = []
    
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
            #print "Loading object names for object type: " + name
            object_dir = os.path.join(self.save_location, name)
            #grab the object names from the filenames and use them to populate
            # the lists of objects
            self.objects[name] = [game_objects.ObjectUtilities.ObjectNode(self, partition(filename, '.')[0], module) for filename in os.listdir(object_dir)]
            self.objects[name].sort()
            #print "Object list:"
            #for o in self.objects[name]:
            #    print o
        #alert listeners to happy initialization
        self.sendODBEvent(ODBInitialize())
        
    def SaveObjects(self):
        """\
        Saves each modified object to its persistence file
        """
        print "Saving objects!"
        for type, module in self.object_modules.iteritems():
            print "Saving objects of type: %s" % type
            for node in self.objects[type]:
                if node.modified:
                    print "\tSaving %s - %s" % (type, node.name)
                    module.saveObject(node.getObject()) 
                    node.modified = False
                    self.UnHighlight(node.name)          

    def Add(self, obj_type, name):
        #check for duplicate object
        # also raise error if no such object type
        if self.ObjectExists(obj_type, name):
            raise DuplicateObjectError(name)
                
        #find out where we need to put it and stick it in there
        idx = bisect.bisect(self.objects[obj_type], name)
        print "Adding object " + name
        print "Object list: ", [o.__str__() for o in self.objects[obj_type]]
        print "Index of " + name + ": ", idx
        node = game_objects.ObjectUtilities.ObjectNode(self, name, self.object_modules[obj_type])
        self.objects[obj_type].insert(idx, node)
        print "New Object List: ", [o.__str__() for o in self.objects[obj_type]]
        
        #let our listeners know we added a new object and let them
        # know the parent in terms of alphabetical order
        if idx == 0:
            #if we're inserting at the start there is no preceding element
            self.sendODBEvent(ODBAdd(node, obj_type, None))
        else:
            self.sendODBEvent(ODBAdd(node, obj_type, self.objects[obj_type][idx-1].name))

    def Remove(self, obj_type, name):
        if not self.ObjectExists(obj_type, name):
            raise NoSuchObjectError(name)
            
        print "Removing an object"
        print "Object List Before: ", [o.__str__() for o in self.objects[obj_type]]
        self.objects[obj_type].remove(name)
        self.object_modules[obj_type].deleteSaveFile(name)
        print "New Object List: ", [o.__str__() for o in self.objects[obj_type]]
        self.sendODBEvent(ODBRemove(name))
           
    def ObjectExists(self, obj_type, name):
        #check that the object type exists
        if not self.objects.has_key(obj_type):
            raise NoSuchTypeError(obj_type.__str__())
        #check that we don't already have an existing object using this name
        for otype in self.objects:
            if name in self.objects[otype]:
                return True
        return False
            
    def Highlight(self, obj_names, color="RED"):
        #todo: this can be so much more elegant
        if isinstance(obj_names, list):
            for name in obj_names:
                if not name in self.highlighted:
                    self.highlights.append(name)
            self.sendODBEvent(ODBHighlight(obj_names, color))
        else:
            if not obj_names in self.highlighted:
                self.highlighted.append(obj_names)
            self.sendODBEvent(ODBHighlight([obj_names], color))
        
    def UnHighlight(self, obj_names):
        #todo: this can be so much more elegant
        if isinstance(obj_names, list):
            for name in obj_names:
                try:
                    self.highlighted.remove(name)
                except ValueError:
                    #don't care that it wasn't there
                    pass
            self.sendODBEvent(ODBUnHighlight(obj_names))
        else:
            try:
                self.highlighted.remove(obj_names)
            except ValueError:
                #don't care that it wasn't there
                pass
            self.sendODBEvent(ODBUnHighlight([obj_names]))        
            
    def Emphasize(self, obj_names, color="BLUE"):
        #todo: this can be so much more elegant
        #todo: this can be so much more elegant
        if isinstance(obj_names, list):
            for name in obj_names:
                if not name in self.emphasized:
                    self.emphasized.append(name)
            self.sendODBEvent(ODBEmphasize(obj_names, color))
        else:
            if not obj_names in self.emphasized:
                self.emphasized.append(obj_names)
            self.sendODBEvent(ODBEmphasize([obj_names], color))
        
    def UnEmphasize(self, obj_names):
        #todo: this can be so much more elegant
        if isinstance(obj_names, list):
            for name in obj_names:
                try:
                    self.emphasized.remove(name)
                except ValueError:
                    #don't care that it wasn't there
                    pass
            self.sendODBEvent(ODBUnEmphasize(obj_names))
        else:
            try:
                self.emphasized.remove(obj_names)
            except ValueError:
                #don't care that it wasn't there
                pass
            self.sendODBEvent(ODBUnEmphasize([obj_names])) 
    
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
    EMPHASIZE = 8
    UNEMPHASIZE = 9
    UNINIT = 10

class ODBInitialize(ODBEvent):
    type = ODBEvent.INIT

class ODBAdd(ODBEvent):
    type = ODBEvent.ADD
    
    def __init__(self, node, type, preceding):
        self.node = node
        self.obj_type = type
        self.preceding = preceding

class ODBRemove(ODBEvent):
    type = ODBEvent.REMOVE
    
    def __init__(self, name):
        self.name = name
    
class ODBModify(ODBEvent):
    type = ODBEvent.MODIFY
    
    def __init__(self, names):
        self.names = names

class ODBHighlight(ODBEvent):
    type = ODBEvent.HIGHLIGHT
    
    def __init__(self, names, color):
        self.names = names
        self.color = color
    
class ODBUnHighlight(ODBEvent):
    type = ODBEvent.UNHIGHLIGHT
    
    def __init__(self, names):
        self.names = names
    
class ODBClearMarkers(ODBEvent):
    type = ODBEvent.CLEAR_MARKERS
    
class ODBEmphasize(ODBEvent):
    type = ODBEvent.EMPHASIZE
    
    def __init__(self, names, color):
        self.names = names
        self.color = color
    
class ODBUnEmphasize(ODBEvent):
    type = ODBEvent.UNEMPHASIZE
    
    def __init__(self, names):
        self.names = names
        
class ODBClearMarkers(ODBEvent):
    type = ODBEvent.UNINIT
    
    
class GameObjectTree(wx.TreeCtrl):
    """
    The default display for game objects. Based on
    a wx.TreeCtrl
    """
    
    def __init__(self, parent, id=-1, object_database = None, pos=wx.DefaultPosition, size=wx.DefaultSize,
                    style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_SINGLE , validator=wx.DefaultValidator,
                    name=wx.TreeCtrlNameStr):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        self.odb = object_database
        self.root_id = self.AddRoot('RDE')
        self.SetPyData(self.root_id, RDE)
        
    def SetObjectDatabase(self, odb):
        self.odb = odb
        odb.addODBListener(self)
             
    def RemoveObject(self, type, name):
        pass
        
    def handleODBEvent(self, event):
        self.eventDict[event.type](self, event)
        
    def HandleInit(self, event):
        self.InitializeTree()
    
    def HandleAdd(self, event):
        type_id = self.type_ids[event.obj_type]
        new_id = None
        
        if event.preceding == None:
            #node belongs at the beginning of the list of objects
            new_id = self.PrependItem(type_id, event.node.name)
        else:
            preceding_id = self.object_ids[event.preceding]
            obj_id = self.GetItemParent(preceding_id)
            new_id = self.InsertItem(type_id, preceding_id, event.node.name)

        #make sure we give the new object some PyData and add it to the
        # treeid hash for objects
        self.object_ids[event.node.name] = new_id
        self.SetPyData(new_id, event.node)
    
    def HandleRemove(self, event):
        obj_id = self.object_ids[event.name]
        self.Delete(obj_id)
    
    def HandleModify(self, event):
        pass
    
    def HandleHighlight(self, event):
        """\
        highlights the given objects in the tree
        objects is a hash with keys that are the object types
        and values of object names to highlight
        """
        #todo: error handling
        for obj_name in event.names:
            id = self.object_ids[obj_name]
            self.SetItemBackgroundColour(id, event.color)
    
    def HandleUnHighlight(self, event):
        for obj_name in event.names:
            id = self.object_ids[obj_name]
            self.SetItemBackgroundColour(id, 'WHITE')
    
    def HandleClear(self, event):
        """\
        clears all highlighting from objects in the tree
        """
        for name in self.odb.highlighted:
            id = self.object_ids[name]
            self.SetItemBackgroundColour(id, 'WHITE')
        for name in self.odb.emphasized:
            id = self.object_ids[name]
            self.SetItemTextColour(id, 'BLACK')
            self.SetItemBold(id, False)
        
    def HandleEmphasize(self, event):
        """\
        highlights the given objects in the tree
        objects is a hash with keys that are the object types
        and values of object names to highlight
        """
        #todo: error handling
        for obj_name in event.names:
            id = self.object_ids[obj_name]
            self.SetItemTextColour(id, 'BLUE')
            self.SetItemBold(id, True)
    
    def HandleUnEmphasize(self, event):
        for obj_name in event.names:
            id = self.object_ids[obj_name]
            self.SetItemTextColour(id, 'BLACK')
            self.SetItemBold(id, False)
        
    def HandleUnInit(self, event):
        pass
        
    def InitializeTree(self):
        self.type_ids = {}
        self.object_ids = {}
        for object_type in self.odb.getObjectTypes():
            self.type_ids[object_type] = self.AppendItem(self.root_id, object_type)
            self.SetPyData(self.type_ids[object_type], self.odb.getObjectModule(object_type))
            for node in self.odb.getObjectsOfType(object_type):
                object_name = node.name
                self.object_ids[object_name] = self.AppendItem(self.type_ids[object_type], object_name)
                self.SetPyData(self.object_ids[object_name], node)
        
        #we will blindly assume that there will always be some game object types included
        # else why would there be an editor for it, eh?
        #later we will save the last open object for a given project, but that's not now
        first_obj = self.type_ids[self.type_ids.keys()[0]]
        while  self.ItemHasChildren(first_obj):
            first_obj= self.GetFirstChild(first_obj)[0]
            
        self.SelectItem(first_obj)

    
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
                 ODBEvent.CLEAR_MARKERS: HandleClear,
                 ODBEvent.EMPHASIZE: HandleEmphasize,
                 ODBEvent.UNEMPHASIZE: HandleUnEmphasize,
                 ODBEvent.UNINIT: HandleUnInit}
