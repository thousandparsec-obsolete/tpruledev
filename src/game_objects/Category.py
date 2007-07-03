"""
Category.py
Representation of Categories.
"""

import os, wx
import xml.dom.minidom
from xml.dom.minidom import Node
import ObjectUtilities, RDE
from ObjectUtilities import getXMLString, getXMLNum
from gui import CategoryPanel

def generateEditPanel(parent):
    print "Generating panel for Category module."
    panel = wx.Panel(parent, wx.ID_ANY)
    panel.SetBackgroundColour('white')
    label = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_MULTILINE)
    label.SetValue( "Category Objects\n"
                    "------------------------\n"
                    "Insert a nice little blurb about Categories here...\n")
    label.SetEditable(False)
    border1 = wx.BoxSizer(wx.HORIZONTAL)
    border1.Add(label, 1, wx.ALL | wx.EXPAND)
    border2 = wx.BoxSizer(wx.VERTICAL)
    border2.Add(border1, 1, wx.ALL | wx.EXPAND)
    panel.SetSizer(border2)
    return panel

class Object(ObjectUtilities.GameObject):

    def __init__(self, node, name, desc = "Null", load_immediate = False):
                 
        self.node = node
        self.name = name
        self.filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Category', name + '.xml')
        
        if load_immediate:
            self.loadFromFile()
        else:
            self.description = desc

    def __str__(self):
        return "Category Game Object - " + self.name
            
    def loadFromFile(self):
        try:
            doc = xml.dom.minidom.parse(self.filename)
            #there should only be one property node...but even so
            root = doc.getElementsByTagName("category")[0]
            self.name = getXMLString(root, "name")
            self.description = getXMLString(root, "description")
        except IOError:
            #file does not exist - we are creating this property for the first time
            # fill with default values
            self.description = ""
    
    def generateEditPanel(self, parent):
        #make the panel
        return CategoryPanel.Panel(self, parent)

def saveObject(cat):
    """\
    Saves a Component to its persistence file.
    """  
    filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Category', cat.name + '.xml')
    ofile = open(filename, 'w')
    ofile.write('<category>\n')
    ofile.write('    <name>' + cat.name + '</name>\n')
    ofile.write('    <description>' + cat.description + '</description>\n')
    ofile.write('</category>\n')
    ofile.flush()
    ofile.close()

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

def getName():
    return 'Category'


import re
def GenerateCode(object_database):
    """\
    Generates C++ code for use with tpserver-cpp
    Code is placed in the .../ProjectName/code/ directory.
    """
    
    NAME = getName()
    FILENAME = NAME.lower() + "factory"
    CLASS_NAME = NAME + "Factory"
    INIT_FUNC_NAME = "init%sObjects" % NAME
    
    print "BEGINNING CODE GENERATION FOR CATEGORIES!"
    outdir = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'project_directory'), 'code')
    if not os.path.exists(outdir):
        os.makedirs(outdir)
                                               
    #we make two files, a header and a cpp file
    hfile_path = os.path.join(outdir, "%s.h" % FILENAME)
    cfile_path = os.path.join(outdir, "%s.cpp" % FILENAME)

    HFILE = open(hfile_path, 'w')
    CFILE = open(cfile_path, 'w')
    
    
    
    h_header = \
"""\
#ifndef CATEFAC_H
#define CATEFAC_H

class %s {
 public:
  %s();
  
  void %s();
  
 private:
""" % (CLASS_NAME, CLASS_NAME, INIT_FUNC_NAME)

    HFILE.write(h_header)
    HFILE.flush()
    
    cpp_header = \
"""\
#include <tpserver/game.h>
#include <tpserver/designstore.h>
#include <tpserver/category.h>

#include <%s.h>

%s::%s(){

}

""" % (FILENAME , CLASS_NAME, CLASS_NAME)
    CFILE.write(cpp_header)
    CFILE.flush()

    func_calls =[]
    
    #generate the code
    for cat_node in object_database.getObjectsOfType(NAME):
        cat = cat_node.getObject()
        func_name = "init%s%s()" % (cat.name.replace('-', ''), NAME)
        func_calls.append("%s;" % func_name)
        
        #write to header file
        HFILE.write("  void %s;\n" % func_name)
        HFILE.flush()
        
        #write to cpp file
        #regex to handle newline stuffs...we write the TPCL code on one line
        regex = re.compile('\s*\r?\n\s*')
        CFILE.write("void %s::%s {\n" % (CLASS_NAME, func_name))
        CFILE.write("  Category* cat = new Category();\n")
        CFILE.write("  DesignStore *ds = Game::getGame()->getDesignStore();\n")
        CFILE.write("\n")        
        CFILE.write('  cat->setName("%s");\n' % cat.name)
        CFILE.write('  cat->setDescription("%s");\n' % cat.description)
        CFILE.write('  ds->addCategory(cat);\n')
        CFILE.write('  return;\n')
        CFILE.write('}\n\n')
        CFILE.flush()
        cat_node.clearObject()
    
    HFILE.write('};\n#endif\n')
    HFILE.flush()
    
    #finish up by adding the initProperties function
    CFILE.write('void %s::%s() {\n' % (CLASS_NAME, INIT_FUNC_NAME))
    for call in func_calls:
        CFILE.write("  %s\n" % call)
    CFILE.write('  return;\n}\n')
    CFILE.flush()
    
    CFILE.close()
    HFILE.close()
    
    print "ALL DONE GENERATING CODE FOR CATEGORIES!"