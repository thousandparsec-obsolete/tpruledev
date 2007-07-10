"""
Game Object Utility classes and utility functions.
"""
import os
print os.getcwd()

import game_objects, RDE
import rde.Nodes
    
class GameObject(object):
    """
    The base game object class. Defines a few variables
    that are necessary for every game object such as the
    ObjectNode which contains this GameObject and the
    name property.
    """    
    def __init__(self, node):
        self.node = node
        
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
        
    def SaveObject(self):
        """\
        Saves an object to its persistence file.
        """  

        #need some error checking here to check for non-existent codegen modules
        xml_module = __import__("codegen.Xml" + self.type, globals(), locals(), [''])
        xml_module.GenerateCode(self, self.filename)
        
    def LoadObject(self):
        """\
        Loads an object from its persistence file
        """  

        #need some error checking here to check for non-existent codegen modules
        if os.path.exists(self.filename):
            xml_module = __import__("codegen.Xml" + self.type, globals(), locals(), [''])
            xml_module.ParseCode(self, self.filename)
        else:
            #no save file created yet, we're fine with defaults
            pass
            
    def DeleteSaveFile(self):
        """\
        Deletes an objects XML save file
        """
        if os.path.exists(self.filename):
            os.remove(self.filename)
        else:
            #no file in existence, guess we just created
            # this object and never saved it, no biggie
            pass
        
    def GetFilename(self):
        return os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                self.type, self.name + '.xml')
    
    filename = property(GetFilename)
        

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
    modified=False
    highlighted=False
    highlight_color=""
    listeners=[]
    object_module=None
    object_database=None
    object=None
    visible=False
    
    def __init__(self, odb, name, module):
        self.name = name
        self.object_module = module
        self.object_database = odb
        
    def SetModified(self, b):
        self.modified = b
        if b:
            self.object_database.pending_modifications = True
            self.object_database.Highlight(self.name, "RED")
        else:
            self.object_database.UnHighlight(self.name)
    
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
            
    def getObject(self, load_imm=True):
        """
        Gets the game object object associated with this
        node.
        """
        if not self.object:
            self.object = self.object_module.Object(self, self.name, load_immediate = load_imm)
            
        return self.object
        
    def clearObject(self):
        """
        Clears a loaded game object if no modifications have been
        made
        """
        print "Clearing ", self.name
        if not self.modified and not self.visible and self.object:
            del self.object
