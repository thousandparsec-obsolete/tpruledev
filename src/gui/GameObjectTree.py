import wx
from rde import ObjectManagement, Nodes

class GameObjectTree(wx.TreeCtrl):
    """
    The default display for game objects. Based on
    a wx.TreeCtrl
    """
    
    def __init__(self, parent, id=-1, object_database = None, pos=wx.DefaultPosition, size=wx.DefaultSize,
                    style=wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_SINGLE , validator=wx.DefaultValidator,
                    name=wx.TreeCtrlNameStr):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        self.odb = object_database
        self.root_id = self.AddRoot('RDE')
        #self.SetPyData(self.root_id, RDE)
        
    def SetObjectDatabase(self, odb):
        self.odb = odb
        odb.addODBListener(self)
             
    def SelectObject(self, name):
        try:
            self.SelectItem(self.object_ids[name])
            return True
        except KeyError:
            #no such object
            return False
        
    def handleODBEvent(self, event):
        self.eventDict[event.type](self, event)
        
    def HandleInit(self, event):
        self.InitializeTree()
    
    def HandleAdd(self, event):
        type_id = self.type_ids[event.obj_type]
        new_id = None
        
        if event.preceding == None:
            #node belongs at the beginning of the list of objects
            new_id = self.PrependItem(type_id, event.node.name)
        else:
            preceding_id = self.object_ids[event.preceding]
            new_id = self.InsertItem(type_id, preceding_id, event.node.name)

        #make sure we give the new object some PyData and add it to the
        # treeid hash for objects
        self.object_ids[event.node.name] = new_id
        self.SetPyData(new_id, event.node)
        if not self.IsExpanded(type_id): self.Expand(type_id)
        self.Refresh()
    
    def HandleRemove(self, event):
        obj_id = self.object_ids[event.name]
        self.Delete(obj_id)
        self.Refresh()
    
    def HandleModify(self, event):
        pass
    
    def HandleHighlight(self, event):
        """\
        highlights the given objects in the tree
        objects is a hash with keys that are the object types
        and values of object names to highlight
        """
        #todo: error handling
        for obj_name in event.names:
            id = self.object_ids[obj_name]
            self.SetItemBackgroundColour(id, event.color)
        self.Refresh()
    
    def HandleUnHighlight(self, event):
        for obj_name in event.names:
            id = self.object_ids[obj_name]
            self.SetItemBackgroundColour(id, 'WHITE')
        self.Refresh()
    
    def HandleClear(self, event):
        """\
        clears all highlighting from objects in the tree
        """
        for name in self.odb.highlighted:
            id = self.object_ids[name]
            self.SetItemBackgroundColour(id, 'WHITE')
        for name in self.odb.emphasized:
            id = self.object_ids[name]
            self.SetItemTextColour(id, 'BLACK')
            self.SetItemBold(id, False)
        self.Refresh()
        
    def HandleEmphasize(self, event):
        """\
        highlights the given objects in the tree
        objects is a hash with keys that are the object types
        and values of object names to highlight
        """
        #todo: error handling
        for obj_name in event.names:
            id = self.object_ids[obj_name]
            self.SetItemTextColour(id, 'BLUE')
            self.SetItemBold(id, True)
        self.Refresh()
    
    def HandleUnEmphasize(self, event):
        for obj_name in event.names:
            id = self.object_ids[obj_name]
            self.SetItemTextColour(id, 'BLACK')
            self.SetItemBold(id, False)
        self.Refresh()
        
    def HandleMarkModified(self, event):
        """\
        puts an exlamation mark next to the given objects in the tree
        objects is a hash with keys that are the object types
        and values of object names to highlight
        """
        #todo: error handling
        for obj_name in event.names:
            id = self.object_ids[obj_name]
            self.SetItemImage(id, self.modimg_idx)
        self.Refresh()
    
    def HandleUnmarkModified(self, event):
        for obj_name in event.names:
            id = self.object_ids[obj_name]
            self.SetItemImage(id, self.noimg_idx)
        self.Refresh()
        
    def HandleUnInit(self, event):
        pass
        
    def InitializeTree(self):
        self.InitImageList()
        self.type_ids = {}
        self.object_ids = {}
        for object_type in self.odb.getObjectTypes():
            self.type_ids[object_type] = self.AppendItem(self.root_id, object_type)
            self.SetPyData(self.type_ids[object_type], self.odb.getObjectModule(object_type))
            for node in self.odb.getObjectsOfType(object_type):
                object_name = node.name
                self.object_ids[object_name] = self.AppendItem(self.type_ids[object_type], object_name)
                self.SetPyData(self.object_ids[object_name], node)
        
        #we want to have everything expanded at default
        self.ExpandAll()
        
        #we will blindly assume that there will always be some game object types included
        # else why would there be an editor for it, eh?
        #later we will save the last open object for a given project, but that's not now
        first_obj = self.type_ids[self.type_ids.keys()[0]]
        while  self.ItemHasChildren(first_obj):
            first_obj= self.GetFirstChild(first_obj)[0]
            
        self.SelectItem(first_obj)
        
    def InitImageList(self):
        il = wx.ImageList(6, 6)
        self.noimg_idx = il.Add(wx.BitmapFromImage(wx.Image('images/noimg.png', wx.BITMAP_TYPE_ANY)))
        self.modimg_idx = il.Add(wx.BitmapFromImage(wx.Image('images/modified.png', wx.BITMAP_TYPE_ANY)))
        print "Tree ImageList Indexes:"
        print "\tnoimg: ", self.noimg_idx
        print "\tmodimg: ", self.modimg_idx
        self.AssignImageList(il)
    
    #the following methods allow the tree to have its objects
    # sorted using external functions so that objects of a certain
    # type can supply a certain sorting function and be
    # sorted in that way
    def SortChildrenByFunction(self, item, func):
        """
        Sorts the children of item using the function func.
        """
        self.compare_function = func
        self.SortChildren(item)
        #default operation leaves ordering intact
        # so we make sure to set ourselves back to the default
        self.compare_function = lambda x, y: 0

    def OnCompareItems(self, item1, item2):
        """
        This particular OnCompareItems function passes the PyData objects of
        the nodes to be compared to the function provided as a comparison technique.
        """
        if self.compare_function:
            return self.compare_function(self.GetPyData(item1), self.GetPyData(item2))
        else:
            return 0
            
    def ExpandAllChildren(self, item):
        if self.IsVisible(item): self.Expand(item)
        
        child, cookie = self.GetFirstChild(item)
        while child.IsOk():
            self.Expand(child)
            if self.ItemHasChildren(child): self.ExpandAllChildren(child)
            child, cookie = self.GetNextChild(item, cookie)
    
    def ExpandAll(self):
        self.ExpandAllChildren(self.GetRootItem())
            
    eventDict = {ObjectManagement.ODBEvent.INIT: HandleInit,
                 ObjectManagement.ODBEvent.ADD: HandleAdd,
                 ObjectManagement.ODBEvent.REMOVE: HandleRemove,
                 ObjectManagement.ODBEvent.MODIFY: HandleModify,
                 ObjectManagement.ODBEvent.HIGHLIGHT: HandleHighlight,
                 ObjectManagement.ODBEvent.UNHIGHLIGHT: HandleUnHighlight,
                 ObjectManagement.ODBEvent.CLEAR_MARKERS: HandleClear,
                 ObjectManagement.ODBEvent.EMPHASIZE: HandleEmphasize,
                 ObjectManagement.ODBEvent.UNEMPHASIZE: HandleUnEmphasize,
                 ObjectManagement.ODBEvent.UNINIT: HandleUnInit,
                 ObjectManagement.ODBEvent.MARKMODIFIED: HandleMarkModified,
                 ObjectManagement.ODBEvent.UNMARKMODIFIED: HandleUnmarkModified}
