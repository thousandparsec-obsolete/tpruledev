"""\
Custom classes and function for handling XRC files and custom widgets such as
the StyledTextCtrl and its subclass SchemeSTC
"""

import wx, wx.xrc
import gui.TextCtrl

class XmlResource(wx.xrc.XmlResource):
    def __init__(self, filemask, flags=wx.xrc.XRC_USE_LOCALE):
        wx.xrc.XmlResource.__init__(self, filemask, flags)
        self.InsertHandler(gui.TextCtrl.wxSchemeStcHandler())