"""
Thousand Parsec Ruleset Developement Environment launcher script.
"""

import wx
import sys
import core.EditorFrame
import ConfigParser
from ConfigParser import ConfigParser

sys.path.append('.')

class GlobalConfig(object):
    config = None

class RDE(wx.App):
    def OnInit(self):
        self.frame = core.EditorFrame.Frame(None, wx.ID_ANY, 'Splitter Test', size=(640,480))
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

if __name__ == '__main__':
    app = RDE(redirect=False)
    app.MainLoop()