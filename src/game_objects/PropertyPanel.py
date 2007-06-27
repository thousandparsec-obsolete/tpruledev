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
        res = gui.XrcUtilities.XmlResource('./game_objects/xrc/PropertyPanel.xrc')
        res.LoadOnPanel(pre, parent, "PropertyPanel")
        self.PostCreate(pre)
        
        self.property = property
        self.OnCreate()
    
    def OnCreate(self):
        self.rank_field = XRCCTRL(self, "rank_field")
        self.rank_field.SetValue(str(self.property.rank))
        self.propid_field = XRCCTRL(self, "propid_field")
        self.propid_field.SetValue(str(self.property.property_id))
        self.catid_field = XRCCTRL(self, "catid_field")
        self.catid_field.SetValue(str(self.property.category_id))
        self.desc_field = XRCCTRL(self, "desc_field")
        self.desc_field.SetValue(str(self.property.description))
        self.disp_field = XRCCTRL(self, "disp_field")
        self.disp_field.SetValue(str(self.property.display_text))
        self.tpcl_disp_stc = XRCCTRL(self, "tpcl_disp_stc")
        self.tpcl_disp_stc.SetText(str(self.property.tpcl_display))        
        self.tpcl_req_stc = XRCCTRL(self, "tpcl_req_stc")
        self.tpcl_req_stc.SetText(str(self.property.tpcl_requires))
        
    def CheckForModification(self):
        print "Checking Property %s for modifications" % self.property.name
        mod = False
        #print "\property_id: %s <> %s" % (self.component.property_id, self.property_id.GetValue())
        if str(self.property.property_id) != self.propid_field.GetValue():
            mod = True
            self.property.component_id = self.propid_field.GetValue()
        
        #print "\category_id: %s <> %s" % (self.property.category_id, self.catid_field.GetValue())
        if str(self.property.category_id) != self.catid_field.GetValue():
            mod = True
            self.property.category_id = self.catid_field.GetValue()
        
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
    
    def createLabel(self, text):
        return wx.StaticText(self, wx.ID_ANY, text, style=wx.ALIGN_RIGHT | wx.ALIGN_TOP)
    
    def addLabelToFlex(self, flex, label):
        flex.Add(label, 2, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.EXPAND, 5)

    def createField(self, text):
        return wx.TextCtrl(self, wx.ID_ANY, text)
        
    def createTextArea(self, text):
        return gui.TextCtrl.SchemeSTC(self, wx.ID_ANY, text)
        
    def addFieldToFlex(self, flex, field):
        flex.Add(field, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 5)
        
    def cleanup(self):
        self.CheckForModification()
        self.property.node.clearObject()