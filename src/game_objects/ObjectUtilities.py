"""
Game Object Utility classes and utility functions.
"""
import os
print os.getcwd()

import game_objects
import core.Nodes

def makeSentinelGetter(var_name):
    def getter(self):
        return self.__getattribute__('__' + var_name)
    return getter
    
def makeSentinelSetter(var_name):
    def setter(self, value):
        self.node.markModified()
        self.__setattr__('__' + var_name, value)
    return setter
    
def sentinelProperty(var_name):
    return property(makeSentinelGetter(var_name), makeSentinelSetter(var_name))
    
class GameObject(object):
    """
    The base game object class. Defines a few variables
    that are necessary for every game object such as the
    ObjectNode which contains this GameObject and the
    name property.
    """
    name = sentinelProperty('name')
    
    def __init__(self, node):
        self.node = node

class ObjectNode(core.Nodes.DatabaseNode):
    """
    Class for keeping track of the state of a
    game object. Tracks such things as whether
    the object has been modified or not. Can
    have listeners added to it to be modified
    of changes to the game object.
    """
    
    name=""
    modified=False
    highlighted=False
    highlight_color=""
    listeners=[]
    object_module=None
    object_database=None
    object=None
    
    def __init__(self, odb, name, module):
        self.name = name
        self.object_module = module
        self.object_database = odb
        
    def __str__(self):
        return self.name  
        
    def markModified(self):
        modified = True
        
    def clearModified(self):
        modified = False
    
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
            
    def getObject(self):
        """
        Gets the game object object associated with this
        node.
        """
        if not self.object:
            self.object = self.object_module.Object(self, self.name, load_immediate=True)
            
        return self.object
        
    def clearObject(self):
        """
        Clears a loaded game object if no modifications have been
        made
        """
        if not self.modified:
            del self.object
            
    def generateEditPanel(self, parent):
            return self.getObject().generateEditPanel(parent)