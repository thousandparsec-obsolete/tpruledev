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
import tpcl

DEFAULT_TPCL_DISPLAY = '(lambda (design) (cons #t \\"Default requires func\\"))'
DEFAULT_TPCL_REQUIRES = '(lambda (design bits) (cons 0 \\"0\\"))'
    
class Object(ObjectUtilities.GameObject):
    def __init__(self, node, name):
        ObjectUtilities.GameObject.__init__(self, node, name)
        self.type = GetName()
        
        self.category = ""
        self.rank = ""
        self.description = ""
        self.display_text = ""
        self.tpcl_display = DEFAULT_TPCL_DISPLAY
        self.tpcl_requires = DEFAULT_TPCL_REQUIRES

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
            
    def CheckForErrors(self):
        self.errors = {}
        err = False
        if self.description == "":
            self.errors['description'] = "Description needs to be non-null!"
            err = True
        if self.category == "":
            self.errors['category'] = "A category must be selected"
            err = True
        #todo: check for positive integer rank!
        if self.rank == "":
            self.errors['rank'] = "A rank must be assigned"
            err = True
        if self.display_text == "":
            self.errors['display_text'] = "Display text must be non-null"
            err = True
        
        #check the tpcl display function
        if not tpcl.TpclSyntaxIsValid(self.tpcl_display):
            self.errors['tpcl_display'] = "Syntax error"
            err = True
            
        #check the tpcl requires function
        if not tpcl.TpclSyntaxIsValid(self.tpcl_requires):
            self.errors['tpcl_requires'] = "Syntax error"
            err = True
        
        self.node.has_errors = err
        if err:
            print "Errors in Property " + self.name
            for attr, error in self.errors.iteritems():
                print "\t%s - %s" % (attr, error)
        return err
            

def GetName():
    return 'Property'