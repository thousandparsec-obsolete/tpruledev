"""\
The dialog class for the TPCL Expression Editor.
"""

import wx
import gui.XrcUtilities
from wx.xrc import XRCCTRL

class BlockInfoDialog(wx.Dialog):
    """
    A wx.Panel for displaying and editing Categories
    """
    
    def __init__(self, parent, name, display, description, id=wx.ID_ANY, style=wx.EXPAND):
        #load from XRC, need to use two-stage create
        res = gui.XrcUtilities.XmlResource('./gui/xrc/BlockInfoDialog.xrc')
        pre = wx.PreDialog()
        res.LoadOnDialog(pre, parent, "dialog")
        self.PostCreate(pre)        

        self.name = name
        self.display = display
        self.description = description
        self.OnCreate()
    
    def OnCreate(self):
        #self.SetSize((600, 400))
	    self.name_label = XRCCTRL(self, "name_label")
	    self.name_label.SetLabel(self.name)
	    self.display_ctrl = XRCCTRL(self, "display_ctrl")
	    self.display_ctrl.SetValue(self.display)
	    self.description_ctrl = XRCCTRL(self, "description_ctrl")
	    self.description_ctrl.SetValue(self.description)