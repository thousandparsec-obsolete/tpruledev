"""\
Runs the TPCL Expression Editor on its own for 
testing purposes.
"""

import wx
import gui.TpclEditorDialog

class App(wx.App):
    def OnInit(self):
        self.frame = wx.Frame(None, wx.ID_ANY, 'Editor Test', size=(480, 320))
        self.frame.Show()
        self.SetTopWindow(self.frame)
        dialog = gui.TpclEditorDialog.Dialog(None)
        dialog.ShowModal()
        return True
        
def main():
    app = App(redirect=False)
    app.MainLoop()

if __name__ == '__main__':
    main()