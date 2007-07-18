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

import os
import ConfigParser, bisect
from ConfigParser import ConfigParser
import RDE, Nodes
from rde import ConfigManager
import game_objects.ObjectUtilities
from rde.Exceptions import *

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
    modified = []
    pending_modifications = False
    
    def __init__(self):
        #hash of object names
        self.objects = {}
        #hash of object modules
        self.object_modules = self.initObjectTypes()
        self.save_location = ConfigManager.config.get('Current Project', 'persistence_directory')
        self.odb_listeners = []
        return
        
    def initObjectTypes(self):
        #print "Trying to initialize object types"
        object_modules = {}
        for name in ConfigManager.config.get('Object Types', 'types').split(', '):
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
            if os.path.exists(object_dir) and os.listdir(object_dir) != []:
                self.objects[name] = [game_objects.ObjectUtilities.ObjectNode(self, partition(filename, '.')[0], module) for filename in os.listdir(object_dir)]
                self.objects[name].sort()
	    else:
		self.objects[name] = []
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
                    node.SaveObject()
                    
    def ValidateAllObjects(self):
        """\
        Loops through all objects and checks it for errors.
        """
        print "Validating project!"
        valid = True
        for type, module in self.object_modules.iteritems():
            for node in self.objects[type]:
                if node.GetObject().CheckForErrors():
                    valid = False
                node.ClearObject()
        return valid
                    
    def RenameObject(self, obj_type, name, new_name):
        if not self.ObjectExists(obj_type, name):
            raise NoSuchObjectError(name)
        
        #delete the object and remove it from the list
        print "Renaming %s to %s" % (name, new_name)
        obj_node = self.GetObjectNode(name, obj_type)
        print "\tnode: %s" % obj_node
        self.objects[obj_type].remove(name)
        obj_node.RenameNode(new_name)
        
        #now we have to call the OnObjectDeletion method of all other game objects
        for type, objects in self.objects.iteritems():
            for node in objects:
                node.GetObject().OnObjectRename(obj_type, name, new_name)
                node.ClearObject()
        #remove the reference to the old name
        self.sendODBEvent(ODBRemove(name))
        #add the same node with the new name
        self.Add(obj_type, new_name, obj_node)
        
                    
    def GenerateCode(self):
        """\
        Generates C++ code for the objects.
        """
        print "Generating code..."
        for type in self.getObjectTypes():
            generator = __import__("codegen.Cpp" + type, globals(), locals(), [''])
            print "Generating code for objects of type: %s" % type
            generator.GenerateCode(self)       

    def Add(self, obj_type, name, node=None):
        """\
        Adds an object to the database. Will create a new
        node if node is None, or will use the provided node
        otherwise.
        """
        print "Adding object %s, node: %s" % (name, node)
        #check for duplicate object
        # also raise error if no such object type
        if self.ObjectExists(obj_type, name):
            raise DuplicateObjectError(name)
                
        #find out where we need to put it and stick it in there
        idx = bisect.bisect(self.objects[obj_type], name)
        if not node:
            node = game_objects.ObjectUtilities.ObjectNode(self, name, self.object_modules[obj_type])
        self.objects[obj_type].insert(idx, node)
        
        #let our listeners know we added a new object and let them
        # know the parent in terms of alphabetical order
        if idx == 0:
            #if we're inserting at the start there is no preceding element
            self.sendODBEvent(ODBAdd(node, obj_type, None))
        else:
            self.sendODBEvent(ODBAdd(node, obj_type, self.objects[obj_type][idx-1].name))
            
        node.SetModified(True)
        self.MarkModified(node)

    def Remove(self, obj_type, name):
        if not self.ObjectExists(obj_type, name):
            raise NoSuchObjectError(name)
        
        #delete the object and remove it from the list
        self.GetObjectNode(name, obj_type).DeleteSaveFile()
        self.objects[obj_type].remove(name)
        
        #now we have to call the OnObjectDeletion method of all other game objects
        for type, objects in self.objects.iteritems():
            for node in objects:
                node.GetObject().OnObjectDeletion(obj_type, name)
                node.ClearObject()
                
        self.sendODBEvent(ODBRemove(name))
           
    def GetObjectNode(self, name, type=None):
        if type:
            for node in self.objects[type]:
                if node == name:
                    return node
        else:
            for nodelist in self.objects.values():
                for node in nodelist:
                    if node == name:
                        return node
        raise NoSuchObjectError
    
    def GetType(self, obj_name):
        """\
        Gets the type of the object with the given name
        """
        for type, objects in self.objects.iteritems():
            if obj_name in objects:
                return type
        raise NoSuchObjectError("Object %s doesn't exist." % obj_name)
    
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
            
    def MarkModified(self, obj_names):
        #todo: this can be so much more elegant
        if isinstance(obj_names, list):
            for name in obj_names:
                if not name in self.modified:
                    self.modified.append(name)
            self.sendODBEvent(ODBMarkModified(obj_names))
        else:
            if not obj_names in self.modified:
                self.modified.append(obj_names)
            self.sendODBEvent(ODBMarkModified([obj_names]))
        
    def UnmarkModified(self, obj_names):
        #todo: this can be so much more elegant
        if isinstance(obj_names, list):
            for name in obj_names:
                try:
                    self.modified.remove(name)
                except ValueError:
                    #don't care that it wasn't there
                    pass
            self.sendODBEvent(ODBUnmarkModified(obj_names))
        else:
            try:
                self.modified.remove(obj_names)
            except ValueError:
                #don't care that it wasn't there
                pass
            self.sendODBEvent(ODBUnmarkModified([obj_names]))
    
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
    MARKMODIFIED = 11
    UNMARKMODIFIED = 12

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
        
class ODBUninitialize(ODBEvent):
    type = ODBEvent.UNINIT
    
class ODBMarkModified(ODBEvent):
    type = ODBEvent.MARKMODIFIED
    
    def __init__(self, names):
        self.names = names
    
class ODBUnmarkModified(ODBEvent):
    type = ODBEvent.UNMARKMODIFIED
    
    def __init__(self, names):
        self.names = names
