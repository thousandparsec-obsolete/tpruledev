"""\
The dialog class for the TPCL Expression Editor.
"""

import wx
import gui.XrcUtilities
from wx.xrc import XRCCTRL
from tpcl.data import Import

class Dialog(wx.Dialog):
    """
    A wx.Panel for displaying and editing Categories
    """
    
    def __init__(self, parent, id=wx.ID_ANY, style=wx.EXPAND):
        #load from XRC, need to use two-stage create
        pre = wx.PreDialog()
        res = gui.XrcUtilities.XmlResource('./gui/xrc/EditorDialog.xrc')
        res.LoadOnDialog(pre, parent, "editor")
        self.PostCreate(pre)

        self.OnCreate()
    
    def OnCreate(self):
        self.blocktypes = Import.LoadBlocktypes()
        self.blocks = Import.LoadBlocks()
        
        #widgets
        self.code_stc = XRCCTRL(self, "code_stc")
        self.type_choice = XRCCTRL(self, "cat_choice")
        self.block_list = XRCCTRL(self, "block_list")
        self.code_stc = XRCCTRL(self, "code_stc")
        
        #buttons
        self.clear_butt = XRCCTRL(self, "clear_butt")
        self.remove_butt = XRCCTRL(self, "remove_butt")
        self.save_butt = XRCCTRL(self, "save_butt")
        self.insert_butt = XRCCTRL(self, "insert_butt")
        
        #fill the cat choice box with all blocktypes
        
    def OnTypeChoice(self, event):
        """\
        Handles a selection of a particular type
        of TPCL code.
        
        We need to fill the block list with the correct
        blocks of code.
        """
        
    def OnClear(self, event):
        """\
        Clears the code window, deleting all unsaved
        changes.
        """
        pass
    
    def OnRemove(self, event):
        """\
        Removes the current tpcl code block that is
        selected.
        """
        pass
    
    def OnSave(self, event):
        """\
        Saves the current work.
        """
        pass
    
    def OnInsert(self, event):
        """\
        Inserts the currently selected code block
        into the currently selected code socket.
        """
        pass