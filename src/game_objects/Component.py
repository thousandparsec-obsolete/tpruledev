"""
Component.py
Representation of Components.
"""

import os
import xml.dom.minidom
from xml.dom.minidom import Node
import ObjectUtilities, RDE
from gui import ComponentPanel
import game_objects.Category, game_objects.Property

DEFAULT_TPCL_REQUIREMENTS = '(lambda (design) (cons #f \\"Default req func\\"))'
    
class Object(ObjectUtilities.GameObject):        

    def __init__(self, node, name):                 
        self.node = node
        self.name = name
        self.type = GetName()
        
        self.properties = {}
        self.category = ""
        self.description = ""
        self.tpcl_requirements = DEFAULT_TPCL_REQUIREMENTS       

    def __str__(self):
        return "Component Game Object - " + self.name
            
    def OnObjectDeletion(self, object_type, object_name):
        if object_type == game_objects.Property.GetName():
            try:
                self.properties.pop(object_name)
                self.node.SetModified(True)
            except KeyError:
                #we weren't associated with that property, that's fine
                pass
        elif object_type == game_objects.Category.GetName():
            if self.category == object_name:
                self.category = ""
                self.node.SetModified(True)
                
    def OnObjectRename(self, object_type, object_name, new_name):
        if object_type == game_objects.Property.GetName():
            try:
                self.properties[new_name] = self.properties.pop(object_name)
                self.node.SetModified(True)
            except KeyError:
                #we weren't associated with that property, that's fine
                pass
        elif object_type == game_objects.Category.GetName():
            if self.category == object_name:
                self.category = new_name
                self.node.SetModified(True)

def GetName():
    return 'Component'
