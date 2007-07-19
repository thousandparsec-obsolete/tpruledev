"""
wx.Panel and associated methods for editing
a Property object
"""

import wx
import ObjectPanel
import gui.TextCtrl, gui.XrcUtilities
from wx.xrc import XRCCTRL

class Panel(ObjectPanel.Panel):
    """
    A wx.Panel for displaying and editing Categories
    """
    
    def __init__(self, parent, id=wx.ID_ANY, style=wx.EXPAND):
        #load from XRC, need to use two-stage create
        pre = wx.PrePanel()
        res = gui.XrcUtilities.XmlResource('./gui/xrc/CategoryPanel.xrc')
        res.LoadOnPanel(pre, parent, "CategoryPanel")
        self.PostCreate(pre)

        ObjectPanel.Panel.Setup(self)
        self.OnCreate()
    
    def OnCreate(self):
        self.name_field = XRCCTRL(self, "name_field")
        self.desc_field = XRCCTRL(self, "desc_field")
        
        self.desc_field.Bind(wx.EVT_TEXT, self.CreateAttributeMonitor('description'))

        self.loaded = False
        
    def LoadObject(self, node):
        self.loading = True
        self.node = node
        self.object = node.GetObject()
        self.node.visible = True
        self.name_field.SetLabel(str(self.object.name))
        self.desc_field.SetValue(str(self.object.description))
        self.desc_field.attr_name = 'description'
        if self.object.errors.has_key('description'):
            print "Error in description!"
            self.SetErrorLabel('description', self.object.errors['description'])
        
        self.loaded = True
        
        self.loading = False
        self.Show()
        return self
        
    def cleanup(self):
        self.node.visible = False
        self.Hide()
        self.node.ClearObject()
        self.object = None
        self.loaded = False