"""
Game Object Utility classes and utility functions.
"""
import os
print os.getcwd()

import game_objects, RDE
import rde.Nodes
from rde import ConfigManager
    
class GameObject(object):
    """
    The base game object class. Handles all of the operations on
    the objects that require manipulation of the data that composes
    the object. We will load these as necessary and unload them
    when we no longer need them and there are no pending modifications.
    """
    
    def __init__(self, node, name):
        self.node = node
        self.name = name
        self.errors = {}
        
    def CopyConstructor(self, obj):
        """\
        Copy constructor. Copies all attributes from the object
        except those that we depend on in some way, like the
        node and the name.
        """
        for attr, value in obj.__dict__.iteritems():
            #copy everything except for the node and the name
            if attr != 'node' and attr != 'name':
                self.__setattr__(attr, value)
        
    def OnObjectDeletion(self, object_type, object_name):
        """\
        Removes any associations that the object has with the given
        object that is being deleted. Since we can delete only the object
        that is currently selected and the deletion process occurs
        before a new object is selected we don't have to worry about
        updating the current edit panel view. Yet.
        """
        pass
        
    def OnObjectRename(self, object_type, object_name, new_name):
        """\
        Adjusts any associations that the object has with the given
        object that is being renamed. Since we can rename only the object
        that is currently selected and the renaming process occurs
        before a new object is selected we don't have to worry about
        updating the current edit panel view. Yet.
        """
        pass
        
    def CheckForErrors(self):
        """\
        Checks the object for errors and modifies the node based
        on its findings.
        
        Returns True or False depending on its findings.
        """
        return False
        

class ObjectNode(rde.Nodes.DatabaseNode):
    """
    Class for keeping track of the state of a
    game object. Tracks such things as whether
    the object has been modified or not. Can
    have listeners added to it to be modified
    of changes to the game object.
    """
    
    ###########################################################
    #Comparison functions, this way we can wrap our 
    # objects in nodes and still use them fairly transparently
    ############################################################
    def __lt__(self, other):
        if isinstance(other, (ObjectNode, str)):
            return self.name.__lt__(other.__str__())
        else:
            return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, (ObjectNode, str)):
            return self.name.__le__(other.__str__())
        else:
            return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, (ObjectNode, str)):
            return self.name.__gt__(other.__str__())
        else:
            return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, (ObjectNode, str)):
            return self.name.__ge__(other.__str__())
        else:
            return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, (ObjectNode, str)):
            return self.name.__eq__(other.__str__())
        else:
            return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, (ObjectNode, str)):
            return self.name.__ne__(other.__str__())
        else:
            return NotImplemented
    
    def __cmp__(self, other):
        if isinstance(other, (ObjectNode, str)):
            if (self.name.__lt__(other.__str__())):
                return -1
            elif (self.name.__gt__(other.__str__())):
                return 1
            else:
                return 0
        else:
            return NotImplemented
    
    #so that we can hash these when necessary
    def __hash__(self):
        return self.name.__hash__()
    
    ####################
    #String function for easy representation and comparison
    ####################
    def __str__(self):
        return self.name
    
    name=""
    visible=False #if we're being used we're visible - so don't delete our object!
    modified=False #if we're modified don't delete our object!
    renamed=False #if we're renamed we need to handle some special cases on saves and deletes
    contains_error=False #if we've got an error we can't generate code
    highlighted=False
    highlight_color=""
    listeners=[]
    object_module=None
    object_database=None
    object=None
    
    def __init__(self, odb, name, module):
        self.name = name
        self.object_module = module
        self.type = module.GetName()
        self.object_database = odb
        self.__error = False
        
    def CopyObject(self, object):
        self.object = self.object_module.Object(self, self.name, object)
        
    def SetModified(self, b):
        #If we're changing the modified state then we need
        # to alert the object manager to this change so
        # that we can be marked accordingly
        if b and not self.modified:
            self.object_database.pending_modifications = True
            self.object_database.MarkModified(self.name)
        elif not b and self.modified:
            self.object_database.UnmarkModified(self.name)
        self.modified = b
    
    def addListener(self, listener):
        """
        Adds an object as a listener for this game
        object, to be notified of certain significant
        changes to the object.
        """
        if self.listeners.count(listener) == 0:
            self.listeners.append(listener)
    
    def removeListener(self, listener):
        """
        Removes a listener.
        """
        if self.listeners.count(listener) != 0:
            self.listeners.remove(listener)
        
    def notifyListeners(self, event):
        """
        Notify all listeners of an event
        """
        for l in self.listeners:
            l.handleObjectEvent(event)
            
    def GetObject(self):
        """
        Gets the game object object associated with this
        node.
        
        If obj is not None then we will copy the object
        represented by obj into this object.
        """
        if not self.object:
            self.object = self.object_module.Object(self, self.name)
            self.FillObject(self.object)
            
        return self.object
        
    def ClearObject(self):
        """
        Clears a loaded game object if no modifications have been
        made
        """
        print "Clearing ", self.name
        if not self.modified and not self.visible and not self.has_errors and self.object:
            del self.object
            
    def RenameNode(self, new_name):
        if not self.renamed:
            self.old_name = self.name
            self.renamed = True
        if self.object:
            self.object.name = new_name
        self.SetModified(True)
        self.name = new_name
        
    def SaveObject(self):
        """\
        Saves an object to its persistence file.
        
        If we were renamed then we also need to delete our old
        persistence file.
        """
        
        #check if we renamed
        if self.renamed:
            #if we renamed then we need to delete our old file name
            self.DeleteSaveFile(self.old_filename)

        #need some error checking here to check for non-existent codegen modules
        if self.modified:
            xml_module = __import__("codegen.Xml" + self.type, globals(), locals(), [''])
            xml_module.GenerateCode(self.GetObject(), self.filename)
            self.renamed = False
            self.old_name = None
            self.SetModified(False)
            self.ClearObject()
        
    def FillObject(self, object):
        """\
        Fills an object with the data from its persistence file
        """  

        #need some error checking here to check for non-existent codegen modules
        if os.path.exists(self.filename):
            xml_module = __import__("codegen.Xml" + self.type, globals(), locals(), [''])
            xml_module.ParseCode(object, self.filename)
        else:
            #no save file created yet, we're fine with defaults
            pass
            
    def DeleteSaveFile(self, fname=None):
        """\
        Deletes an objects XML save file
        """
        
        #default to the filename based on the current name
        if not fname:
            fname = self.filename
        if os.path.exists(fname):
            os.remove(fname)
        else:
            #no file in existence, guess we just created
            # this object and never saved it, no biggie
            pass
            
    def GetError(self):
        return self.__error
        
    def SetError(self, b):
        """\
        Marks this object as having an error - highlights it in red.
        """
        if b and not self.__error:
            #we're setting there error where there was none before
            # highlight ourselves in red!
            self.__error = b
            self.object_database.Highlight(self.name, "RED")
        elif not b and self.__error:
            #we're clearing an existing error
            self.__error = b
            self.object_database.UnHighlight(self.name)
            
    has_errors = property(GetError, SetError)
        
    def GetFilename(self):
        return os.path.join(ConfigManager.config.get('Current Project', 'persistence_directory'),
                                self.type, self.name + '.xml')    
    filename = property(GetFilename)
    
    def GetOldFilename(self):
        return os.path.join(ConfigManager.config.get('Current Project', 'persistence_directory'),
                                self.type, self.old_name + '.xml')    
    old_filename = property(GetOldFilename)
    