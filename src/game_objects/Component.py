"""
Component.py
Representation of Components.
"""

import os, wx
import xml.dom.minidom
from xml.dom.minidom import Node
import ObjectUtilities, RDE, ComponentPanel
from ObjectUtilities import getXMLString, getXMLNum

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
    border1.Add(label, 1, wx.ALL | wx.EXPAND, 5)
    border2 = wx.BoxSizer(wx.VERTICAL)
    border2.Add(border1, 1, wx.ALL | wx.EXPAND, 5)
    panel.SetSizer(border2)
    return panel

def compareFunction(comp1, comp2):
    id1 = int(comp1.component_id)
    id2 = int(comp2.component_id)
    if id1 < id2:
        return -1
    if id1 == id2:
        return 0
    return 1

class Object(ObjectUtilities.GameObject):
    component_id = ObjectUtilities.sentinelProperty('component_id')
    description = ObjectUtilities.sentinelProperty('description')
    category_id = ObjectUtilities.sentinelProperty('category_id')
    tpcl_requirements = ObjectUtilities.sentinelProperty('tpcl_requirements')
    properties = ObjectUtilities.sentinelProperty('properties')

    def __init__(self, node, name, comp_id = -1,
                 desc = "Null", cat_id = -1,
                 tpcl_req = "Null", load_immediate = False):
                 
        self.node = node
        self.name = name
        self.filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Component', name + '.xml')
        
        if load_immediate:
            self.loadFromFile()
        else:
            self.properties = {}
            self.component_id = comp_id
            self.category_id = cat_id
            self.name = name
            self.description = desc
            self.tpcl_requirements = tpcl_req
        
        if node != None:
            self.node.modified = False

    def __str__(self):
        return "Component Game Object - " + self.name
            
    def loadFromFile(self):
        try:
            doc = xml.dom.minidom.parse(self.filename)
            #there should only be one property node...but even so
            root = doc.getElementsByTagName("component")[0]
            self.name = getXMLString(root, "name")
            self.component_id = getXMLNum(root, "component_id")
            self.category_id = getXMLNum(root, "category_id")
            self.description = getXMLString(root, "description")
            self.tpcl_requirements = getXMLString(root, "tpcl_requirements")
            #now the properties associated with this component
            self.properties = {}
            for prop in root.getElementsByTagName("property"):
                self.properties[getXMLString(prop, "name")] = getXMLString(prop, "tpcl_cost")
        except IOError:
            #file does not exist
            # fill with default values
            self.component_id = -1
            self.category_id = -1
            self.description = ""
            self.tpcl_requirements = ""
            self.properties = {}
    
    def generateEditPanel(self, parent):
        #make the panel
        return ComponentPanel.Panel(self, parent)

def saveObject(comp):
    """\
    Saves a Component to its persistence file.
    """  
    filename = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'persistence_directory'),
                                               'Component', comp.name + '.xml')
    ofile = open(filename, 'w')
    ofile.write('<component>\n')
    ofile.write('    <name>' + comp.name + '</name>\n')
    ofile.write('    <component_id>' + str(comp.component_id) + '</component_id>\n')
    ofile.write('    <category_id>' + str(comp.category_id) + '</category_id>\n')
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
    os.remove(filename)

def getName():
    return 'Component'


def generateCode(outdir, props):
    print "Called Component's generateCode function"
