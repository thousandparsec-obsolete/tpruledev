import wx

class EditPanel(wx.Panel):
    """\
    Panel that will load and track the various editing panels for different object types
    and fill and show the appropriate panel when given an object to display.
    """    
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent, id)
        
        #make our sizer
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.edit_panels = {}
        self.SetContentPanel(wx.Panel(self))
    
    def SetContentPanel(self, panel):
        self.content_panel = panel
        self.sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 5)
        self.Layout()
        
    def ReloadPanel(self):
        self.node = self.node
    
    def node_get(self):
        return self.__node
    
    def node_set(self, value):
        self.__node = value
        
        #cleanup after the old object
        self.content_panel.Hide()
        if hasattr(self.content_panel, "cleanup"): self.content_panel.cleanup()
        self.sizer.Remove(self.content_panel)
        
        if hasattr(value, "object_module"):
            type = value.object_module.GetName()
            #if we haven't already loaded a panel for it, let's load a panel for it
            if not self.edit_panels.has_key(type):
                panel_module = __import__("gui." + type + "Panel", globals(), locals(), [''])
                self.edit_panels[type] = panel_module.Panel(self)
            #now fill the panel and set it as our content panel
            print "Loading %s" % self.node.name
            self.SetContentPanel(self.edit_panels[type].LoadObject(self.node))
        else:
            self.SetContentPanel(wx.Panel(self))
            
    #our current node, when we change it we also update the edit panel
    # and clean up after the last one
    node = property(node_get, node_set)
                