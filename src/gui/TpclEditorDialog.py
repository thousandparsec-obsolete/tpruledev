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
        self.blocks = Import.LoadBlocks()
        
        #widgets
        self.code_stc = XRCCTRL(self, "code_stc")
        self.block_tree = XRCCTRL(self, "block_tree")
        
        #buttons
        self.clear_butt = XRCCTRL(self, "clear_button")
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.clear_butt)
        self.remove_butt = XRCCTRL(self, "remove_button")
        #self.Bind(wx.EVT_BUTTON, self.OnRemove, self.remove_butt)
        self.save_butt = XRCCTRL(self, "save_button")
        self.insert_butt = XRCCTRL(self, "insert_button")
        self.Bind(wx.EVT_BUTTON, self.OnInsert, self.insert_butt)
        
        #fill the block_tree
        Import.LoadBlockIntoTree(self.block_tree)
        
        #set the text of out code to a basic element
        self.root_expression = TpclExpression(self.blocks["INITIAL_BLOCK"]["Lambda Design"])
        self.code_stc.SetText(str(self.root_expression))
        
    def OnTypeChoice(self, event):
        """\
        Handles a selection of a particular type
        of TPCL code.
        
        We need to fill the block list with the correct
        blocks of code.
        """
        print "Processing choice event..."
        type_name = self.type_choice.GetStringSelection()
        self.block_list.Clear()
        for name in self.blocks[type_name].keys():
            self.block_list.Append(name)
        event.Skip()
        
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
                expression = TpclExpression(block)
                self.root_expression.InsertExpression(pos, expression)
                self.code_stc.SetText(str(self.root_expression))
        event.Skip()