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
    
class Object(ObjectUtilities.GameObject):

    def __init__(self, node, name, category = "", prop_id = -1, rank = -1,
                 desc = '', disp_text = '', tpcl_disp = '', tpcl_req = '',
                 load_immediate=False):

        self.node = node
        self.name = name
        self.filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Property', name + '.xml')
                 
        if (load_immediate):
            self.loadFromFile()
        else:
            self.category = category
            self.property_id = prop_id
            self.rank = rank
            self.description = desc
            self.display_text = disp_text
            self.tpcl_display = tpcl_disp
            self.tpcl_requires = tpcl_req
        
        if self.node != None:
            self.node.modified = False

    def __str__(self):
        return "<Property Game Object - %s>" % self.name
    
    def loadFromFile(self):
        try:
            doc = xml.dom.minidom.parse(self.filename)
            #there should only be one property node...but even so
            root = doc.getElementsByTagName("property")[0]
            self.name = getXMLString(root, "name")
            self.rank = getXMLNum(root, "rank")
            self.category = getXMLString(root, "category")
            self.description = getXMLString(root, "description")
            self.display_text = getXMLString(root, "display_text")
            self.tpcl_display = getXMLString(root, "tpcl_display")
            self.tpcl_requires = getXMLString(root, "tpcl_requires")
        except IOError:
            #file does not exist
            # fill with default values
            self.rank = -1
            self.property_id = -1
            self.category = ""
            self.description = ""
            self.display_text = ""
            self.tpcl_display = ""
            self.tpcl_requires = ""
        

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