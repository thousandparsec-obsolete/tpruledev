"""
Category.py
Representation of Categories.
"""

import os
import xml.dom.minidom
from xml.dom.minidom import Node
import ObjectUtilities, RDE
from ObjectUtilities import getXMLString, getXMLNum
from gui import CategoryPanel

class Object(ObjectUtilities.GameObject):

    def __init__(self, node, name, load_immediate = False):
                 
        self.node = node
        self.name = name
        self.type = GetName()
                
        self.description = ""
        
        if load_immediate:
            self.LoadObject()            

    def __str__(self):
        return "Category Game Object - " + self.name

def saveObject(cat):
    """\
    Saves a Component to its persistence file.
    """  
    filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Category', cat.name + '.xml')
    xml_module = __import__("codegen.Xml" + GetName(), globals(), locals(), [''])
    xml_module.GenerateCode(cat, filename)

def deleteSaveFile(name):
    """\
    Deletes the save file for a Component that has been deleted.
    """
    filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Category', name + '.xml')
    if os.path.exists(filename):
        os.remove(filename)
    else:
        #persistence file was never created
        pass

def GetName():
    return 'Category'
