import wx

class MyFrame(wx.Frame):

    """frame with panel containing two labels and two textcontrols"""
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'wx.FlexGridSizer', size=(350, 100))
        panel = wx.Panel(self, -1)
        basicLabel = wx.StaticText(panel, -1, "Basic wx.TextCtrl:")
        # size height = -1 implies height as needed
        basicText = wx.TextCtrl(panel, -1, "Normal text", size=(175, -1))

        pwdLabel = wx.StaticText(panel, -1, "Password wx.TextCtrl:")
        # the password will show up as dots
        pwdText = wx.TextCtrl(panel, -1, "password", size=(175, -1), style=wx.TE_PASSWORD)
        
        # hgap is between columns, vgap between rows
        sizer = wx.FlexGridSizer(rows=2, cols=2, hgap=10, vgap=5)
        sizer.Add(basicLabel)  # row1, col1
        sizer.Add(basicText)   # row1, col2
        sizer.Add(pwdLabel)    # row2, col1
        sizer.Add(pwdText)     # row2, col2
        sizer.AddGrowableCol(0)
        sizer.AddGrowableCol(1)
        # or use: sizer.AddMany([basicLabel, basicText, pwdLabel, pwdText])
        #panel.SetSizer(sizer)  # use this if you don't want the boxsizer border
        
        # optionally use boxsizer to add a border/gap around sizer ...
        border = wx.BoxSizer()
        border.Add(sizer, 0, wx.ALL, 10)
        panel.SetSizerAndFit(border)
        self.Fit()

app = wx.PySimpleApp()
frame = MyFrame()
frame.Show()
app.MainLoop()
