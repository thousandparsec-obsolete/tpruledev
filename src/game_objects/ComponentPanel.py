"""
wx.Panel and associated methods for editing
a Component object
"""

import wx
from core.Exceptions import NoSuchIDError
import gui.TextCtrl

class Panel(wx.Panel):
    """
    A wx.Panel for displaying and editing Components
    """
    
    def __init__(self, component, parent, id=wx.ID_ANY, style=wx.EXPAND):
        wx.Panel.__init__(self, parent, id, style=style)
        self.component = component
        flex_sizer = wx.FlexGridSizer(6, 2, 5, 5)
        flex_sizer.SetFlexibleDirection(wx.BOTH)
        
        name_label = self.createLabel("Name:")
        self.addLabelToFlex(flex_sizer, name_label)
        self.name_field = self.createField(str(component.name))
        self.addFieldToFlex(flex_sizer, self.name_field)

        comp_id_label = self.createLabel("Component ID:")
        self.addLabelToFlex(flex_sizer, comp_id_label)
        self.comp_id_field = self.createField(str(component.component_id))
        self.addFieldToFlex(flex_sizer, self.comp_id_field)

        category_id_label = self.createLabel("Category ID:")
        self.addLabelToFlex(flex_sizer, category_id_label)
        self.category_id_field = self.createField(str(component.category_id))
        self.addFieldToFlex(flex_sizer, self.category_id_field)

        desc_label = self.createLabel("Description:")
        self.addLabelToFlex(flex_sizer, desc_label)
        self.desc_field = self.createField(str(component.description))
        self.addFieldToFlex(flex_sizer, self.desc_field)

        tpcl_req_label = self.createLabel("TPCL Requirements Function:")
        self.addLabelToFlex(flex_sizer, tpcl_req_label)
        self.tpcl_req_stc = gui.TextCtrl.SchemeSTC(self, -1, str(component.tpcl_requirements))
        self.addFieldToFlex(flex_sizer, self.tpcl_req_stc)

        props_label = self.createLabel("Associated Properties:")
        self.addLabelToFlex(flex_sizer, props_label)
        #TODO make this into a ListCtrl?
        #TODO sort this list alphabetically
        self.prop_list = wx.ListBox(self, wx.ID_ANY, style=wx.LB_MULTIPLE | wx.LB_SORT)
        prop_add_button = wx.Button(self, wx.ID_ANY, "Add Property")
        self.Bind(wx.EVT_BUTTON, self.OnAddProperty, prop_add_button)
        prop_remove_button = wx.Button(self, wx.ID_ANY, "Remove Property")
        self.Bind(wx.EVT_BUTTON, self.OnRemoveProperty, prop_remove_button)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(prop_add_button)
        button_sizer.Add((5,5))
        button_sizer.Add(prop_remove_button)
        prop_sizer = wx.BoxSizer(wx.VERTICAL)
        prop_sizer.Add(self.prop_list, 1, wx.EXPAND | wx.ALL)
        prop_sizer.Add((5,5))
        prop_sizer.Add(button_sizer, flag = wx.ALIGN_RIGHT)
        prop_names = []
        #todo: fix order of display here
        for pname, tpcl_cost in component.properties.iteritems():
            prop_names.append(pname)
            self.prop_list.Insert(str(pname), 0)
        self.high_id = component.node.object_database.Emphasize(prop_names, "BLUE")
        self.addFieldToFlex(flex_sizer, prop_sizer)
       
        flex_sizer.AddGrowableCol(1) #field column
        flex_sizer.AddGrowableRow(4) #tpcl_requirements function
        flex_sizer.AddGrowableRow(5) #property list

        border1 = wx.BoxSizer(wx.HORIZONTAL)
        border1.Add(flex_sizer, 1, wx.ALL | wx.EXPAND, 5)
        border2 = wx.BoxSizer(wx.VERTICAL)
        border2.Add(border1, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(border2)
        
    def OnDClickProperty(self, event):
        pass
        
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
            self.component.properties = self.component.properties
        else:
            #cancelled
            print "CANCELED!"
            print "Selections: ", choice_diag.GetSelections()
            pass
        choice_diag.Destroy()
        
    def OnRemoveProperty(self, event):
        #remove the selected properties
        ridx = []
        for idx in self.prop_list.GetSelections():
            prop_name = self.prop_list.GetString(idx)
            del self.component.properties[prop_name]
            ridx.insert(0, idx)
        for i in ridx:
            self.prop_list.Delete(i)
        self.component.properties = self.component.properties
        
    def createLabel(self, text):
        return wx.StaticText(self, wx.ID_ANY, text, style=wx.ALIGN_RIGHT | wx.ALIGN_TOP)
    
    def addLabelToFlex(self, flex, label):
        flex.Add(label, 2, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.EXPAND, 5)

    def createField(self, text):
        return wx.TextCtrl(self, wx.ID_ANY, text)
        
    def addFieldToFlex(self, flex, field):
        flex.Add(field, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 5)
        
    def cleanup(self):
        print "Cleaning up Component Panel"
        self.component.node.object_database.UnEmphasize(self.prop_list.GetItems())
        self.component.node.clearObject()