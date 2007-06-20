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
import PropertyPanel

def generateEditPanel(parent):
    print "Generating panel for Property module."
    panel = wx.Panel(parent, wx.ID_ANY)
    panel.SetBackgroundColour('white')
    label = wx.StaticText(panel, wx.ID_ANY, "Test panel for value Property module.")
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
    prop_id = ObjectUtilities.sentinelProperty('prop_id')
    rank = ObjectUtilities.sentinelProperty('rank')
    desc = ObjectUtilities.sentinelProperty('desc')
    disp_text = ObjectUtilities.sentinelProperty('disp_text')
    tpcl_disp = ObjectUtilities.sentinelProperty('tpcl_disp')
    tpcl_req = ObjectUtilities.sentinelProperty('tpcl_req')

    def __init__(self, node, name, catid = -1, prop_id = -1, rank = -1,
                 desc = '', disp_text = '', tpcl_disp = '', tpcl_req = '',
                 load_immediate=False):

        self.node = node
        self.filename = RDE.GlobalConfig.config.get('Current Project', 'persistence_directory') + \
                                               'Property/' + name + '.xml'
                 
        if (load_immediate):
            self.loadFromFile()
        else:
            self.category_id = catid
            self.property_id = prop_id
            self.rank = rank
            self.name = name
            self.description = desc
            self.display_text = disp_text
            self.tpcl_display = tpcl_disp
            self.tpcl_requires = tpcl_req
            
        self.node.clearModified()

    def __str__(self):
        return "Property Game Object - " + self.name
    
    def loadFromFile(self):
        doc = xml.dom.minidom.parse(self.filename)
        #there should only be one property node...but even so
        root = doc.getElementsByTagName("property")[0]
        self.name = root.getElementsByTagName("name")[0].childNodes[0].data
        self.rank = root.getElementsByTagName("rank")[0].childNodes[0].data
        self.property_id = root.getElementsByTagName("property_id")[0].childNodes[0].data
        self.category_id = root.getElementsByTagName("category_id")[0].childNodes[0].data
        self.description = root.getElementsByTagName("description")[0].childNodes[0].data
        self.display_text = root.getElementsByTagName("display_text")[0].childNodes[0].data
        self.tpcl_display = root.getElementsByTagName("tpcl_display")[0].childNodes[0].data
        self.tpcl_requires = root.getElementsByTagName("tpcl_requires")[0].childNodes[0].data

    """
    Yes. I do know that writing XML by hand is stupid. Not my problem right
    now, though. Busy getting it to read and populate a data structure
    first...then proper writeout
    """
    def storeToDir(self, dir):
        os.makedirs(dir) #this is only for while we're testin
        fname = dir + "/" + self.name + ".xml"
        out = os.open(fname)
        out.write("<property>\n")
        out.write("\t<name>" + self.name + "</name>")
        out.write("\t<rank>" + self.rank + "</rank>")
        out.write("\t<property_id>" + self.property_id + "</property_id>")
        out.write("\t<category_id>" + self.category_id + "</category_id>")
        out.write("\t<description>" + self.description + "</description>")
        out.write("\t<display_text>" + self.display_text + "</display_text>")
        out.write("\t<tpcl_display>" + self.tpcl_display + "</tpcl_display>")
        out.write("\t<tpcl_requires>" + self.tpcl_requires + "</tpcl_requires>")
        out.write("</property>")
    
    def generateEditPanel(self, parent):
        #make the panel
        return PropertyPanel.Panel(self, parent)    

    def createLabel(self, panel, text):
        return wx.StaticText(panel, wx.ID_ANY, text, style=wx.ALIGN_RIGHT | wx.ALIGN_TOP)
    
    def addLabelToFlex(self, flex, label):
        flex.Add(label, 2, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.EXPAND, 5)

    def createField(self, panel, text):
        return wx.TextCtrl(panel, wx.ID_ANY, text)
        
    def addFieldToFlex(self, flex, field):
        flex.Add(field, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 5)
        
    def OnEditPanelSave(self):
        self.storeToDir("persistence/Property")

def initializeSaveFile(name):
    """\
    Creates an empty save file for the Component with the given name
    """
    filename = RDE.GlobalConfig.config.get('Current Project', 'persistence_directory') + \
                                               'Property/' + name + '.xml'
    ofile = open(filename, 'w')
    ofile.write('<property>\n')
    ofile.write('    <name>' + name + '</name>\n')
    ofile.write('    <property_id>0</property_id>\n')
    ofile.write('    <category_id>0</category_id>\n')
    ofile.write('    <rank>0</rank>\n')
    ofile.write('    <display_text>Null</display_text>\n')
    ofile.write('    <description>Null</description>\n')
    ofile.write('    <tpcl_display>(lambda 0)</tpcl_display>\n')
    ofile.write('    <tpcl_requires>(lambda 0)</tpcl_requires>\n')
    ofile.write('</property>\n')	
    ofile.flush()
    ofile.close()
    
def deleteSaveFile(name):
    """\
    Deletes the save file for a Component that has been deleted.
    """
    filename = RDE.GlobalConfig.config.get('Current Project', 'persistence_directory') + \
                                               'Property/' + name + '.xml'
    os.remove(filename)

def getName():
    return 'Property'

def generateCode(outdir, props=None):
    print "Called Property's generateCode function"
