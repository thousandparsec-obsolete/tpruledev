#!/usr/bin/env python

"""
Thousand Parsec Ruleset Developement Environment launcher script.
"""

import wx, ConfigParser
import core.EditorFrame
import sys  

class GlobalConfig(object):
    config = None

class App(wx.App):
    def OnInit(self):
        self.frame = core.EditorFrame.Frame(None, wx.ID_ANY, 'Splitter Test', size=(640,480))
        self.frame.Show()
        self.SetTopWindow(self.frame)
        GlobalConfig.config = ConfigParser.ConfigParser()
        return True

if __name__ == '__main__':
    app = App(redirect=False)
    app.MainLoop()