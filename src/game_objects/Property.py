"""
Property.py
Representation of Properties.
"""

import os
import os.path
import wx
import xml.dom.minidom
from xml.dom.minidom import Node
import ObjectUtilities, RDE
from ObjectUtilities import getXMLString, getXMLNum
import PropertyPanel

def generateEditPanel(parent):
    print "Generating panel for Property module."
    panel = wx.Panel(parent, wx.ID_ANY)
    panel.SetBackgroundColour('white')
    label = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_MULTILINE)
    label.SetValue( "Property Objects\n"
                    "------------------------\n"
                    "Insert a nice little blurb about Properties here...\n")
    label.SetEditable(False)
    border1 = wx.BoxSizer(wx.HORIZONTAL)
    border1.Add(label, 1, wx.ALL | wx.EXPAND)
    border2 = wx.BoxSizer(wx.VERTICAL)
    border2.Add(border1, 1, wx.ALL | wx.EXPAND)
    panel.SetSizer(border2)
    return panel
    

def compareFunction(prop1, prop2):
    id1 = int(prop1.property_id)
    id2 = int(prop2.property_id)
    if id1 < id2:
        return -1
    if id1 == id2:
        return 0
    return 1
    

class Object(ObjectUtilities.GameObject):
    property_id = ObjectUtilities.sentinelProperty('property_id')
    category_id = ObjectUtilities.sentinelProperty('category_id')
    rank = ObjectUtilities.sentinelProperty('rank')
    description = ObjectUtilities.sentinelProperty('description')
    display_text = ObjectUtilities.sentinelProperty('display_text')
    tpcl_display = ObjectUtilities.sentinelProperty('tpcl_display')
    tpcl_requires = ObjectUtilities.sentinelProperty('tpcl_requires')

    def __init__(self, node, name, catid = -1, prop_id = -1, rank = -1,
                 desc = 'Null', disp_text = 'Null', tpcl_disp = 'Null', tpcl_req = 'Null',
                 load_immediate=False):

        self.node = node
        self.name = name
        self.filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Property', name + '.xml')
                 
        if (load_immediate):
            self.loadFromFile()
        else:
            self.category_id = catid
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
            self.property_id = getXMLNum(root, "property_id")
            self.category_id = getXMLNum(root, "category_id")
            self.description = getXMLString(root, "description")
            self.display_text = getXMLString(root, "display_text")
            self.tpcl_display = getXMLString(root, "tpcl_display")
            self.tpcl_requires = getXMLString(root, "tpcl_requires")
        except IOError:
            #file does not exist
            # fill with default values
            self.rank = -1
            self.property_id = -1
            self.category_id = -1
            self.description = ""
            self.display_text = ""
            self.tpcl_display = ""
            self.tpcl_requires = ""
        
    def generateEditPanel(self, parent):
        #make the panel
        return PropertyPanel.Panel(self, parent)    
        

def saveObject(prop):
    """\
    Saves a Property to its persistence file.
    """
    filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Property', prop.name + '.xml')
    ofile = open(filename, 'w')
    ofile.write('<property>\n')
    ofile.write('    <name>' + prop.name + '</name>\n')
    ofile.write('    <property_id>' + str(prop.property_id) + '</property_id>\n')
    ofile.write('    <category_id>' + str(prop.category_id) + '</category_id>\n')
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
    

def getName():
    return 'Property'
    
import re
def GenerateCode(object_database):
    """\
    Generates C++ code for use with tpserver-cpp
    Code is placed in the .../ProjectName/code/ directory.
    """
    
    print "BEGINNING CODE GENERATION FOR PROPERTIES!"
    outdir = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'project_directory'),
                                               'code', getName())
    if not os.path.exists(outdir):
        os.makedirs(outdir)
                                               
    #we make two files, a header and a cpp file
    hfile_path = os.path.join(outdir, "propertyfactory.h")
    cfile_path = os.path.join(outdir, "propertyfactory.cpp")

    HFILE = open(hfile_path, 'w')
    CFILE = open(cfile_path, 'w')
    
    h_header = \
"""\
#ifndef PROPFAC_H
#define PROPFAC_H

class PropertyFactory {
 public:
  PropertyFactory();
  
  void initProperties();
  
 private:
"""
    HFILE.write(h_header)
    HFILE.flush()
    
    cpp_header = \
"""\
#include <tpserver/game.h>
#include <tpserver/designstore.h>
#include <tpserver/property.h>

#include <propertyfactory.h>

PropertyFactory::PropertyFactory(){

}

"""
    CFILE.write(cpp_header)
    CFILE.flush()

    func_calls =[]
    
    #generate the code
    for prop_node in object_database.getObjectsOfType(getName()):
        prop = prop_node.getObject()
        func_name = "init%sProp()" % prop.name.replace('-', '')
        func_calls.append("%s;" % func_name)
        
        #write to header file
        HFILE.write("  void %s;\n" % func_name)
        HFILE.flush()
        
        #write to cpp file
        #regex to handle newline stuffs...we write the TPCL code on one line
        regex = re.compile('\s*\r?\n\s*')
        CFILE.write("void PropertyFactory::%s {\n" % func_name)
        CFILE.write("  Property* prop = new Property();\n")
        CFILE.write("  DesignStore *ds = Game::getGame()->getDesignStore();\n")
        CFILE.write("\n")
        CFILE.write("  prop->setCategoryId(%s);\n" % prop.category_id)
        CFILE.write("  prop->setRank(%s);\n" % prop.rank)
        CFILE.write('  prop->setName("%s");\n' % prop.name)
        CFILE.write('  prop->setDisplayName("%s");\n' % prop.display_text)
        CFILE.write('  prop->setDescription("%s");\n' % prop.description)
        CFILE.write('  prop->setTpclDisplayFunction("%s");\n' % \
                        " ".join(regex.split(prop.tpcl_display)))
        CFILE.write('  prop->setTpclRequirementsFunction("%s");\n' % \
                        " ".join(regex.split(prop.tpcl_requires)))
        CFILE.write('  ds->addProperty(prop);\n')
        CFILE.write('  return;\n')
        CFILE.write('}\n\n')
        CFILE.flush()
        prop_node.clearObject()
    
    HFILE.write('};\n#endif\n')
    HFILE.flush()
    
    #finish up by adding the initProperties function
    CFILE.write('void PropertyFactory::initProperties() {\n')
    for call in func_calls:
        CFILE.write("  %s\n" % call)
    CFILE.write('  return;\n}\n')
    CFILE.flush()
    
    CFILE.close()
    HFILE.close()
    
    print "ALL DONE GENERATING CODE FOR PROPERTIES!"