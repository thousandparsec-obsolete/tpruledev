"""
EditorFrame.py
 Skeleton for the RDE. Will eventually evolve into the actual
 editor, but for the time being will serve as a testbed.
"""

import wx, os, ConfigParser
from ConfigParser import ConfigParser

import RDE
import core.ObjectManagement

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
        
        #initialize odbase and gui components
        self.object_database = core.ObjectManagement.ObjectDatabase()
        self.initGUI()
        self.object_database.addODBListener(self.tree)

        #load the object nodes to fill the tree
        self.object_database.loadObjectNodes()
        self.curr_node_id = None
        self.Show(True)

    def initGUI(self):
        self.splitter = wx.SplitterWindow(self, SPLITTER_ID,
                                          style=wx.SP_NO_XP_THEME |
                                          wx.SP_3DSASH | wx.BORDER |
                                          wx.SP_3D)
        self.cp_right = wx.Panel(self.splitter, wx.ID_ANY)
        self.cp_right.SetBackgroundColour("black")
        
        self.tree = core.ObjectManagement.GameObjectTree(self.splitter, wx.ID_ANY)
        self.tree.SetObjectDatabase(self.object_database)
	    #self.tree = self.object_database.getTree(self.splitter)
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
        self.curr_node_id = event.GetItem()
        if self.curr_node_id:
            print "OnSelChanged: %s" % self.tree.GetItemText(self.curr_node_id)
            
            #cleanup the last panel, which will release resources
            # grabbed by objects if applicable
            #this will also clear any highlighting done by the
            # panel and stuff like that
            try:
                self.cp_right.cleanup()
            except AttributeError:
                #no biggie, just doesn't have a cleanup method
                pass
                
            #generate the new panel and do highlighting and stuff like that
            # (all handled by the generateEditPanel method)
            panel = self.tree.GetPyData(self.curr_node_id).generateEditPanel(self.splitter)
            self.splitter.ReplaceWindow(self.cp_right, panel)
            
            #destroy the old panel and refresh everything
            self.cp_right.Destroy()
            self.cp_right = panel
            self.Refresh()
            self.Update()
            
        event.Skip()

