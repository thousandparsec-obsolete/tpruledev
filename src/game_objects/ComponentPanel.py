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
        name_field = self.createField(str(component.name))
        self.addFieldToFlex(flex_sizer, name_field)

        comp_id_label = self.createLabel("Component ID:")
        self.addLabelToFlex(flex_sizer, comp_id_label)
        comp_id_field = self.createField(str(component.component_id))
        self.addFieldToFlex(flex_sizer, comp_id_field)

        category_id_label = self.createLabel("Category ID:")
        self.addLabelToFlex(flex_sizer, category_id_label)
        category_id_field = self.createField(str(component.category_id))
        self.addFieldToFlex(flex_sizer, category_id_field)

        desc_label = self.createLabel("Description:")
        self.addLabelToFlex(flex_sizer, desc_label)
        desc_field = self.createField(str(component.description))
        self.addFieldToFlex(flex_sizer, desc_field)

        tpcl_req_label = self.createLabel("TPCL Requirements Function:")
        self.addLabelToFlex(flex_sizer, tpcl_req_label)
        tpcl_req_stc = gui.TextCtrl.SchemeSTC(self, -1, str(component.tpcl_requirements))
        self.addFieldToFlex(flex_sizer, tpcl_req_stc)

        props_label = self.createLabel("Associated Properties:")
        self.addLabelToFlex(flex_sizer, props_label)
        #TODO make this into a ListCtrl
        prop_list = wx.ListBox(self, wx.ID_ANY)
        prop_names = []
        for pname, tpcl_cost in component.properties.iteritems():
            prop_names.append(pname)
            prop_list.Insert(str(pname) + " - " + str(tpcl_cost), 0)
        self.high_id = component.node.object_database.Emphasize(prop_names, "BLUE")
        self.addFieldToFlex(flex_sizer, prop_list)
       
        flex_sizer.AddGrowableCol(1) #field column
        flex_sizer.AddGrowableRow(4) #tpcl_requirements function
        flex_sizer.AddGrowableRow(5) #property list

        border1 = wx.BoxSizer(wx.HORIZONTAL)
        border1.Add(flex_sizer, 1, wx.ALL | wx.EXPAND, 5)
        border2 = wx.BoxSizer(wx.VERTICAL)
        border2.Add(border1, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(border2)
        
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
        prop_names = []
        try:
            self.component.node.object_database.UnEmphasize(self.high_id)
        except NoSuchIDError:
            #someone already got rid of our emphasis...strange but OK
            pass
        self.component.node.clearObject()