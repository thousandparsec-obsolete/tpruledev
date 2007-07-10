"""
Component.py
Representation of Components.
"""

import os
import xml.dom.minidom
from xml.dom.minidom import Node
import ObjectUtilities, RDE
from ObjectUtilities import getXMLString, getXMLNum
from gui import ComponentPanel
import game_objects.Category, game_objects.Property
    
class Object(ObjectUtilities.GameObject):
    #component_id = ObjectUtilities.sentinelProperty('component_id')
    #description = ObjectUtilities.sentinelProperty('description')
    #category_id = ObjectUtilities.sentinelProperty('category_id')
    #tpcl_requirements = ObjectUtilities.sentinelProperty('tpcl_requirements')
    #properties = ObjectUtilities.sentinelProperty('properties')
    
    def __init__(self, node, name, comp_id = -1,
                 desc = "", category = "",
                 tpcl_req = "", load_immediate = False):
                 
        self.node = node
        self.name = name
        self.filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Component', name + '.xml')
        
        if load_immediate:
            self.loadFromFile()
        else:
            self.properties = {}
            self.component_id = comp_id
            self.category = category
            self.name = name
            self.description = desc
            self.tpcl_requirements = tpcl_req

    def __str__(self):
        return "Component Game Object - " + self.name
            
    def loadFromFile(self):
        try:
            doc = xml.dom.minidom.parse(self.filename)
            #there should only be one property node...but even so
            root = doc.getElementsByTagName("component")[0]
            self.name = getXMLString(root, "name")
            self.component_id = getXMLNum(root, "component_id")
            self.category = getXMLString(root, "category")
            self.description = getXMLString(root, "description")
            self.tpcl_requirements = getXMLString(root, "tpcl_requirements")
            #now the properties associated with this component
            self.properties = {}
            for prop in root.getElementsByTagName("property"):
                self.properties[getXMLString(prop, "name")] = getXMLString(prop, "tpcl_cost")
        except IOError:
            #file does not exist - we are creating this property for the first time
            # fill with default values
            self.component_id = -1
            self.category = ""
            self.description = ""
            self.tpcl_requirements = ""
            self.properties = {}
            
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
                    

def saveObject(comp):
    """\
    Saves a Component to its persistence file.
    """  
    filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Component', comp.name + '.xml')
    import codegen.XmlComponent
    codegen.XmlComponent.GenerateCode(comp, filename)

def deleteSaveFile(name):
    """\
    Deletes the save file for a Component that has been deleted.
    """
    filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Component', name + '.xml')
    if os.path.exists(filename):
        os.remove(filename)
    else:
        #persistence file was never created
        pass

def GetName():
    return 'Component'
