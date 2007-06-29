"""
Category.py
Representation of Categories.
"""

import os, wx
import xml.dom.minidom
from xml.dom.minidom import Node
import ObjectUtilities, RDE, CategoryPanel
from ObjectUtilities import getXMLString, getXMLNum

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

def compareFunction(cat1, cat2):
    if cat1.name < cat2.name:
        return -1
    if cat1.name == cat2.name:
        return 0
    return 1

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
    ofile.write('    <name>' + comp.name + '</name>\n')
    ofile.write('    <description>' + comp.description + '</description>\n')
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


def GenerateCode(object_database):
    #don't want to yet
    return