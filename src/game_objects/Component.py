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
import tpcl, tpcl.ComponentTpcl

DEFAULT_TPCL_REQUIREMENTS = '(lambda (design) (cons #f "Default req func"))'
    
class Object(ObjectUtilities.GameObject):        

    def __init__(self, node, name, comp=None):                 
        ObjectUtilities.GameObject.__init__(self, node, name)
        self.type = GetName()
        
        if comp:
            ObjectUtilities.GameObject.CopyConstructor(self, comp)
        else:
            self.properties = {}
            self.categories = []
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
            try:
                self.categories.remove(object_name)
                self.node.SetModified(True)
            except:
                #we weren't in that category, no biggie
                pass
                
    def CheckForErrors(self):
        self.errors = {}
        err = False
        if self.description == "":
            self.errors['description'] = "Description needs to be non-null!"
            err = True
        if self.categories == []:
            self.errors['categories'] = "A category must be selected"
            err = True
        
        #check the tpcl requirements function
        if not tpcl.ComponentTpcl.TpclCodeIsValid(self):
            err = True
                
        #eventually we will want to check the TPCL Cost functions
        # for each associated property
        #for propname, tpcl_cost in self.properties:
        
        self.node.has_errors = err
        if err:
            print "Errors in Component " + self.name
            for attr, error in self.errors.iteritems():
                print "\t%s - %s" % (attr, error)
        return err

def GetName():
    return 'Component'
