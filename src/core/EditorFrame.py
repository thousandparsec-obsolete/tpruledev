"""
EditorFrame.py
 Skeleton for the RDE. Will eventually evolve into the actual
 editor, but for the time being will serve as a testbed.
"""

import wx, os, ConfigParser, sys
from ConfigParser import ConfigParser

import RDE
import core.ObjectManagement, core.ProjectManagement
import game_objects.ObjectUtilities
from core.Exceptions import *

SPLITTER_ID = 101

def GenCreateNewObjHandler(type, frame):
    """\
    Generates a function to handle the creation of a specific object type. This is
    in lieu of creating a custom event to carry the type information.
    """
    def f(event):
        obj_name = wx.GetTextFromUser('Enter the name of the new ' + type + ':', 'Input Object Name')
        if obj_name == '':
            #cancel
            pass
        else:
            #add the object to the database
            # it should take care of the rest
            # don't handle errors yet
            try:
                frame.object_database.Add(type, obj_name.encode('ascii'))
            except DuplicateObjectError:
                #there's already a game object with that name
                wx.MessageBox("A game object already exists with that name!\nPlease use a different name.",
                    caption="Duplicate Name", style=wx.OK)
            except NoSuchTypeError:
                #this should never happen, but...perhaps it could, eh?
                wx.MessageBox("Contact the author - " + type +  " is not an object type!",
                    caption="Invalid Type", style=wx.OK)
        event.Skip()
    return f

class Frame(wx.Frame):
    def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                 size=wx.DefaultSize):
        wx.Frame.__init__(self, parent, id, title, pos, size)
        #self.content_panel = wx.Panel(self, wx.ID_ANY)
        #self.active_panel = None
        #self.content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #stretcher = wx.BoxSizer(wx.VERTICAL)
        #stretcher.Add(self.content_sizer, 1, wx.ALL | wx.EXPAND, 0)
        #self.content_panel.SetSizer(stretcher)
            
        #import configuration settings, will build on this as is necessary
        RDE.GlobalConfig.config = ConfigParser()
        self.config = RDE.GlobalConfig.config
        self.config.readfp(open(os.path.join(sys.path[0], 'tpconf')))
        
        #check to see if there's a current project that we can load
        #if self.config.has_option('DEFAULT', 'current_project'):
        #    self.config.read(self.config.get('DEFAULT', 'current_project'))
        #    self.SetTitle("TP-RDE: " + self.config.get('Current Project', 'project_name'))                
        #else:
        
        self.config.read(self.config.get('DEFAULT', 'current_project'))
        self.SetTitle("TP-RDE: " + self.config.get('Current Project', 'project_name'))            
        
        #initialize odbase and gui components
        self.object_database = core.ObjectManagement.ObjectDatabase()
        self.initGUI()

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
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelect)
        
        self.splitter.SetMinimumPaneSize(140)
        self.splitter.SplitVertically(self.tree,
                                      self.cp_right,
                                      200)

        self.CreateStatusBar()
        self.SetMenuBar(self.initMenuBar())
    
    def initProjectGUI(self):
        pass
        
        
    def initNoProjectGUI(self):
        if self.active_panel != None:
            self.active_panel.Hide()
            self.content_sizer.Remove(self.active_panel)
            
        self.active_panel = RDE.generateInfoPanel(self.content_panel)
        self.content_size.Add(self.active_panel)
        #self.content_panel.
                                      
    def initMenuBar(self):
        menubar = wx.MenuBar()
        
        #create and append the File menu
        file_menu = wx.Menu()
        new_proj_item = file_menu.Append(-1, 'New Project', 'Create a new TP Project')
        self.Bind(wx.EVT_MENU, self.OnNewProject, new_proj_item)
        open_proj_item = file_menu.Append(-1, 'Open Project', 'Open an existing TP Project')
        del_proj_item = file_menu.Append(-1, 'Delete Project', 'Delete the current TP Project')
        self.Bind(wx.EVT_MENU, self.OnDeleteProject, del_proj_item)
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
        del_object_item = edit_menu.Append(-1, 'Delete Object', 'Deletes the currently selected object')
        self.Bind(wx.EVT_MENU, self.OnDeleteObject, del_object_item)
        ren_object_item = edit_menu.Append(-1, 'Rename Object', 'Renames the currently object')
        menubar.Append(edit_menu, 'Edit')
        
        #disable unused menu items
        #new_proj_item.Enable(False)
        open_proj_item.Enable(False)
        save_proj_item.Enable(False)
        
        ren_object_item.Enable(False)
        
        return menubar
        
    def OnNewProject(self, event):
        #get project name
        proj_name = wx.GetTextFromUser('Enter the name of the ruleset:', 'Input Ruleset Name')
        if proj_name == '':
            wx.MessageBox("No name was entered! No probject will be created!", caption="Project Creation Cancelled",
                style=wx.OK)
        else:
            #get project directory
            dir_dialog = wx.DirDialog(None, "Choose the directory in which\nto create the project folder:",
                style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
            if dir_dialog.ShowModal() == wx.ID_OK:
                try:
                    #create project dir and config
                    core.ProjectManagement.createNewProject(dir_dialog.GetPath(), proj_name,
                                                self.object_database.getObjectTypes())
                except DuplicateProjectError:
                    wx.MessageBox("A project with that name already exists in that location!",
                                  caption = "Duplicate Project Error", style=wx.OK)
            dir_dialog.Destroy()
            #switch to project
            
    def OnDeleteProject(self, event):
        #confirm project deletion
        confirm = wx.MessageBox("Are you sure that you want to delete the current project?", caption="Confirm Project Deletion",
                    style=wx.OK | wx.CANCEL)
        if confirm == wx.OK:
            #todo: actually delete the project
            wx.MessageBox("Deletion confirmed...uhm...not actually doing anything yet...", caption="Deletion confirmed",
                style=wx.OK)
            
    def OnDeleteObject(self, event):
        try:
            data = self.tree.GetPyData(self.tree.GetSelection())
            if isinstance(data, game_objects.ObjectUtilities.ObjectNode):
                #confirm the delete
                confirm = wx.MessageBox("Are you sure you want to delete the " + data.object_module.getName() +
                                " " + data.name + "?", caption="Confirm Delete",
                                style=wx.OK | wx.CANCEL)
                if confirm == wx.OK:
                    #perform the delete
                    self.object_database.Remove(data.object_module.getName(), data.name)
                else:
                    #user changed his mind
                    pass
            else:
                #tell the user he needs to select an object
                wx.MessageBox("Your selection was invalid! You must\nselect and object to delete.",
                    caption="Invalid Selection", style=wx.OK)
                    
        except wx._core.PyAssertionError:
            #there was no selection
            wx.MessageBox("Your selection was invalid!\nYou must select an object to delete.",
                caption="Invalid Selection", style=wx.OK)
            
    def SetCurrentProject(self, project_cfg):
        self.object_databse.Uninitialize()
        self.config.read(project_cfg)
        self.SetTitle("TP-RDE: " + self.config.get('Current Project', 'project_name'))
        self.object_database.loadObjectNodes()
        pass
    
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