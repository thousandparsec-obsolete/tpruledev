#!/usr/bin/env python

"""\
Runs the TPCL Expression Editor on its own for 
testing purposes.
"""

import wx
import gui.TpclEditorDialog
from rde import ConfigManager
from tpcl.data import Import

class App(wx.App):
    def OnInit(self):
        self.frame = wx.Frame(None, wx.ID_ANY, 'Editor Test', size=(480, 320))
        self.frame.Show()
        self.SetTopWindow(self.frame)
        ConfigManager.LoadRDEConfig('tpconf')
        self.block_store = Import.InitializeBlockstore()
        butt = wx.Button(self.frame, label="Show Editor")
        self.Bind(wx.EVT_BUTTON, self.OnShowEditor, butt)
        
        return True
        
    def OnShowEditor(self, event):
        dialog = gui.TpclEditorDialog.MyDialog(self.frame, self.block_store)
        dialog.ShowModal()
        
def main():
    app = App(redirect=False)
    app.MainLoop()

if __name__ == '__main__':
    main()
