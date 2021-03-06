"""\
The dialog class for the TPCL Expression Editor.
"""

import wx
import gui.XrcUtilities
from wx.xrc import XRCCTRL
import tpcl.IO
from tpcl.Representation import *
from gui.BlockInfoDialog import BlockInfoDialog

class EditorFrame(wx.Frame):
    """
    A wx.Panel for displaying and editing Categories
    """
    
    def __init__(self, parent, block_store, id=wx.ID_ANY, style=wx.EXPAND):
        #load from XRC, need to use two-stage create
        res = gui.XrcUtilities.XmlResource('./gui/xrc/TpclEditorFrame.xrc')
        pre = wx.PreFrame()
        res.LoadOnFrame(pre, parent, "editor")
        self.PostCreate(pre)        

        self.block_store = block_store
        self.OnCreate()
    
    def OnCreate(self):
        self.SetSize((600, 400))
        
        #widgets
        self.code_stc = XRCCTRL(self, "code_stc")
        self.code_stc.Bind(wx.EVT_LEFT_UP, self.ContextMenuHandler)
        self.block_tree = XRCCTRL(self, "block_tree")
        self.block_tree.SetBlockstore(self.block_store)
        self.preview_ctrl = XRCCTRL(self, "preview_ctrl")
        self.block_tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectionChanged)
        
        #buttons
        self.clear_button = XRCCTRL(self, "clear_button")
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.clear_button)
        self.remove_button = XRCCTRL(self, "remove_button")
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.remove_button)
        self.save_button = XRCCTRL(self, "save_button")
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.save_button)
        self.info_button = XRCCTRL(self, "info_button")
        self.Bind(wx.EVT_BUTTON, self.OnInfo, self.info_button)
                
        #fill the block_tree
        #tpcl.IO.LoadBlockIntoTree(self.block_tree)
        self.root_expression = None
        
        self.CreateQuickInsertMenu()
        
    def CreateQuickInsertMenu(self):
        self.quick_insert_menu = wx.Menu()
        submenus = ["Procedure Definitions", "Literal Expression", "Numerical Functions", "Flow Control"]
        for sm in submenus:
            cat_id = self.block_store.FindCategory(sm)
            smenu = wx.Menu()
            for child_id in self.block_store.GetChildBlocks(cat_id):
                node = self.block_store.GetNode(child_id)
                mitem = smenu.Append(wx.ID_ANY, node.name)
                self.Bind(wx.EVT_MENU, MakeInserter(self, node.block), mitem)
            self.quick_insert_menu.AppendMenu(wx.ID_ANY, sm, smenu)
        
    def OnInfo(self, event):
        """\
        Opens a dialog without a parent for the moment
        """
        sel_id = self.block_tree.GetSelection()
        if sel_id.IsOk():
            block = self.block_tree.GetPyData(sel_id)
            if block:
                info_dialog = BlockInfoDialog(self, block.name, block.display, block.description)
                info_dialog.ShowModal()
        event.Skip()
        
    def OnClear(self, event):
        """\
        Clears the code window, deleting all unsaved
        changes.
        """
        self.code_stc.ClearAll()
        #for now we'll put the root expression back in place
        self.root_expression = None
        event.Skip()
    
    def OnRemove(self, event):
        """\
        Removes the current tpcl code block that is
        selected.
        """
        pos = self.code_stc.GetCurrentPos()
        try:
            self.root_expression.RemoveExpression(pos)
            self.code_stc.SetText(str(self.root_expression))
        except ValueError:
            #text in top level expression, get rid of it
            self.root_expression = None
            self.code_stc.ClearAll()
        event.Skip()
    
    def OnSave(self, event):
        """\
        Saves the current work.
        """
        event.Skip()
        
    def OnSelectionChanged(self, event):
        """\
        Selection change in the block tree
        We need to fill the preview control here
        """
        print "Handling selection changed event."
        sel_id = self.block_tree.GetSelection()
        if sel_id.IsOk():
            block = self.block_tree.GetPyData(sel_id)
            if block:
                self.preview_ctrl.SetValue(block.display)
            else:
                self.preview_ctrl.SetValue("")
        else:
            self.preview_ctrl.SetValue("")
        event.Skip()
    
    def OnInsert(self, event, block=None):
        """\
        Inserts the currently selected code block
        into the currently selected code socket.
        """
        pos = self.code_stc.GetCurrentPos()

        if not block:
            sel_id = self.block_tree.GetSelection()
            if sel_id.IsOk():
                block = self.block_tree.GetPyData(sel_id)
                    
        if block:
            print "Trying to insert block..."
            try:
                #provide the OnInsert function of the block
                # access to us as a parent frame for when they
                # need to show a dialog
                parent_frame = self
                
                expression = TpclExpression(block)
                insert_ok = True
                if block.on_insert:
                    print "Trying to use OnInsert function of block"
                    exec(block.on_insert)
                    insert_ok = OnInsert(expression)
                
                if insert_ok:    
                    if not self.root_expression:
                        self.root_expression = expression                        
                    else:
                        self.root_expression.InsertExpression(pos, expression)                        
                    self.code_stc.SetText(str(self.root_expression))
                    
            except ValueError:
                print "Tried to insert in a place where there's no expansion point"
        event.Skip()

    def ContextMenuHandler(self, event):
        """\
        Processes a left click on the STC
        """
        event.Skip()
        print "Trying to show context menu at pos:", self.code_stc.GetCurrentPos()
        try:
            if wx.GetMouseState().ControlDown():
                print "Trying to show popup menu..."
                menu = wx.Menu()
                
                offset = self.code_stc.GetCurrentPos()
                            
                if not self.root_expression:
                    is_insertion_point = True
                    is_added_insertion_point = False
                    is_expansion_point = False
                else:
                    is_insertion_point = self.root_expression.IsInsertionPoint(offset)[0]
                    is_added_insertion_point = self.root_expression.IsAddedInsertionPoint(offset)[0]
                    is_expansion_point = self.root_expression.IsExpansionPoint(offset)[0]
                    
                print "is_insertion_point", is_insertion_point
                print "is_expansion_point", is_expansion_point
                    
                sel_id = self.block_tree.GetSelection()
                if sel_id.IsOk():
                    block = self.block_tree.GetPyData(sel_id)
                else:
                    block = None
                
                #insert item
                insert_item = menu.Append(wx.ID_ANY, "Insert")
                self.Bind(wx.EVT_MENU, self.OnInsert, insert_item)
                #only enable if we're on an expansion point
                insert_item.Enable(block != None and is_insertion_point)
                
                #quick insert
                quick_insert = menu.AppendMenu(wx.ID_ANY, "Quick Insert...", self.quick_insert_menu)
                quick_insert.Enable(is_insertion_point)
                    
                #remove item
                remove_item = menu.Append(wx.ID_ANY, "Remove")
                self.Bind(wx.EVT_MENU, self.OnRemove, remove_item)
                remove_item.Enable((not is_insertion_point and not is_expansion_point) or is_added_insertion_point)
                
                #check for expansion menu
                if is_expansion_point:
                    exp_menu = wx.Menu()
                    i = 0
                    for option in self.root_expression.GetExpansionOptions(offset):
                        opt_item = exp_menu.Append(wx.ID_ANY, option)
                        self.Bind(wx.EVT_MENU, MakeExpander(self, offset, i), opt_item)
                        i += 1
                    menu.AppendMenu(wx.ID_ANY, "Expansion Point...", exp_menu)
                
                self.code_stc.PopupMenu(menu, event.GetPosition())
                
        except ValueError:
            print "Index out of range..."
            
    def ShowModal(self):
        print "TPCLEE Showing itself Modally"
        self.MakeModal(True)
        self.old_top_window = wx.GetApp().GetTopWindow()
        wx.GetApp().SetTopWindow(self)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Show(True)        
    
    def OnClose(self, event):
        self.MakeModal(False)
        self.Unbind(wx.EVT_CLOSE)
        wx.GetApp().SetTopWindow(self.old_top_window)
        event.Skip()
            
def MakeInserter(tpcl_editor, block):
    def f(event):
        tpcl_editor.OnInsert(event, block)
    return f

def MakeExpander(tpcl_editor, offset, option):
    def f(event):
        tpcl_editor.root_expression.Expand(offset, option)
        tpcl_editor.code_stc.SetText(str(tpcl_editor.root_expression))
    return f