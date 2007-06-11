"""
EditorFrame.py
 Skeleton for the RDE. Will eventually evolve into the actual
 editor, but for the time being will serve as a testbed.
"""

import wx, os, ConfigParser
from ConfigParser import ConfigParser

import core.ObjectManagement
from core.ObjectManagement import ObjectDatabase, GameObjectTree
import RDE

SPLITTER_ID = 101
TREE_ID = 110

class Frame(wx.Frame):    
    def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                 size=wx.DefaultSize):
        wx.Frame.__init__(self, parent, id, title, pos, size)
        
        #import configuration settings, will build on this as is necessary
        RDE.GlobalConfig.config = ConfigParser()
        self.config = RDE.GlobalConfig.config
        self.config.readfp(open('tpconf'))
        self.config.read(self.config.get('DEFAULT', 'current_project'))
        self.SetTitle("TP-RDE: " + self.config.get('Current Project', 'project_name'))
        
        self.initGUI()
        
        self.object_database = self.tree.getObjectDatabase()
        self.object_database.loadObjectNames()

        #self.tree.Expand(self.root)
        
        self.Show(True)

    def initGUI(self):
        self.splitter = wx.SplitterWindow(self, SPLITTER_ID,
                                          style=wx.SP_NO_XP_THEME |
                                          wx.SP_3DSASH | wx.BORDER |
                                          wx.SP_3D)
        self.cp_right = wx.Panel(self.splitter, wx.ID_ANY)
        self.cp_right.SetBackgroundColour("black")
        
        self.tree = GameObjectTree(self.splitter, wx.ID_ANY)
        #self.root = self.tree.AddRoot("Game Objects")
        #self.tree.SetPyData(self.root, MyNode("Root"))
        self.tree.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeSelect)
        
        self.splitter.SetMinimumPaneSize(140)
        self.splitter.SplitVertically(self.tree,
                                      self.cp_right,
                                      150)
                                      
    def OnLeftDClick(self, event):
        print "Handling double click in Tree!"
        pt = event.GetPosition()
        item, flags = self.tree.HitTest(pt)
        if item:
            parent = self.tree.GetItemParent(item)
            print "\tparent: ", parent
            obj = self.tree.GetPyData(parent)
            print "\tobj: ", obj
            if hasattr(obj, "compareFunction"):
                self.tree.SortChildrenByFunction(parent, obj.compareFunction)
    
    def onTreeSelect(self, event):
        self.item = event.GetItem()
        if self.item:
            print "OnSelChanged: %s" % self.tree.GetItemText(self.item)
            #self.tree.SetItemBackgroundColour(self.item, 'RED')
            panel = self.tree.GetPyData(self.item).generateEditPanel(self.splitter)
            self.splitter.ReplaceWindow(self.cp_right, panel)
            self.cp_right.Destroy()
            self.cp_right = panel
            self.Refresh()
            self.Update()
        event.Skip()

