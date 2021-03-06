"""
EditorFrame.py
 Skeleton for the RDE. Will eventually evolve into the actual
 editor, but for the time being will serve as a testbed.
"""

import wx, os, ConfigParser, sys
from ConfigParser import ConfigParser

import RDE
from rde import ConfigManager
import rde.ObjectManagement, rde.ProjectManagement
from gui import GameObjectTree, EditPanel
import game_objects.ObjectUtilities
from rde.Exceptions import *

import traceback

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
        self.right_clicking = False
            
        #import configuration settings, will build on this as is necessary
        ConfigManager.LoadRDEConfig('tpconf')
        
        #check to see if there's a current project that we can load
        self.initGUI()
        if ConfigManager.config.has_option('Global', 'current_project'):
            self.initProjectGUI(ConfigManager.config.get('Global', 'current_project'))
        else:
            self.initRDEInfo()
        
        self.Bind(wx.EVT_CLOSE, self.OnClosing)
        
        self.Show(True)

    def initGUI(self):
        #initialize backbone of GUI
        self.content_panel = wx.Panel(self, wx.ID_ANY)
        self.active_panel = None
        self.content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        stretcher = wx.BoxSizer(wx.VERTICAL)
        stretcher.Add(self.content_sizer, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, 0)
        self.content_panel.SetSizer(stretcher)
        
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightMouseDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightMouseUp)

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
        self.SaveCurrentProjectConfig()
        self.clearGUI()
        self.project_active = True
        self.curr_node_id = None
        
        #read in the project info
        if ConfigManager.config.has_section("Current Project"):
            ConfigManager.config.remove_section("Current Project")
        ConfigManager.config.set("Global", "current_project", project_file)
        ConfigManager.LoadProjectConfig(project_file)
        ConfigManager.AddToProjectHistory((ConfigManager.config.get('Current Project', 'project_name'),
                                          ConfigManager.config.get('Current Project', 'project_file')))
        self.UpdateRecentProjectMenu()
        self.SetTitle("TP-RDE: " + ConfigManager.config.get('Current Project', 'project_name'))
        
        #initialize odbase and gui components
        self.object_database = rde.ObjectManagement.ObjectDatabase()       
        
        self.splitter = wx.SplitterWindow(self.content_panel, SPLITTER_ID,
                                          style=wx.SP_NO_XP_THEME |
                                          wx.SP_3DSASH | wx.BORDER |
                                          wx.SP_3D)
        self.content_sizer.Add(self.splitter, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, 0)
        self.edit_panel = EditPanel.EditPanel(self.splitter)
        
        self.tree = GameObjectTree.GameObjectTree(self.splitter, wx.ID_ANY)
        self.tree.SetObjectDatabase(self.object_database)
        self.tree.Bind(wx.EVT_RIGHT_DOWN, self.OnRightMouseDown)
        self.tree.Bind(wx.EVT_RIGHT_UP, self.OnRightMouseUp)
        self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnTreeRightClick)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelect)
        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.OnTreeSelecting)
        
        
        self.splitter.SetMinimumPaneSize(140)
        self.splitter.SplitVertically(self.tree,
                                      self.edit_panel,
                                      200)
                                      
        self.object_database.loadObjectNodes()
        if ConfigManager.config.has_option("Current Project", "last_item"):
            self.tree.SelectObject(ConfigManager.config.get("Current Project", "last_item"))
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
        self.recent_project_menu = wx.Menu()
        self.UpdateRecentProjectMenu()
        file_menu.AppendMenu(-1, 'Open Recent...', self.recent_project_menu, 'Open a recently edited project')
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
        for type in ConfigManager.config.get('Object Types', 'types').split(', '):
            type = type.strip()
            id = new_obj_menu.Append(-1, type)
            self.obj_create_menu_items[type] = id
            self.Bind(wx.EVT_MENU, GenCreateNewObjHandler(type, self), id)
            
        new_object_item = edit_menu.AppendMenu(-1, 'Create New Object', new_obj_menu, 'Add an object to the project')
        del_object_item = edit_menu.Append(-1, 'Delete Object\tCtrl-d', 'Deletes the currently selected object')
        self.Bind(wx.EVT_MENU, self.OnDeleteObject, del_object_item)
        duplicate_object_item = edit_menu.Append(-1, 'Duplicate Object', 'Duplicates the current object into a new object, copying over the data')
        self.Bind(wx.EVT_MENU, self.OnDuplicateObject, duplicate_object_item)
        ren_object_item = edit_menu.Append(-1, 'Rename Object', 'Renames the currently object')
        self.Bind(wx.EVT_MENU, self.OnRenameObject, ren_object_item)
        menubar.Append(edit_menu, 'Edit')
        
        #create and append the Project menu
        project_menu = wx.Menu()
        validate_item = project_menu.Append(-1, 'Validate Project', 'Checks each object in the project for errors...')
        self.Bind(wx.EVT_MENU, self.OnValidateProject, validate_item)
        gen_code_item = project_menu.Append(-1, 'Generate Code', 'Generates C++ code for the project')
        self.Bind(wx.EVT_MENU, self.OnGenCode, gen_code_item)
        menubar.Append(project_menu, 'Project')
        
        #disabled items
        #menubar.Enable(gen_code_item.GetId(), False)
        
        return menubar
        
    def UpdateRecentProjectMenu(self):
        for mi in self.recent_project_menu.GetMenuItems():
            self.recent_project_menu.Remove(mi.GetId())
        project_history = ConfigManager.GetProjectHistory()
        if  project_history != []:
            for name, proj_file in project_history:
                mitem = self.recent_project_menu.Append(-1, name, proj_file)
                self.Bind(wx.EVT_MENU, self.OnOpenRecentProject, mitem)
    
    def OnOpenRecentProject(self, event):
        item = self.GetMenuBar().FindItemById(event.GetId())
        self.initProjectGUI(item.GetHelp())        
    
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
                    rde.ProjectManagement.createNewProject(dir_dialog.GetPath(), proj_name,
                                                ConfigManager.config.get('Object Types', 'types').split(', '))
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
            
    def OnGenCode(self, event):
        if self.object_database.pending_modifications:
            choice = wx.MessageBox("You have unsaved changes!\nYou cannot generate code without saving.",
                caption="Unsaved Changes", style = wx.OK)
            return
        elif not self.object_database.ValidateAllObjects():
            choice = wx.MessageBox("You have errors in your code!\nYou cannot generate code when errors are present!",
                caption="Errors Present", style = wx.OK)
            return
        else:
            #try:
            try:
                self.object_database.GenerateCode()
                wx.MessageBox("Code generated successfully.",
                                  caption = "Code Generation Complete", style=wx.OK)
            except Exception, e:
                print "Code Generation Error:", e.args
                wx.MessageBox("Code generation failed! Previous code files likely corrupted in the process.",
                                  caption = "Code Generation Error!", style=wx.OK)
        
            
    def OnSaveProject(self, event):
        #we may want to locate the checkformodification function
        # on the nodes...ionno.
        print "OnProjectSave"
        node = self.tree.GetPyData(self.tree.GetSelection())
        print "\topen object: %s" % node.name
        self.object_database.SaveObjects()
            
    def OnDeleteProject(self, event):
        #confirm project deletion
        confirm = wx.MessageBox("Are you sure that you want to delete the current project?", caption="Confirm Project Deletion",
                    style=wx.OK | wx.CANCEL)
        if confirm == wx.OK:
            #todo: actually delete the project
            wx.MessageBox("Deletion confirmed...uhm...not actually doing anything yet...", caption="Deletion confirmed",
                style=wx.OK)
    
    def OnRenameObject(self, event):
        if not self.project_active:
            wx.MessageBox("You must have an open porject to rename an object!",
                    caption="Invalid State", style=wx.OK)
            return
        try:
            data = self.tree.GetPyData(self.tree.GetSelection())
            if isinstance(data, game_objects.ObjectUtilities.ObjectNode):
                #get the new name
                new_name = wx.GetTextFromUser('Enter the new name:', 'Input New Name')
                if new_name == '':
                    #cancel
                    pass
                else:
                    self.object_database.RenameObject(data.object_module.GetName(), data.name, new_name.encode('ascii'))
            else:
                #tell the user he needs to select an object
                wx.MessageBox("Your selection was invalid! You must\nselect and object to rename.",
                    caption="Invalid Selection", style=wx.OK)
                    
        except wx._core.PyAssertionError:
            #there was no selection
            wx.MessageBox("Your selection was invalid!\nYou must select an object to delete.",
                caption="Invalid Selection", style=wx.OK)
    
    def OnDeleteObject(self, event):
        if not self.project_active:
            wx.MessageBox("You must have an open porject to delete an object!",
                    caption="Invalid State", style=wx.OK)
            return
        try:
            data = self.tree.GetPyData(self.tree.GetSelection())
            if isinstance(data, game_objects.ObjectUtilities.ObjectNode):
                #confirm the delete
                confirm = wx.MessageBox("Are you sure you want to delete the " + data.object_module.GetName() +
                                " " + data.name + "?", caption="Confirm Delete",
                                style=wx.OK | wx.CANCEL)
                if confirm == wx.OK:
                    #perform the delete
                    self.object_database.Remove(data.object_module.GetName(), data.name)
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
                
    def OnDuplicateObject(self, event):
        """\
        Duplicates the currently selected object.
        """
        if not self.project_active:
            wx.MessageBox("You must have an open porject to delete an object!",
                    caption="Invalid State", style=wx.OK)
            return
        try:
            node = self.tree.GetPyData(self.tree.GetSelection())
            #get the new name
            new_obj_name = wx.GetTextFromUser("Enter the new object's name:", 'Input Object Name')
            if new_obj_name == '':
                #cancel
                pass
            else:
                self.object_database.DuplicateObject(node, new_obj_name.encode('ascii'))
        except wx._core.PyAssertionError:
            #there was no selection
            wx.MessageBox("Your selection was invalid!\nYou must select an object to delete.",
                caption="Invalid Selection", style=wx.OK)
                
    def OnValidateProject(self, event):
        """\
        Checks all of the game objects for errors.
        """
        if self.object_database.ValidateAllObjects():
            wx.MessageBox("No errors were found in your project.",
                caption="Project Valid", style=wx.OK)
        else:
            wx.MessageBox("Errors were found in your project!",
                caption="Project Invalid", style=wx.OK)
        self.edit_panel.ReloadPanel()
    
    def OnRightMouseDown(self, event):
        print "Marking right mouse down as true"
        self.right_clicking = True
        event.Skip()
        
    def OnRightMouseUp(self, event):
        print "Marking right mouse down as false"
        self.right_clicking = False
        event.Skip()
    
    def OnTreeRightClick(self, event):
        """\
        Respond to a right click by the user
        We want to generate and display a popup context menu if
        the user clicked on a game object in the game object tree.
        """
        print "Handling tree right click."
        event.Skip()
    
    def OnTreeSelecting(self, event):
        """\
        Called when the selection on the tree is changing. We only
        want to allow game objects to be selected.
        """
        #print "*********************************************************"
        #print "OnTreeSelecting: Where the hell are we being called from?"
        #print "Stack:"
        #traceback.print_stack(limit=15, file=sys.stdout)
        #print "*********************************************************"
        print "Handling Tree Selection change"
        itemid = event.GetItem()
        if self.right_clicking:
            print "Vetoing selection change because we're right clicking"
            event.Veto()
        elif itemid.IsOk():
            pydata = self.tree.GetPyData(event.GetItem())
            if pydata == None:
                print "Vetoing selection change because there is no pydata"
                event.Veto()
            elif not isinstance(pydata, game_objects.ObjectUtilities.ObjectNode):
                print "Vetoing selection change because the selection is not a game object"
                print "Tried to select:", self.tree.GetItemText(itemid)
                event.Veto()
        else:
            print "Vetoing selection change because item id is not ok"
            event.Veto()
        event.Skip()
    
    def OnTreeSelect(self, event):
        print "OnTreeSelect"
        try:
            if event.GetItem().IsOk():
                self.edit_panel.node = self.tree.GetPyData(event.GetItem())                
            event.Skip()
        except wx.PyDeadObjectError:
            #the app is closing
            pass
            
    def OnClosing(self, event):
        #we want to save config information now
        ConfigManager.WriteRDEConfig("tpconf")
        self.SaveCurrentProjectConfig()
        self.Destroy()
        event.Skip()
    
    def SaveCurrentProjectConfig(self):
        """\
        Save the current project's configuration (things such as the
        currently viewed object and the like
        """
        if self.project_active:
            sel_id = self.tree.GetSelection()
            if sel_id.IsOk():
                ConfigManager.config.set("Current Project", "last_item", self.tree.GetItemText(sel_id))
            else:
                ConfigManager.config.remove_option("Current Project", "last_item")
            ConfigManager.WriteProjectConfig(ConfigManager.config.get("Global", "current_project"))
        
    def OnQuit(self, event):
        if self.object_database.pending_modifications:
            choice = wx.MessageBox("You have unsaved changes!\nAre you sure you want to quit?",
                caption="Confirm Quit", style = wx.YES_NO)
            if choice == wx.YES:
                self.Close()
            else:
                return
        self.Close()