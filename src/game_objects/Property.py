"""
Property.py
Representation of Properties.
"""

import os
import xml.dom.minidom
from xml.dom.minidom import Node
import ObjectUtilities, RDE
from ObjectUtilities import getXMLString, getXMLNum
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
        

def saveObject(prop):
    """\
    Saves a Property to its persistence file.
    """
    filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Property', prop.name + '.xml')
    ofile = open(filename, 'w')
    ofile.write('<property>\n')
    ofile.write('    <name>' + prop.name + '</name>\n')
    ofile.write('    <category>' + prop.category + '</category>\n')
    ofile.write('    <rank>' + str(prop.rank) + '</rank>\n')
    ofile.write('    <display_text>' + prop.display_text + '</display_text>\n')
    ofile.write('    <description>' + prop.description + '</description>\n')
    ofile.write('    <tpcl_display><![CDATA[' + prop.tpcl_display + ']]></tpcl_display>\n')
    ofile.write('    <tpcl_requires><![CDATA[' + prop.tpcl_requires + ']]></tpcl_requires>\n')
    ofile.write('</property>\n')	
    ofile.flush()
    ofile.close()
  
    
def deleteSaveFile(name):
    """\
    Deletes the save file for a Component that has been deleted.
    """
    filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Property', name + '.xml')
    if os.path.exists(filename):
        os.remove(filename)
    else:
        #no persistence file has yet been created
        pass
    

def GetName():
    return 'Property'