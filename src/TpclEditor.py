"""\
Runs the TPCL Expression Editor on its own for 
testing purposes.
"""

import wx
import gui.TpclEditorDialog
from rde import ConfigManager

class App(wx.App):
    def OnInit(self):
        self.frame = wx.Frame(None, wx.ID_ANY, 'Editor Test', size=(480, 320))
        self.frame.Show()
        self.SetTopWindow(self.frame)
        ConfigManager.LoadRDEConfig('tpconf')
        dialog = gui.TpclEditorDialog.Dialog(None)
        dialog.ShowModal()
        return True
        
def main():
    app = App(redirect=False)
    app.MainLoop()

if __name__ == '__main__':
    main()