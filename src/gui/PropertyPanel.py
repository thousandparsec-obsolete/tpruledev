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
    
        ObjectPanel.Panel.Setup(self)
        self.OnCreate()
    
    def OnCreate(self):
        self.name_field = XRCCTRL(self, "name_field")
        self.rank_field = XRCCTRL(self, "rank_field")
        self.desc_field = XRCCTRL(self, "desc_field")
        self.disp_field = XRCCTRL(self, "disp_field")
        self.tpcl_disp_stc = XRCCTRL(self, "tpcl_disp_stc")      
        self.tpcl_req_stc = XRCCTRL(self, "tpcl_req_stc")        
        self.cat_choice = XRCCTRL(self, "cat_choice")
        
        self.desc_field.Bind(wx.EVT_TEXT, self.CreateAttributeMonitor('description'))
        self.rank_field.Bind(wx.EVT_TEXT, self.CreateAttributeMonitor('rank'))
        self.disp_field.Bind(wx.EVT_TEXT, self.CreateAttributeMonitor('display_text'))
        self.tpcl_disp_stc.Bind(wx.stc.EVT_STC_CHANGE, self.CreateAttributeMonitor('tpcl_display'))
        self.tpcl_req_stc.Bind(wx.stc.EVT_STC_CHANGE, self.CreateAttributeMonitor('tpcl_requires'))
        self.cat_choice.Bind(wx.EVT_CHECKLISTBOX, self.CreateAttributeMonitor('categories'))
        
        self.loaded = False
        
    def LoadObject(self, node):
        self.loading = True
        self.node = node
        self.object = node.GetObject()
        self.node.visible = True
        
        self.name_field.SetLabel(str(self.object.name))
        
        self.rank_field.SetValue(str(self.object.rank))
        if self.object.errors.has_key('rank'):
            print "Error in rank!"
            self.SetErrorLabel('rank', self.object.errors['rank'])
            
        self.desc_field.SetValue(str(self.object.description))
        if self.object.errors.has_key('description'):
            print "Error in description!"
            self.SetErrorLabel('description', self.object.errors['description'])
        
        self.disp_field.SetValue(str(self.object.display_text))
        if self.object.errors.has_key('display_text'):
            print "Error in display_text!"
            self.SetErrorLabel('display_text', self.object.errors['display_text'])
        
        self.tpcl_disp_stc.SetText(str(self.object.tpcl_display))
        if self.object.errors.has_key('tpcl_display'):
            print "Error in tpcl_display!"
            self.SetErrorLabel('tpcl_display', self.object.errors['tpcl_display'])
        
        self.tpcl_req_stc.SetText(str(self.object.tpcl_requires))
        if self.object.errors.has_key('tpcl_requires'):
            print "Error in tpcl_requires!"
            self.SetErrorLabel('tpcl_requires', self.object.errors['tpcl_requires'])
        
        #fill the category choice box
        self.cat_choice.Clear()
        for catnode in self.node.object_database.getObjectsOfType('Category'):
            idx = self.cat_choice.Append(catnode.name)                
            if catnode.name in self.object.categories:
                self.cat_choice.Check(idx)
        if self.object.errors.has_key('categories'):
            print "Error in categories!"
            self.SetErrorLabel('categories', self.object.errors['categories'])
        
        self.loaded = True
        
        self.loading = False
        self.Show()
        return self           
            
    def Destroy(self):
        self.Hide()
        
    def ReallyDestroy(self):
        wx.Panel.Destroy(self)
        
    def cleanup(self):
        self.CleanupErrorLabels()
        self.node.visible = False
        self.Hide()
        self.node.ClearObject()
        self.object = None
        self.loaded = False