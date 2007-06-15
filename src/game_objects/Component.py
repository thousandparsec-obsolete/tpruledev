"""
Component.py
Representation of Components.
"""

import os, wx
import xml.dom.minidom
from xml.dom.minidom import Node
import ObjectUtilities, RDE, ComponentPanel

def generateEditPanel(parent):
    print "Generating panel for Component module."
    panel = wx.Panel(parent, wx.ID_ANY)
    panel.SetBackgroundColour('white')
    label = wx.StaticText(panel, wx.ID_ANY, "Test panel for value Component module.")
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
    comp_id = ObjectUtilities.sentinelProperty('comp_id')
    rank = ObjectUtilities.sentinelProperty('rank')
    desc = ObjectUtilities.sentinelProperty('desc')
    cat_id = ObjectUtilities.sentinelProperty('cat_id')
    tpcl_req = ObjectUtilities.sentinelProperty('tpcl_req')

    def __init__(self, node, name, comp_id = -1, rank = -1,
                 desc = '', cat_id = -1,
                 tpcl_req = '', load_immediate = False):
                 
        self.node = node
        self.filename = RDE.GlobalConfig.config.get('Current Project', 'persistence_directory') + \
                                               'Component/' + name + '.xml'
        
        if load_immediate:
            self.loadFromFile()
        else:
            self.properties = {}
            self.component_id = comp_id
            self.category_id = cat_id
            self.rank = rank
            self.name = name
            self.description = desc
            self.tpcl_requirements = tpcl_req
            
        self.node.clearModified()

    def __str__(self):
        return "Component Game Object - " + self.name
            
    def loadFromFile(self):
        doc = xml.dom.minidom.parse(self.filename)
        #there should only be one property node...but even so
        root = doc.getElementsByTagName("component")[0]
        self.name = root.getElementsByTagName("name")[0].childNodes[0].data
        self.component_id = root.getElementsByTagName("component_id")[0].childNodes[0].data
        self.category_id = root.getElementsByTagName("category_id")[0].childNodes[0].data
        self.description = root.getElementsByTagName("description")[0].childNodes[0].data
        self.tpcl_requirements = root.getElementsByTagName("tpcl_requirements")[0].childNodes[0].data
        #now the properties associated with this component
        self.properties = {}
        for prop in root.getElementsByTagName("property"):
            self.properties[prop.getElementsByTagName("name")[0].childNodes[0].data] = prop.getElementsByTagName("tpcl_cost")[0].childNodes[0].data
    
    def storeToFile(self, file):
        return
    
    def generateEditPanel(self, parent):
        #make the panel
        return ComponentPanel.Panel(self, parent)

    def createLabel(self, panel, text):
        return wx.StaticText(panel, wx.ID_ANY, text, style=wx.ALIGN_RIGHT | wx.ALIGN_TOP)
    
    def addLabelToFlex(self, flex, label):
        flex.Add(label, 2, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.EXPAND, 5)

    def createField(self, panel, text):
        return wx.TextCtrl(panel, wx.ID_ANY, text)
        
    def addFieldToFlex(self, flex, field):
        flex.Add(field, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 5)

def getName():
    return 'Component'

def generateCode(outdir, props):
    print "Called Component's generateCode function"
