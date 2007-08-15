import wx, sys
from tpcl.BlockManagement import *

class TpclBlockTree(wx.TreeCtrl):
    """
    The default display for tpcl blocks. Based on
    a wx.TreeCtrl
    """
    
    def __init__(self, parent, id=-1, blockstore = None, pos=wx.DefaultPosition, size=wx.DefaultSize,
                    style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_SINGLE , validator=wx.DefaultValidator,
                    name=wx.TreeCtrlNameStr):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        self.id_map = {}
        self.bs = None
        if blockstore:
            self.SetBlockStore(blockstore)
        self.root_id = self.AddRoot('TPCL Blocks')
        
    def SetBlockstore(self, bs):
        if not self.bs:
            self.bs = bs
            bs.addBsListener(self)
            self.InitializeTree()
             
    def SelectObject(self, name):
        try:
            self.SelectItem(self.object_ids[name])
            return True
        except KeyError:
            #no such object
            return False
        
    def HandleBsEvent(self, event):
        self.eventDict[event.type](self, event)
        
    def HandleInit(self, event):
        self.InitializeTree()
    
    def HandleAdd(self, event):
        print "BST adding %d" % event.node_id
        obj_id = self.id_map[event.node_id]
        parent_id = self.id_map[event.parent_id]
        new_id = None
        
        node = self.bs.GetNode(event.node_id)
        new_id = self.AppendItem(parent_id, node.name)

        #make sure we give the new object some PyData and add it to the
        # treeid hash for objects
        self.id_map[event.node_id] = new_id
        if node.IsBlock():
            self.SetPyData(new_id, node.block)
        #if not self.IsExpanded(parent_id): self.Expand(parent_id)
        self.Refresh()
        
    def HandleInsert(self, event):
        print "BST inserting %d" % event.node_id
        obj_id = self.id_map[event.node_id]
        preceding_id = self.id_map[event.preceding_id]
        parent_id = self.id_map[self.bs.GetParent(event.preceding_id)]
        new_id = None
        
        node = self.bs.GetNode(event.node_id)
        new_id = self.InsertItem(parent_id, preceding_id, node.name)
        
        #make sure we give the new object some PyData and add it to the
        # treeid hash for objects
        self.id_map[event.node_id] = new_id
        if node.IsBlock():
            self.SetPyData(new_id, node.block)
    
    def HandleRemove(self, event):
        obj_id = self.object_ids[event.node_id]
        self.Delete(obj_id)
        
    def InitializeTree(self):
        self.catid_stack = [self.root_id]
        for bs_node in self.bs.iternodes():
            parent_id = self.catid_stack[-1]
            if bs_node.IsCategory():
                item_id = self.AppendItem(parent_id, bs_node.name)
                self.catid_stack.append(item_id)
            else:
                #it's a block
                item_id = self.AppendItem(parent_id, bs_node.name)
                self.SetPyData(item_id, node.block)
            self.id_map[bs_node.id] = item_id
        
        #we want to have everything expanded at default
        #self.ExpandAll()        
                    
    def ExpandAllChildren(self, item):
        if self.IsVisible(item): self.Expand(item)
        
        child, cookie = self.GetFirstChild(item)
        while child.IsOk():
            self.Expand(child)
            if self.ItemHasChildren(child): self.ExpandAllChildren(child)
            child, cookie = self.GetNextChild(item, cookie)
    
    def ExpandAll(self):
        self.ExpandAllChildren(self.GetRootItem())
            
    eventDict = {BSEvent.INIT: HandleInit,
                 BSEvent.ADD: HandleAdd,
                 BSEvent.INSERT: HandleInsert,
                 BSEvent.REMOVE: HandleRemove,
                 BSEvent.MODIFY: HandleModify,
