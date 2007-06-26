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
    project_active = False

    def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                 size=wx.DefaultSize):
        wx.Frame.__init__(self, parent, id, title, pos, size)
            
        #import configuration settings, will build on this as is necessary
        RDE.GlobalConfig.config = ConfigParser()
        self.config = RDE.GlobalConfig.config
        self.config.readfp(open(os.path.join(sys.path[0], 'tpconf')))
        
        #check to see if there's a current project that we can load
        self.initGUI()
        if self.config.has_option('DEFAULT', 'current_project'):
            self.initProjectGUI(self.config.get('DEFAULT', 'current_project'))
        else:
            self.initRDEInfo()
        
        self.Show(True)

    def initGUI(self):
        #initialize backbone of GUI
        self.content_panel = wx.Panel(self, wx.ID_ANY)
        self.active_panel = None
        self.content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        stretcher = wx.BoxSizer(wx.VERTICAL)
        stretcher.Add(self.content_sizer, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, 0)
        self.content_panel.SetSizer(stretcher)

        #create handy interface elements
        self.CreateStatusBar()
        self.SetMenuBar(self.initMenuBar())

        
    def clearGUI(self):
        if self.project_active:
            self.cleanupCurrentProject()
            
        self.active_panel = None
        for child in self.content_panel.GetChildren():
            child.Hide()
            self.content_sizer.Remove(child)
            child.Destroy()
            del child
                
    def initRDEInfo(self):
        self.clearGUI()
        self.project_active = False
        self.SetTitle("Thousand Parsec Ruleset Development Environment")
        self.active_panel = RDE.generateInfoPanel(self.content_panel)
        self.content_sizer.Add(self.active_panel, 1, wx.ALL | wx.EXPAND, 0)
        self.content_panel.Layout()
        
    def initProjectGUI(self, project_file):
        self.clearGUI()
        self.project_active = True
        
        #read in the project info
        self.config.read(project_file)
        self.SetTitle("TP-RDE: " + self.config.get('Current Project', 'project_name'))
        
        #initialize odbase and gui components
        self.object_database = core.ObjectManagement.ObjectDatabase()       
        
        self.splitter = wx.SplitterWindow(self.content_panel, SPLITTER_ID,
                                          style=wx.SP_NO_XP_THEME |
                                          wx.SP_3DSASH | wx.BORDER |
                                          wx.SP_3D)
        self.content_sizer.Add(self.splitter, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, 0)
        self.cp_right = wx.Panel(self.splitter, wx.ID_ANY)
        self.cp_right.SetBackgroundColour("black")
        
        self.tree = core.ObjectManagement.GameObjectTree(self.splitter, wx.ID_ANY)
        self.tree.SetObjectDatabase(self.object_database)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelect)
        
        self.splitter.SetMinimumPaneSize(140)
        self.splitter.SplitVertically(self.tree,
                                      self.cp_right,
                                      200)
                                      
        self.object_database.loadObjectNodes()
        self.curr_node_id = None
        self.content_panel.Layout()
        
    def cleanupCurrentProject(self):
        del self.object_database
        for child in self.splitter.GetChildren():
            child.Hide()
            child.Destroy()
            del child
                                      
    def initMenuBar(self):
        menubar = wx.MenuBar()
        
        #create and append the File menu
        file_menu = wx.Menu()
        new_proj_item = file_menu.Append(-1, 'New Project\tCtrl-n', 'Create a new TP Project')
        self.Bind(wx.EVT_MENU, self.OnNewProject, new_proj_item)
        open_proj_item = file_menu.Append(-1, 'Open Project\tCtrl-o', 'Open an existing TP Project')
        self.Bind(wx.EVT_MENU, self.OnOpenProject, open_proj_item)
        del_proj_item = file_menu.Append(-1, 'Delete Project', 'Delete the current TP Project')
        self.Bind(wx.EVT_MENU, self.OnDeleteProject, del_proj_item)
        save_proj_item = file_menu.Append(-1, 'Save Project\tCtrl-s', 'Save the current TP Project')
        self.Bind(wx.EVT_MENU, self.OnSaveProject, save_proj_item)
        file_menu.AppendSeparator()
        quit_item = file_menu.Append(-1, 'Quit\tCtrl-q', 'Quit the Ruleset Development Evironment')
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
                                                self.config.get('Object Types', 'types').split(', '))
                except DuplicateProjectError:
                    wx.MessageBox("A project with that name already exists in that location!",
                                  caption = "Duplicate Project Error", style=wx.OK)
            dir_dialog.Destroy()
            #switch to project
            self.initProjectGUI(os.path.join(dir_dialog.GetPath(), proj_name, 'tprde.cfg'))
            
    def OnOpenProject(self, event):
        #get project directory
        dir_dialog = wx.DirDialog(None, "Select the project directory:",
            style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dir_dialog.ShowModal() == wx.ID_OK:
            if 'tprde.cfg' in os.listdir(dir_dialog.GetPath()):
                self.initProjectGUI(os.path.join(dir_dialog.GetPath(), 'tprde.cfg'))
            else:
                x.MessageBox("You must select a valid TP-RDE Project Folder!",
                                  caption = "Invalid Project Folder!", style=wx.OK)
        else:
            return
            
    def OnSaveProject(self, event):
        self.object_database.SaveObjects()
            
    def OnDeleteProject(self, event):
        #confirm project deletion
        confirm = wx.MessageBox("Are you sure that you want to delete the current project?", caption="Confirm Project Deletion",
                    style=wx.OK | wx.CANCEL)
        if confirm == wx.OK:
            #todo: actually delete the project
            wx.MessageBox("Deletion confirmed...uhm...not actually doing anything yet...", caption="Deletion confirmed",
                style=wx.OK)
            
    def OnDeleteObject(self, event):
        if not self.project_active:
            wx.MessageBox("You must have an open porject to delete an object!",
                    caption="Invalid State", style=wx.OK)
            return
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
     
    def OnTreeSelect(self, event):
        self.curr_node_id = event.GetItem()
        if self.curr_node_id:
            print "OnSelChanged: %s" % self.tree.GetItemText(self.curr_node_id)
            
            #cleanup the last panel, which will release resources
            # grabbed by objects if applicable
            #this will also clear any highlighting done by the
            # panel and stuff like that
            if hasattr(self.cp_right, "cleanup"):
                self.cp_right.cleanup()
                
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