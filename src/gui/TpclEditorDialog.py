"""\
The dialog class for the TPCL Expression Editor.
"""

import wx
import gui.XrcUtilities
from wx.xrc import XRCCTRL
from tpcl.data import Import
from tpcl.Representation import *

class MyDialog(wx.Dialog):
    """
    A wx.Panel for displaying and editing Categories
    """
    
    def __init__(self, parent, id=wx.ID_ANY, style=wx.EXPAND):
        #load from XRC, need to use two-stage create
        res = gui.XrcUtilities.XmlResource('./gui/xrc/EditorDialog.xrc')
        pre = wx.PreDialog()
        res.LoadOnDialog(pre, parent, "editor")
        self.PostCreate(pre)        

        self.OnCreate()
    
    def OnCreate(self):
        self.SetSize((600, 400))
        self.blocks = Import.LoadBlocks()
        
        #widgets
        self.code_stc = XRCCTRL(self, "code_stc")
        self.code_stc.Bind(wx.EVT_LEFT_UP, self.ContextMenuHandler)
        self.block_tree = XRCCTRL(self, "block_tree")
        
        #buttons
        self.clear_button = XRCCTRL(self, "clear_button")
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.clear_button)
        self.remove_button = XRCCTRL(self, "remove_button")
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.remove_button)
        self.save_button = XRCCTRL(self, "save_button")
        
        #fill the block_tree
        Import.LoadBlockIntoTree(self.block_tree)
        
        #set the text of out code to a basic element
        self.root_expression = TpclExpression(self.blocks["INITIAL_BLOCK"]["Lambda Design"])
        self.code_stc.SetText(str(self.root_expression))
        
    def OnClear(self, event):
        """\
        Clears the code window, deleting all unsaved
        changes.
        """
        self.code_stc.ClearAll()
        #for now we'll put the root expression back in place
        self.root_expression = TpclExpression(self.blocks["INITIAL_BLOCK"]["Lambda Design"])
        self.code_stc.SetText(str(self.root_expression))
        pass
    
    def OnRemove(self, event):
        """\
        Removes the current tpcl code block that is
        selected.
        """
        pos = self.code_stc.GetCurrentPos()
        self.root_expression.RemoveExpression(pos)
        self.code_stc.SetText(str(self.root_expression))
        event.Skip()
    
    def OnSave(self, event):
        """\
        Saves the current work.
        """
        wx.MessageBox("You hit the save button!", caption = "OMG Save!", style=wx.OK)
        event.Skip()
        
    def OnPosChanged(self, event):
        """\
        Position changed, check to see if we should enable or disable
        the insert button
        """
        self.insert_button.Enable(self.root_expression.IsExpression(self.code_stc.GetCurrentPos()))
        event.Skip()
    
    def OnInsert(self, event):
        """\
        Inserts the currently selected code block
        into the currently selected code socket.
        """
        pos = self.code_stc.GetCurrentPos()
        sel_id = self.block_tree.GetSelection()
        if sel_id.IsOk():
            block = self.block_tree.GetPyData(sel_id)
            if block:
                try:
                    expression = TpclExpression(block)
                    self.root_expression.InsertExpression(pos, expression)
                    self.code_stc.SetText(str(self.root_expression))
                except ValueError:
                    print "Tried to insert in a place where there's no expansion point"
        event.Skip()

    def ContextMenuHandler(self, event):
        """\
        Processes a right click on the STC
        """
        event.Skip()
        print "Trying to show context menu at pos:", self.code_stc.GetCurrentPos()
        try:
            if self.root_expression.IsExpansionPoint(self.code_stc.GetCurrentPos())[0]:
                print "Trying to show popup menu..."
                menu = wx.Menu()
                insert_item = menu.Append(wx.ID_ANY, "Insert")
                self.Bind(wx.EVT_MENU, self.OnInsert, insert_item)
                sel_id = self.block_tree.GetSelection()
                if sel_id.IsOk():
                    block = self.block_tree.GetPyData(sel_id)
                    insert_item.Enable((block != None))
                
                self.code_stc.PopupMenu(menu, event.GetPosition())
        except ValueError:
            print "Index out of range..."
