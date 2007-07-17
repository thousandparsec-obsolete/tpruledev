"""
Category.py
Representation of Categories.
"""

import os
import xml.dom.minidom
from xml.dom.minidom import Node
import ObjectUtilities, RDE
from gui import CategoryPanel

class Object(ObjectUtilities.GameObject):

    def __init__(self, node, name):
        ObjectUtilities.GameObject.__init__(self, node, name)
        self.type = GetName()
                
        self.description = ""          

    def __str__(self):
        return "Category Game Object - " + self.name
        
    def CheckForErrors(self):
        if self.description == "":
            self.errors[self.description] = "Description needs to be non-null!"
            self.node.has_errors = True
            return True
        return False

def GetName():
    return 'Category'
