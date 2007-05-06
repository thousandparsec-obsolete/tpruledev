import wx
import sys
sys.path.append("..")
Property = __import__("game_objects.Property", globals(), locals(), [''])

SPLITTER_ID = 101
TREE_ID = 110

class SplitterTest(wx.Frame):
    
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        self.splitter = wx.SplitterWindow(self, SPLITTER_ID,\
                                          style=wx.SP_NO_XP_THEME | wx.SP_3DSASH\
                                          | wx.BORDER | wx.SP_3D)
        self.cp_right = wx.Panel(self.splitter, wx.ID_ANY)
        self.cp_right.SetBackgroundColour("black")
        
        self.tree = wx.TreeCtrl(self.splitter, wx.ID_ANY)
        self.root = self.tree.AddRoot("The Root Item")
        self.buildTree(self.tree, self.root)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeSelect, self.tree)
        
        self.splitter.SetMinimumPaneSize(140)
        self.splitter.SplitVertically(self.tree,
                                      self.cp_right,
                                      150)
     
        self.Show(True)
        
    
    def buildTree(self, tree, root):
        tree.SetPyData(root, MyNode("Root"))
        prop_node = tree.AppendItem(root, "Property")
        tree.SetPyData(prop_node, MyNode("Property Node"))
        prop1 = Property.Object(catid = 1, prop_id = 1, rank = 1, name = 'TestProp',
            desc = 'Just a test property.', disp_text = 'Testing display text',
            tpcl_disp = '(lambda)', tpcl_req = '(lambda)')
        prop1_node = tree.AppendItem(prop_node, "Property 1")
        tree.SetPyData(prop1_node, prop1)
        
        for i in range(7):
            child = tree.AppendItem(root, "Item " + str(i))
            tree.SetPyData(child, MyNode("Item " + str(i)))
        return
    
    def onTreeSelect(self, event):
        self.item = event.GetItem()
        if self.item:
            print "OnSelChanged: %s" % self.tree.GetItemText(self.item)
            panel = self.tree.GetPyData(self.item).generateEditPanel(self.splitter)
            self.splitter.ReplaceWindow(self.cp_right, panel)
            self.cp_right.Destroy()
            self.cp_right = panel
            self.Refresh()
            self.Update()
        event.Skip()

        
class MyNode:
    def __init__(self, value):
        self.value = value
    
    def generateEditPanel(self, parent):
        print "Generating panel for [%s]" % self.value
        panel = wx.Panel(parent, wx.ID_ANY)
        panel.SetBackgroundColour('white')
        label = wx.StaticText(panel, wx.ID_ANY, "Test panel for value %s" % self.value)
        return panel
    
app = wx.PySimpleApp()
frame = SplitterTest(None, -1, 'Splitter Test')
app.MainLoop()
