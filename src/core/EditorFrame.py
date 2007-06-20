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

def GenCreateNewObjHandler(type, frame):
    def f(event):
        obj_name = wx.GetTextFromUser('Enter the name of the new ' + type + ':', 'Input Object Name')
        if obj_name == '':
            #cancel
            pass
        else:
            #add the object to the database
            # it should take care of the rest
            # don't handle errors yet
            frame.object_database.Add(type, obj_name)
        event.Skip()
    return f

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
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelect)
        
        self.splitter.SetMinimumPaneSize(140)
        self.splitter.SplitVertically(self.tree,
                                      self.cp_right,
                                      150)
        #give ourselves a status bar because we'll be needing it in the near future
        self.CreateStatusBar()
        self.SetMenuBar(self.initMenuBar())
                                      
    def initMenuBar(self):
        menubar = wx.MenuBar()
        
        #create and append the File menu
        file_menu = wx.Menu()
        new_proj_item = file_menu.Append(-1, 'New Project', 'Create a new TP Project')
        self.Bind(wx.EVT_MENU, self.OnNewProject, new_proj_item)
        open_proj_item = file_menu.Append(-1, 'Open Project', 'Open an existing TP Project')
        save_proj_item = file_menu.Append(-1, 'Save Project', 'Save the current TP Project')
        file_menu.AppendSeparator()
        quit_item = file_menu.Append(-1, 'Quit', 'Quit the Ruleset Development Evironment')
        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        menubar.Append(file_menu, 'File')
        
        #create and append the Edit menu
        edit_menu = wx.Menu()
        #create the items for creating new objects
        new_obj_menu = wx.Menu()
        self.obj_create_menu_items = {}
        for type in self.config.get('Object Types', 'types').split(', '):
            type = type.strip()
            id = new_obj_menu.Append(-1, type)
            self.obj_create_menu_items[type] = id
            self.Bind(wx.EVT_MENU, GenCreateNewObjHandler(type, self), id)
            
        new_object_item = edit_menu.AppendMenu(-1, 'Create New Object', new_obj_menu, 'Add an object to the project')
        del_object_item = edit_menu.Append(-1, 'Delete Object', 'Deletes the current object')
        ren_object_item = edit_menu.Append(-1, 'Rename Object', 'Deletes the current object')
        menubar.Append(edit_menu, 'Edit')
        
        return menubar
        
    def OnNewProject(self, event):
        proj_name = wx.GetTextFromUser('Enter the name of the ruleset:', 'Input Ruleset Name')
        if proj_name == '':
            print 'User cancelled new project...'
        else:
            print 'You wanted to create a project called: ', proj_name
            
    def OnCreateNewObject(self, event):
        print "event object: ", event.GetEventObject()
        pass
        
    def CreateNewProject(self, proj_name):
        pass
                                      
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
    
    def OnTreeSelect(self, event):
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
        
    def OnQuit(self, event):
        self.Close()
