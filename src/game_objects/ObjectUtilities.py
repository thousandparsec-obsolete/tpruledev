"""
Game Object Utility classes and utility functions.
"""

def makeSentinelGetter(var_name):
    def getter(self):
        return self.__getattribute__('__' + var_name)
    return getter
    
def makeSentinelSetter(var_name, node):
    def setter(self, value):
        node.modified = True
        self.__setattr__('__' + var_name, value)
    return setter
    
def sentinelProperty(var_name, node):
    return property(makeSentinelGetter(var_name), makeSentinelSetter(var_name, node))

class ObjectNode(object):
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
    object=None
    
    def __init__(self, object_module, name):
        self.name = name
        self.object_module = object_module    
        
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
        if not object:
            self.object = self.object_module.Object(
            
        return self.object
        
    def clearObject(self):
        """
        Clears a loaded game object if no modifications have been
        made
        """
        if not modified:
            del self.object