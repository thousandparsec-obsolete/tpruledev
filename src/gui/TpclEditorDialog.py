"""\
The dialog class for the TPCL Expression Editor.
"""

import wx
import gui.XrcUtilities
from wx.xrc import XRCCTRL

class Dialog(wx.Dialog):
    """
    A wx.Panel for displaying and editing Categories
    """
    
    def __init__(self, parent, id=wx.ID_ANY, style=wx.EXPAND):
        #load from XRC, need to use two-stage create
        pre = wx.PreDialog()
        res = gui.XrcUtilities.XmlResource('./gui/xrc/EditorDialog.xrc')
        res.LoadOnDialog(pre, parent, "editor")
        self.PostCreate(pre)

        self.OnCreate()
    
    def OnCreate(self):
        pass