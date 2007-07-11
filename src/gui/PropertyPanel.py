"""
wx.Panel and associated methods for editing
a Property object
"""

import wx
import gui.TextCtrl, gui.XrcUtilities
import ObjectPanel
from wx.xrc import XRCCTRL

class Panel(ObjectPanel.Panel):
    """
    A wx.Panel for displaying and editing Properties
    """
    
    def __init__(self, parent, id=wx.ID_ANY, style=wx.EXPAND):
        #load from XRC, need to use two-stage create
        pre = wx.PrePanel()
        res = gui.XrcUtilities.XmlResource('./gui/xrc/PropertyPanel.xrc')
        res.LoadOnPanel(pre, parent, "PropertyPanel")
        self.PostCreate(pre)

        self.OnCreate()
    
    def OnCreate(self):
        self.name_field = XRCCTRL(self, "name_field")
        self.rank_field = XRCCTRL(self, "rank_field")
        self.desc_field = XRCCTRL(self, "desc_field")
        self.disp_field = XRCCTRL(self, "disp_field")
        self.tpcl_disp_stc = XRCCTRL(self, "tpcl_disp_stc")      
        self.tpcl_req_stc = XRCCTRL(self, "tpcl_req_stc")        
        self.cat_choice = XRCCTRL(self, "cat_choice")   
        self.BindEditWatchers([self.desc_field, self.rank_field, self.disp_field,
                                self.tpcl_disp_stc, self.tpcl_req_stc])
        self.loaded = False
        
    def LoadObject(self, prop):
        self.object = prop
        self.object.node.visible = True
        
        self.name_field.SetLabel(str(self.object.name))
        self.rank_field.SetValue(str(self.object.rank))
        self.desc_field.SetValue(str(self.object.description))
        self.disp_field.SetValue(str(self.object.display_text))
        self.tpcl_disp_stc.SetText(str(self.object.tpcl_display))
        self.tpcl_req_stc.SetText(str(self.object.tpcl_requires))
        
        #fill the category choice box
        self.cat_choice.Clear()
        self.cat_choice.Append("")
        catidx = 0
        for catnode in self.object.node.object_database.getObjectsOfType('Category'):
            idx = self.cat_choice.Append(catnode.name)                
            if self.object.category == catnode.name:
                catidx = idx
        self.cat_choice.Select(catidx)
        self.cat_choice.Bind(wx.EVT_CHOICE, self.CreateChoiceMonitor(self.object.category))
        
        self.loaded = True
        
        self.Show()
        return self           
        
    def CheckForModification(self):
        print "Checking Property %s for modifications" % self.object.name
        if self.loaded:
            mod = False
            
            #print "\category_id: %s <> %s" % (self.object.category_id, self.catid_field.GetValue())
            if self.object.category != self.cat_choice.GetStringSelection():
                mod = True
                self.object.category = self.cat_choice.GetStringSelection()
            
            #display text
            if self.object.display_text != self.disp_field.GetValue():
                mod = True
                self.object.display_text = self.disp_field.GetValue()
                
            #rank
            if str(self.object.rank) != self.rank_field.GetValue():
                mod = True
                self.object.rank = self.rank_field.GetValue()
            
            #print "\description: %s <> %s" % (self.object.description, self.desc_field.GetValue())
            if self.object.description != self.desc_field.GetValue():
                mod = True
                self.object.description = self.desc_field.GetValue()
                
            #print "\tpcl_requires: %s <> %s" % (self.object.tpcl_requires, self.tpcl_req_ctrl.GetText())
            if self.object.tpcl_requires != self.tpcl_req_stc.GetText():
                mod = True
                self.object.tpcl_requires = self.tpcl_req_stc.GetText()
                
            #print "\tpcl_display: %s <> %s" % (self.object.tpcl_display, self.tpcl_req_ctrl.GetText())
            if self.object.tpcl_display != self.tpcl_disp_stc.GetText():
                mod = True
                self.object.tpcl_display = self.tpcl_disp_stc.GetText()
            
            if mod:
                self.object.node.SetModified(True)
            
    def Destroy(self):
        self.Hide()
        
    def ReallyDestroy(self):
        wx.Panel.Destroy(self)
        
    def cleanup(self):
        self.CheckForModification()
        self.object.node.visible = False
        self.Hide()
        self.object.node.clearObject()
        self.object = None
        self.loaded = False