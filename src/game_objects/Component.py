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

def GetName():
    return 'Component'
