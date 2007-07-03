"""
Component.py
Representation of Components.
"""

import os, wx
import xml.dom.minidom
from xml.dom.minidom import Node
import ObjectUtilities, RDE
from ObjectUtilities import getXMLString, getXMLNum
from gui import ComponentPanel

def generateEditPanel(parent):
    print "Generating panel for Component module."
    panel = wx.Panel(parent, wx.ID_ANY)
    panel.SetBackgroundColour('white')
    label = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_MULTILINE)
    label.SetValue( "Component Objects\n"
                    "------------------------\n"
                    "Insert a nice little blurb about Components here...\n")
    label.SetEditable(False)
    border1 = wx.BoxSizer(wx.HORIZONTAL)
    border1.Add(label, 1, wx.ALL | wx.EXPAND)
    border2 = wx.BoxSizer(wx.VERTICAL)
    border2.Add(border1, 1, wx.ALL | wx.EXPAND)
    panel.SetSizer(border2)
    return panel
    
edit_panel = None
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
    
    def generateEditPanel(self, parent):
        #make the panel
        global edit_panel
        if not edit_panel:
            edit_panel = ComponentPanel.Panel(parent)
        return edit_panel.LoadObject(self)
        
    def deleteEditPanel(self):
        #we keep our edit panel around
        global edit_panel
        edit_panel.Hide()

def saveObject(comp):
    """\
    Saves a Component to its persistence file.
    """  
    filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Component', comp.name + '.xml')
    ofile = open(filename, 'w')
    ofile.write('<component>\n')
    ofile.write('    <name>' + comp.name + '</name>\n')
    ofile.write('    <category>' + comp.category + '</category>\n')
    ofile.write('    <description>' + comp.description + '</description>\n')
    ofile.write('    <tpcl_requirements><![CDATA[' + comp.tpcl_requirements + ']]></tpcl_requirements>\n')
    ofile.write('\n')
    ofile.write('    <!--propertylist:-->\n')
    for prop, cost_func in comp.properties.iteritems():
        ofile.write('    <property>\n')
        ofile.write('        <name>' + prop + '</name>\n')
        ofile.write('        <tpcl_cost><![CDATA[' + cost_func + ']]></tpcl_cost>\n')
        ofile.write('    </property>\n')
    ofile.write('</component>\n')
    ofile.flush()
    ofile.close()

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

def getName():
    return 'Component'


import re
def GenerateCode(object_database):
    """\
    Generates C++ code for use with tpserver-cpp
    Code is placed in the .../ProjectName/code/Component directory.
    """
    
    NAME = getName()
    FILENAME = NAME.lower() + "factory"
    CLASS_NAME = NAME + "Factory"
    INIT_FUNC_NAME = "init%sObjects" % NAME
    
    print "BEGINNING CODE GENERATION FOR PROPERTIES!"
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
#ifndef COMPFAC_H
#define COMPFAC_H

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
#include <tpserver/component.h>

#include <%s.h>

%s::%s(){

}

""" % (FILENAME, CLASS_NAME, CLASS_NAME)

    CFILE.write(cpp_header)
    CFILE.flush()

    func_calls =[]
    
    #generate the code
    for comp_node in object_database.getObjectsOfType(NAME):
        comp = comp_node.getObject()
        func_name = "init%s%s()" % (comp.name.replace('-', ''), NAME)
        func_calls.append("%s;" % func_name)
        
        #write to header file
        HFILE.write("  void %s;\n" % func_name)
        HFILE.flush()
        
        #write to cpp file
        #regex to handle newline stuffs...we write the TPCL code on one line
        regex = re.compile('\s*\r?\n\s*')
        CFILE.write('void %s::%s {\n' % (CLASS_NAME, func_name))
        CFILE.write('  std::map<unsigned int, std::string> propertylist;\n')
        CFILE.write('  DesignStore *ds = Game::getGame()->getDesignStore();\n');
        CFILE.write('  Component* comp = new Component();\n');
        CFILE.write('\n')
        CFILE.write('  comp->setCategoryId(ds->getCategoryByName("%s"));\n' % comp.category)
        CFILE.write('  comp->setName("%s");\n' % comp.name)
        CFILE.write('  comp->setDescription("%s");\n' % comp.description)
        CFILE.write('  comp->setTpclRequirementsFunction("%s");\n' % \
                        " ".join(regex.split(comp.tpcl_requirements)))
        #now the properties...
        for name, cost_func in comp.properties.iteritems():
            #NOTE:
            # we here replace hyphens with underscores in the names of properties
            # since hyphens are not valid in variable names in C++
            CFILE.write('  propertylist[ds->getPropertyByName("%s")] = "%s";\n' % \
                (name.replace('-', '_'), " ".join(regex.split(cost_func))))
        CFILE.write('  comp->setPropertyList(propertylist);\n')
        CFILE.write('  ds->addComponent(comp);\n')
        CFILE.write('  return;\n}\n\n')
        CFILE.flush()
        comp_node.clearObject()
    
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
    
    print "ALL DONE GENERATING CODE FOR PROPERTIES!"
