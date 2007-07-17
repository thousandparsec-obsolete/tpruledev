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
                 
        self.node = node
        self.name = name
        self.type = GetName()
                
        self.description = ""          

    def __str__(self):
        return "Category Game Object - " + self.name

def GetName():
    return 'Category'
