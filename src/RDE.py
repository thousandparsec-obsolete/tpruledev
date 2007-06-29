#!/usr/bin/env python

"""
Thousand Parsec Ruleset Developement Environment launcher script.
"""

import wx, ConfigParser
import gui.EditorFrame
import sys  

class GlobalConfig(object):
    config = None

class App(wx.App):
    def OnInit(self):
        self.frame = gui.EditorFrame.Frame(None, wx.ID_ANY, 'Splitter Test', size=(800,600))
        self.frame.Show()
        self.SetTopWindow(self.frame)
        GlobalConfig.config = ConfigParser.ConfigParser()
        return True
        
def generateEditPanel(parent):
    return generateInfoPanel(parent)

def generateInfoPanel(parent):
    print "Generating panel for RDE Module."
    panel = wx.Panel(parent, wx.ID_ANY)
    panel.SetBackgroundColour('white')
    label = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_MULTILINE)
    label.SetValue("Welcome to the Thousand Parsec Ruleset Developement Environment.\n"
                  "\n"
                  "This application allows for the rapid development of Rulesets for "
                  "the Thousand Parsec protocol by managing game objects and generating "
                  "the code needed by Thousand Parsec servers to implement those objects.\n"
                  "\n"
                  "To get started create a new project with the name of the ruleset that "
                  "you are developing and begin creating objects. Alternatively you can open "
                  "a project that already exists.")
    label.SetEditable(False)
    border1 = wx.BoxSizer(wx.HORIZONTAL)
    border1.Add(label, 1, wx.ALL | wx.EXPAND, 5)
    border2 = wx.BoxSizer(wx.VERTICAL)
    border2.Add(border1, 1, wx.ALL | wx.EXPAND, 5)
    panel.SetSizer(border2)
    return panel    

if __name__ == '__main__':
    app = App(redirect=False)
    app.MainLoop()