"""
wx.Panel and associated methods for editing
a Property object
"""

import wx
import gui.TextCtrl, gui.XrcUtilities
from wx.xrc import XRCCTRL

class Panel(wx.Panel):
    """
    A wx.Panel for displaying and editing Properties
    """
    
    def __init__(self, property, parent, id=wx.ID_ANY, style=wx.EXPAND):
        #load from XRC, need to use two-stage create
        pre = wx.PrePanel()
        res = gui.XrcUtilities.XmlResource('./gui/xrc/PropertyPanel.xrc')
        res.LoadOnPanel(pre, parent, "PropertyPanel")
        self.PostCreate(pre)
        
        self.property = property
        self.OnCreate()
    
    def OnCreate(self):
        name_field = XRCCTRL(self, "name_field")
        name_field.SetLabel(str(self.property.name))
        self.rank_field = XRCCTRL(self, "rank_field")
        self.rank_field.SetValue(str(self.property.rank))
        self.cat_choice = XRCCTRL(self, "cat_choice")
        self.desc_field = XRCCTRL(self, "desc_field")
        self.desc_field.SetValue(str(self.property.description))
        self.disp_field = XRCCTRL(self, "disp_field")
        self.disp_field.SetValue(str(self.property.display_text))
        self.tpcl_disp_stc = XRCCTRL(self, "tpcl_disp_stc")
        self.tpcl_disp_stc.SetText(str(self.property.tpcl_display))        
        self.tpcl_req_stc = XRCCTRL(self, "tpcl_req_stc")
        self.tpcl_req_stc.SetText(str(self.property.tpcl_requires))
        
        self.property.node.visible = True 
        
    def CheckForModification(self):
        print "Checking Property %s for modifications" % self.property.name
        mod = False
        
        #print "\category_id: %s <> %s" % (self.property.category_id, self.catid_field.GetValue())
        #if str(self.property.category_id) != self.catid_field.GetValue():
        #    mod = True
        #    self.property.category_id = self.catid_field.GetValue()
        
        #display text
        if self.property.display_text != self.disp_field.GetValue():
            mod = True
            self.property.display_text = self.disp_field.GetValue()
            
        #rank
        if str(self.property.rank) != self.rank_field.GetValue():
            mod = True
            self.property.rank = self.rank_field.GetValue()
        
        #print "\description: %s <> %s" % (self.property.description, self.desc_field.GetValue())
        if self.property.description != self.desc_field.GetValue():
            mod = True
            self.property.description = self.desc_field.GetValue()
            
        #print "\tpcl_requires: %s <> %s" % (self.property.tpcl_requires, self.tpcl_req_ctrl.GetText())
        if self.property.tpcl_requires != self.tpcl_req_stc.GetText():
            mod = True
            self.property.tpcl_requires = self.tpcl_req_stc.GetText()
            
        #print "\tpcl_display: %s <> %s" % (self.property.tpcl_display, self.tpcl_req_ctrl.GetText())
        if self.property.tpcl_display != self.tpcl_disp_stc.GetText():
            mod = True
            self.property.tpcl_display = self.tpcl_disp_stc.GetText()
        
        if mod:
            self.property.node.SetModified(True)
        
    def cleanup(self):
        self.CheckForModification()
        self.property.node.visible = False
        self.property.node.clearObject()