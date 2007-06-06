"""
Component.py
Representation of Components.
"""

import os, os.path
import wx
import xml.dom.minidom
from xml.dom.minidom import Node

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

class Object(object):
    def __init__(self, comp_id = -1, rank = -1,
                 name = '', desc = '', cat_id = -1,
                 tpcl_req = '', file=''):
        self.properties = {}
        if (file != ''):
            self.loadFromFile(file)
        else:
            self.component_id = comp_id
            self.category_id = cat_id
            self.rank = rank
            self.name = name
            self.description = desc
            self.tpcl_requirements = tpcl_req

    def __str__(self):
        return "Component Game Object - " + self.name
            
    def loadFromFile(self, file):
        doc = xml.dom.minidom.parse(file)
        #there should only be one property node...but even so
        root = doc.getElementsByTagName("component")[0]
        self.name = root.getElementsByTagName("name")[0].childNodes[0].data
        self.component_id = root.getElementsByTagName("component_id")[0].childNodes[0].data
        self.category_id = root.getElementsByTagName("category_id")[0].childNodes[0].data
        self.description = root.getElementsByTagName("description")[0].childNodes[0].data
        self.tpcl_requirements = root.getElementsByTagName("tpcl_requirements")[0].childNodes[0].data
        #now the properties associated with this component
        for prop in root.getElementsByTagName("property"):
            self.properties[prop.getElementsByTagName("property_id")[0].childNodes[0].data] = prop.getElementsByTagName("tpcl_cost")[0].childNodes[0].data
    
    def storeToFile(self, file):
        return
    
    def generateEditPanel(self, parent):
        #make the panel
        panel = wx.Panel(parent, wx.ID_ANY, style=wx.EXPAND)
        flex_sizer = wx.FlexGridSizer(6, 2, 5, 5)
        flex_sizer.SetFlexibleDirection(wx.BOTH)
        
        name_label = self.createLabel(panel, "Name:")
        self.addLabelToFlex(flex_sizer, name_label)
        name_field = self.createField(panel, str(self.name))
        self.addFieldToFlex(flex_sizer, name_field)

        comp_id_label = self.createLabel(panel, "Component ID:")
        self.addLabelToFlex(flex_sizer, comp_id_label)
        comp_id_field = self.createField(panel, str(self.component_id))
        self.addFieldToFlex(flex_sizer, comp_id_field)

        category_id_label = self.createLabel(panel, "Category ID:")
        self.addLabelToFlex(flex_sizer, category_id_label)
        category_id_field = self.createField(panel, str(self.category_id))
        self.addFieldToFlex(flex_sizer, category_id_field)

        desc_label = self.createLabel(panel, "Description:")
        self.addLabelToFlex(flex_sizer, desc_label)
        desc_field = self.createField(panel, str(self.description))
        self.addFieldToFlex(flex_sizer, desc_field)

        tpcl_req_label = self.createLabel(panel, "TPCL Requirements Function:")
        self.addLabelToFlex(flex_sizer, tpcl_req_label)
        tpcl_req_field = self.createField(panel, str(self.tpcl_requirements))
        self.addFieldToFlex(flex_sizer, tpcl_req_field)

        props_label = self.createLabel(panel, "Associated Properties:")
        self.addLabelToFlex(flex_sizer, props_label)
        #TODO make this into a ListCtrl
        prop_list = wx.ListBox(panel, wx.ID_ANY)
        for prop_id, tpcl_cost in self.properties.iteritems():
            prop_list.Insert(str(prop_id) + " - " + str(tpcl_cost), 0)
        self.addFieldToFlex(flex_sizer, prop_list)
       
        flex_sizer.AddGrowableCol(1) #field column
        flex_sizer.AddGrowableRow(4) #tpcl_requirements function
        flex_sizer.AddGrowableRow(5) #property list

        
        border1 = wx.BoxSizer(wx.HORIZONTAL)
        border1.Add(flex_sizer, 1, wx.ALL | wx.EXPAND, 5)
        border2 = wx.BoxSizer(wx.VERTICAL)
        border2.Add(border1, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(border2)
    
        return panel

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
