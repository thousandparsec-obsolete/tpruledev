"""
Creates a 3x3 grid of labels to test the
FlexGridSizer and GridBagSizer
"""

import wx

FRAME_ID = 101

class ObjPanelTest(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(300, 400))
        self.Bind(wx.EVT_SIZING, self.OnSizeEvent)
        self.panel = wx.Panel(self, wx.ID_ANY, style=wx.EXPAND)
        self.flex_sizer = wx.FlexGridSizer(3, 2, 5, 5)
        #self.vert_sizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(3):
            #we want three rows
            #horz_sizer = wx.BoxSizer(wx.HORIZONTAL)
            tex1 = wx.StaticText(self.panel, -1, "Label #" + str(i) + ":", style=wx.EXPAND)
            tex2 = wx.TextCtrl(self.panel, -1, "Value #" + str(i), style=wx.EXPAND)
            self.flex_sizer.Add(tex1, 1, wx.ALIGN_RIGHT, 5)
            self.flex_sizer.Add(tex2, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 5)
            #horz_sizer.Add(tex1, 1, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
            #horz_sizer.Add(tex2, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 5)
            #self.vert_sizer.Add(horz_sizer, 1, wx.ALL | wx.EXPAND)
            #if (i < 2):
            #    self.vert_sizer.AddSpacer((5,5))
        border = wx.BoxSizer()
        border.Add(self.flex_sizer, 1, wx.ALL, 5)
        self.flex_sizer.AddGrowableCol(1)
        self.flex_sizer.AddGrowableRow(0)
        self.flex_sizer.AddGrowableRow(1)
        self.flex_sizer.AddGrowableRow(2)
        self.panel.SetSizerAndFit(border)
        self.Fit()
        self.Show(True)
        
    def OnSizeEvent(self, e):
        print "Got size event!"
        self.Fit()

app = wx.PySimpleApp()
frame = ObjPanelTest(None, -1, "FlexGridSizer Test")
app.MainLoop() 