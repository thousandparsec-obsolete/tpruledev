"""
Property.py
Representation of Properties.
"""

import os
import xml.dom.minidom
from xml.dom.minidom import Node
import ObjectUtilities, RDE
from gui import PropertyPanel
import game_objects.Category

DEFAULT_TPCL_DISPLAY = '(lambda (design) (cons #t \\"Default requires func\\"))'
DEFAULT_TPCL_REQUIRES = '(lambda (design bits) (cons 0 \\"0\\"))'
    
class Object(ObjectUtilities.GameObject):
    def __init__(self, node, name, category = "", prop_id = -1, rank = -1,
                 desc = '', disp_text = '', tpcl_disp = '', tpcl_req = '',
                 load_immediate=False):

        self.node = node
        self.name = name
        self.type = GetName()
        
        self.category = ""
        self.rank = ""
        self.description = ""
        self.display_text = ""
        self.tpcl_display = DEFAULT_TPCL_DISPLAY
        self.tpcl_requires = DEFAULT_TPCL_REQUIRES

                 
        if (load_immediate):
            self.LoadObject()

    def __str__(self):
        return "<Property Game Object - %s>" % self.name
            
    def OnObjectDeletion(self, object_type, object_name):
        if object_type == game_objects.Category.GetName() and \
                self.category == object_name:
            self.category = ""
            self.node.SetModified(True)
            
    def OnObjectRename(self, object_type, object_name, new_name):
        if object_type == game_objects.Category.GetName() and \
                self.category == object_name:
            self.category = new_name
            self.node.SetModified(True)  
    

def GetName():
    return 'Property'