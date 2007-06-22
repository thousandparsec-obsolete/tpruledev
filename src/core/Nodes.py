"""
Nodes for object storage and such.
"""

import wx

class DatabaseNode(object):
    def generateEditPanel(self, parent):
        print "Generating DefaultNode panel"
        panel = wx.Panel(parent, wx.ID_ANY)
        panel.SetBackgroundColour('white')
        label = wx.StaticText(panel, wx.ID_ANY, "Default Node Panel")
        return panel    
   
            
class DefaultNode(DatabaseNode):
    def __init__(self, name):
        self.name = name
    
    def generateEditPanel(self, parent):
        print "Generating panel for [%s]" % self.name
        panel = wx.Panel(parent, wx.ID_ANY)
        panel.SetBackgroundColour('white')
        label = wx.StaticText(panel, wx.ID_ANY, "Default panel for value %s" % self.name)
        return panel   