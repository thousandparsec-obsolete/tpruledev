"""
wx.Panel and associated methods for editing
a Property object
"""

import wx
import gui.TextCtrl, gui.XrcUtilities
from wx.xrc import XRCCTRL

class Panel(wx.Panel):
    """
    A wx.Panel for displaying and editing Categories
    """
    
    def __init__(self, category, parent, id=wx.ID_ANY, style=wx.EXPAND):
        #load from XRC, need to use two-stage create
        pre = wx.PrePanel()
        res = gui.XrcUtilities.XmlResource('./gui/xrc/CategoryPanel.xrc')
        res.LoadOnPanel(pre, parent, "CategoryPanel")
        self.PostCreate(pre)
        
        self.category = category
        self.OnCreate()
    
    def OnCreate(self):
        self.name_field = XRCCTRL(self, "name_field")
        self.name_field.SetLabel(str(self.category.name))
        self.desc_field = XRCCTRL(self, "desc_field")
        self.desc_field.SetValue(str(self.category.description))
        
        self.category.node.visible = True 
        
    def CheckForModification(self):
        print "Checking Category %s for modifications" % self.category.name
        mod = False
        #print "\description: %s <> %s" % (self.category.description, self.desc_field.GetValue())
        if self.category.description != self.desc_field.GetValue():
            mod = True
            self.category.description = self.desc_field.GetValue()
        
        if mod:
            self.category.node.SetModified(True)
        
    def cleanup(self):
        self.CheckForModification()
        self.category.node.visible = False
        self.category.node.clearObject()