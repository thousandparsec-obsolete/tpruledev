"""
wx.Panel and associated methods for editing
a Component object
"""

import wx, wx.stc
from rde.Exceptions import NoSuchIDError
import gui.TextCtrl, gui.XrcUtilities
from wx.xrc import XmlResource, XRCCTRL

class Panel(wx.Panel):
    """
    A wx.Panel for displaying and editing Components
    """
        
    def __init__(self, parent, id=wx.ID_ANY, style=wx.EXPAND):
        #load from XRC, need to use two-stage create
        pre = wx.PrePanel()
        res = gui.XrcUtilities.XmlResource('./gui/xrc/ComponentPanel.xrc')
        res.LoadOnPanel(pre, parent, "ComponentPanel")
        self.PostCreate(pre)
        
        self.OnCreate()
        
    def OnCreate(self):
        self.name_field = XRCCTRL(self, "name_field")
        self.desc_field = XRCCTRL(self, "desc_field")
        self.tpcl_req_stc = XRCCTRL(self, "tpcl_req_stc")
        self.cat_choice = XRCCTRL(self, "cat_choice")
        self.prop_list = XRCCTRL(self, "prop_list")
        self.tpcl_cost_stc = XRCCTRL(self, "tpcl_cost_stc")
        self.tpcl_cost_stc.Bind(wx.EVT_KEY_UP, self.OnCostEdit)
        self.tpcl_cost_stc.Enable(False)
        add_button = XRCCTRL(self, "add_button")
        self.Bind(wx.EVT_BUTTON, self.OnAddProperty, add_button)        
        remove_button = XRCCTRL(self, "remove_button")
        self.Bind(wx.EVT_BUTTON, self.OnRemoveProperty, remove_button)
        
    def LoadObject(self, comp):
        self.component = comp
        self.component.node.visible = True
        
        self.name_field.SetLabel(str(self.component.name))
        self.desc_field.SetValue(str(self.component.description))
        self.tpcl_req_stc.SetText(self.component.tpcl_requirements)
        
        #fill the category choice box        
        self.cat_choice.Clear()
        self.cat_choice.Append("")
        catidx = 0
        for catnode in self.component.node.object_database.getObjectsOfType('Category'):
            idx = self.cat_choice.Append(catnode.name)                
            if self.component.category == catnode.name:
                catidx = idx
        self.cat_choice.Select(catidx)
        
        #create the property list        
        self.prop_sel = -1
        self.Bind(wx.EVT_LISTBOX, self.OnListBoxSelect, self.prop_list)
        prop_names = [pname for pname in self.component.properties.keys()]
        self.prop_list.Set(prop_names)
        self.component.node.object_database.Emphasize(prop_names, "BLUE")
        self.Show()
        return self        
        
    def OnDClickProperty(self, event):
        """\
        Should open a window to edit the TPCL cost function here.
        """
        pass
        
    def OnListBoxSelect(self, event):
        sel_idx = self.prop_list.GetSelection()
        if sel_idx != wx.NOT_FOUND:
            self.tpcl_cost_stc.Enable(True)
            self.prop_sel = sel_idx
            self.tpcl_cost_stc.SetText(self.component.properties[
                                            self.prop_list.GetString(sel_idx)])
    
    def OnCostEdit(self, event):
        """\
        Saves changes made to the TPCL cost functions
        """
        print "Handling a cost edit event!"
        idx = self.prop_list.GetSelection()
        if idx == wx.NOT_FOUND:
            pass
        else:
            if not event.GetKeyCode() == wx.WXK_CONTROL and not event.ControlDown():
                self.component.properties[self.prop_list.GetString(idx)] = \
                        self.tpcl_cost_stc.GetText()
                self.component.node.SetModified(True)
            event.Skip()
        
        
    def OnAddProperty(self, event):
        print "On Add Property"
        loose_props = filter(lambda x: not x in self.component.properties.keys(),
                             [n.name for n in self.component.node.object_database.getObjectsOfType('Property')])
        choice_diag = wx.MultiChoiceDialog(self, "Choose the Properties to add...",
                                            "Add Properties...", loose_props)
        choice_diag.ShowModal()
        if len(choice_diag.GetSelections()) > 0:
            print "Selection OK"
            for i in choice_diag.GetSelections():
                print "\t" + loose_props[i]
                self.component.properties[loose_props[i]] = "(lambda (design) #)"
                self.prop_list.Append(loose_props[i])
            self.component.node.SetModified(True)
        else:
            #cancelled
            print "CANCELED!"
            print "Selections: ", choice_diag.GetSelections()
            pass
        choice_diag.Destroy()
        
    def OnRemoveProperty(self, event):
        #remove the selected properties
        if self.prop_list.GetSelections() != []:
            ridx = []
            for idx in self.prop_list.GetSelections():
                prop_name = self.prop_list.GetString(idx)
                del self.component.properties[prop_name]
                ridx.insert(0, idx)
            for i in ridx:
                self.prop_list.Delete(i)
            self.tpcl_cost_stc.SetText("")
            self.component.node.SetModified(True)            
    
    def CheckForModification(self):
        #print "Checking for modification..."
        mod = False
        
        #print "\category_id: %s <> %s" % (self.component.category_id, self.catid_field.GetValue())
        if self.component.category != self.cat_choice.GetStringSelection():
            mod = True
            self.component.category = self.cat_choice.GetStringSelection()
        
        #print "\description: %s <> %s" % (self.component.description, self.desc_field.GetValue())
        if self.component.description != self.desc_field.GetValue():
            mod = True
            self.component.description = self.desc_field.GetValue()
            
        #print "\tpcl_requirements: %s <> %s" % (self.component.tpcl_requirements, self.tpcl_req_stc.GetText())
        if self.component.tpcl_requirements != self.tpcl_req_stc.GetText():
            mod = True
            self.component.tpcl_requirements = self.tpcl_req_stc.GetText()
        
        if mod:
            self.component.node.SetModified(True)
    
    def Destroy(self):
        self.Hide()
        
    def ReallyDestroy(self):
        wx.Panel.Destroy(self)
        
    def cleanup(self):
        print "Cleaning up Component Panel"
        self.CheckForModification()
        self.component.node.object_database.UnEmphasize(
            [self.prop_list.GetString(i) for i in range(0, self.prop_list.GetCount())])
        self.component.node.visible = False
        self.component.node.clearObject()