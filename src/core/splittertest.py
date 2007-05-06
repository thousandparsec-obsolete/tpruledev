import wx

SPLITTER_ID = 101
TREE_ID = 110

class SplitterTest(wx.Frame):
    
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        self.splitter = wx.SplitterWindow(self, SPLITTER_ID)
        self.cp_left = wx.Panel(self.splitter, wx.ID_ANY)
        self.cp_left.SetBackgroundColour("white")
        self.cp_right = wx.Panel(self.splitter, wx.ID_ANY)
        self.cp_right.SetBackgroundColour("black")
        
        self.tree = self.initTree(self.cp_left)
        self.root = self.tree.AddRoot("The Root Item")
        self.buildTree(self.tree, self.root)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeSelect, self.tree)
        
        self.splitter.SetMinimumPaneSize(140)
        self.splitter.SplitVertically(self.cp_left,
                                      self.cp_right,
                                      150)
        
        
        self.Show(True)
        
    """
    Installs a tree in the given parent window. Returns the tree.
        parent - the window that will the tree's parent
        TREE_ID - the id of the tree if we care
    """
    def initTree(self, parent, TREE_ID = wx.ID_ANY):
        tree = wx.TreeCtrl(parent, TREE_ID)
        vert_tree_sizer = wx.BoxSizer(wx.VERTICAL)
        vert_tree_sizer.Add(tree, 1, wx.EXPAND)
        horz_tree_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horz_tree_sizer.Add(vert_tree_sizer, 1, wx.EXPAND)
        parent.SetSizer(horz_tree_sizer)
        parent.SetAutoLayout(1)
        horz_tree_sizer.Fit(parent)
        return tree
    
    def buildTree(self, tree, root):
        child1 = tree.AppendItem(root, "Item 1")
        tree.SetPyData(child1, MyNode("Item 1"))
        
        child2 = tree.AppendItem(root, "Item 2")
        tree.SetPyData(child2, MyNode("Item 2"))
        return
    
    def onTreeSelect(self, event):
        self.item = event.GetItem()
        if self.item:
            print "OnSelChanged: %s\n" % self.tree.GetItemText(self.item)
            self.tree.GetPyData(self.item).generatePanel(self.cp_right)
        event.Skip()

        
class MyNode:
    def __init__(self, value):
        self.value = value
    
    def generatePanel(self, parent):
        panel = wx.Panel(parent, wx.ID_ANY)
        label = wx.StaticText(panel, -1, "Test panel for value %s" % self.value)
        vert_sizer = wx.BoxSizer(wx.VERTICAL)
        vert_sizer.Add(panel, 1, wx.EXPAND)
        horz_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horz_sizer.Add(vert_sizer, 1, wx.EXPAND)
        parent.SetSizer(horz_sizer)
        parent.SetAutoLayout(1)
        horz_sizer.Fit(parent)
        return panel
    
app = wx.PySimpleApp()
frame = SplitterTest(None, -1, 'Splitter Test')
frame.checkScope()
app.MainLoop()
