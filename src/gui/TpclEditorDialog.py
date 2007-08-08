"""\
The dialog class for the TPCL Expression Editor.
"""

import wx
import gui.XrcUtilities
from wx.xrc import XRCCTRL
from tpcl.data import Import
from tpcl.Representation import *

class MyDialog(wx.Frame):
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
        
        #widgets
        self.code_stc = XRCCTRL(self, "code_stc")
        self.code_stc.Bind(wx.EVT_LEFT_UP, self.ContextMenuHandler)

        #buttons
        self.clear_button = XRCCTRL(self, "clear_button")
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.clear_button)
        self.remove_button = XRCCTRL(self, "remove_button")
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.remove_button)
        self.save_button = XRCCTRL(self, "save_button")
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.save_button)
        self.info_button = XRCCTRL(self, "info_button")
        self.Bind(wx.EVT_BUTTON, self.OnInfo, self.info_button)
                
        self.root_expression = None
        
    def OnInfo(self, event):
        """\
        Opens a dialog without a parent for the moment
        """
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
    
    def OnInsert(self, event):
        """\
        Inserts the currently selected code block
        into the currently selected code socket.
        """
        pos = self.code_stc.GetCurrentPos()

        block = MyPopup(self).ShowModal()

        if block:
            expression = TpclExpression(block)
            if not self.root_expression:
                self.root_expression = expression                        
            else:
                self.root_expression.InsertExpression(pos, expression)                        
            self.code_stc.SetText(str(self.root_expression))

        event.Skip()

    def ContextMenuHandler(self, event):
        """\
        Processes a right click on the STC
        """
        event.Skip()
        print "Trying to show context menu at pos:", self.code_stc.GetCurrentPos()
        try:
            print "Trying to show popup menu..."
            menu = wx.Menu()
            
            if not self.root_expression:
                is_expansion_point = True
            else:
                is_expansion_point = self.root_expression.IsExpansionPoint(self.code_stc.GetCurrentPos())[0]
            
            #insert item
            insert_item = menu.Append(wx.ID_ANY, "Insert")
            self.Bind(wx.EVT_MENU, self.OnInsert, insert_item)

            #only enable if we're on an expansion point
            insert_item.Enable(is_expansion_point)
                
            #remove item
            remove_item = menu.Append(wx.ID_ANY, "Remove")
            self.Bind(wx.EVT_MENU, self.OnRemove, remove_item)
            remove_item.Enable(not is_expansion_point)
            
            self.code_stc.PopupMenu(menu, event.GetPosition())
        except ValueError:
            print "Index out of range..."

class MyPopup(wx.Dialog):
    """
    A wx.Panel for displaying and editing Categories
    """
    
    def __init__(self, parent, id=wx.ID_ANY, style=wx.EXPAND):
        #load from XRC, need to use two-stage create
        res = gui.XrcUtilities.XmlResource('./gui/xrc/EditorPopup.xrc')
        pre = wx.PreDialog()
        res.LoadOnDialog(pre, parent, "editor")
        self.PostCreate(pre) 

        self.OnCreate()
    
    def OnCreate(self):
        print "OnCreate..."
        self.SetSize((600, 400))
        
        #widgets
        self.code_stc = XRCCTRL(self, "code_stc")

        self.block_tree = XRCCTRL(self, "block_tree")
        self.block_tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelect)
        
        #buttons
        self.insert_button = XRCCTRL(self, "insert_button")
        self.Bind(wx.EVT_BUTTON, self.OnInsert, self.insert_button)
        self.cancel_button = XRCCTRL(self, "cancel_button")
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel_button)

        #fill the block_tree
        Import.LoadBlockIntoTree(self.block_tree)

        print "End OnCreate..."
        
    def OnCancel(self, event):
        """\
        """
        self.block_tree.Unselect()
        self.Close()
 
    def OnInsert(self, event):
        """\
        Inserts the currently selected code block
        into the currently selected code socket.
        """
        self.Close()

    def Selected(self):
        sel_id = self.block_tree.GetSelection()
        if sel_id.IsOk():
            block = self.block_tree.GetPyData(sel_id)
            return block

    def OnTreeSelect(self, event):
        selected = self.Selected()
        if selected:
            # Update the scheme box
            self.code_stc.SetText(str(TpclExpression(selected)))

            # Update the info box

        event.Skip()

    def ShowModal(self):
        wx.Dialog.ShowModal(self)
        return self.Selected()

