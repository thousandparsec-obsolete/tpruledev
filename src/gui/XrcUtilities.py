"""\
Custom classes and function for handling XRC files and custom widgets such as
the StyledTextCtrl and its subclass SchemeSTC
"""

import wx, wx.xrc
import gui.TextCtrl

class wxCheckListBoxHandler(wx.xrc.XmlResourceHandler):
    def __init__(self):
        wx.xrc.XmlResourceHandler.__init__(self)
        self.AddWindowStyles()
        
    def CanHandle(self, node):
        return self.IsOfClass(node, "wxCheckBoxList")
    
    def DoCreateResource(self):
        cbl = wx.CheckListBox(
            self.GetParentAsWindow(),
            self.GetID(),
            pos = self.GetPosition(),
            size = self.GetSize(),
            style=self.GetStyle()
        )      
        self.SetupWindow(cbl)     # handles font, bg/fg color
        return cbl
        
class wxSchemeStcHandler(wx.xrc.XmlResourceHandler):
    def __init__(self):
        wx.xrc.XmlResourceHandler.__init__(self)
        self.AddWindowStyles()
        
    def CanHandle(self, node):
        return self.IsOfClass(node, "SchemeSTC")
    
    def DoCreateResource(self):
        stc = gui.TextCtrl.SchemeSTC(
            self.GetParentAsWindow(),
            self.GetID(),
            pos = self.GetPosition(),
            size = self.GetSize(),
            style=self.GetStyle()
        )      
        self.SetupWindow(stc)     # handles font, bg/fg color
        return stc

class XmlResource(wx.xrc.XmlResource):
    def __init__(self, filemask, flags=wx.xrc.XRC_USE_LOCALE):
        wx.xrc.XmlResource.__init__(self, filemask, flags)
        self.InsertHandler(wxSchemeStcHandler())
        self.InsertHandler(wxCheckListBoxHandler())