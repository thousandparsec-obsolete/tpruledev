"""
wx.Panel and associated methods for editing
a Property object
"""

import wx

class Panel(wx.Panel):
    """
    A wx.Panel for displaying and editing Properties
    """
    
    def __init__(self, property, parent, id=wx.ID_ANY, style=wx.EXPAND):
        wx.Panel.__init__(self, parent, id=id, style=style)
        self.property = property
        flex_sizer = wx.FlexGridSizer(8, 2, 5, 5)
        flex_sizer.SetFlexibleDirection(wx.BOTH)
        
        name_label = self.createLabel("Name:")
        self.addLabelToFlex(flex_sizer, name_label)
        name_field = self.createField(str(property.name))
        self.addFieldToFlex(flex_sizer, name_field)

        rank_label = self.createLabel("Rank:")
        self.addLabelToFlex(flex_sizer, rank_label)
        rank_field = self.createField(str(property.rank))
        self.addFieldToFlex(flex_sizer, rank_field)

        property_id_label = self.createLabel("Property ID:")
        self.addLabelToFlex(flex_sizer, property_id_label)
        self_id_field = self.createField(str(property.property_id))
        self.addFieldToFlex(flex_sizer, self_id_field)

        category_id_label = self.createLabel("Category ID:")
        self.addLabelToFlex(flex_sizer, category_id_label)
        category_id_field = self.createField(str(property.category_id))
        self.addFieldToFlex(flex_sizer, category_id_field)

        desc_label = self.createLabel("Description:")
        self.addLabelToFlex(flex_sizer, desc_label)
        desc_field = self.createField(str(property.description))
        self.addFieldToFlex(flex_sizer, desc_field)

        disp_label = self.createLabel("Display Text:")
        self.addLabelToFlex(flex_sizer, disp_label)
        disp_field = self.createField(str(property.display_text))
        self.addFieldToFlex(flex_sizer, disp_field)

        tpcl_disp_label = self.createLabel("TPCL Display Function:")
        self.addLabelToFlex(flex_sizer, tpcl_disp_label)
        tpcl_disp_field = self.createField(str(property.tpcl_display))
        self.addFieldToFlex(flex_sizer, tpcl_disp_field)

        tpcl_req_label = self.createLabel("TPCL Requires Function:")
        self.addLabelToFlex(flex_sizer, tpcl_req_label)
        tpcl_req_field = self.createField(str(property.tpcl_requires))
        self.addFieldToFlex(flex_sizer, tpcl_req_field)
       
        flex_sizer.AddGrowableCol(1)
        flex_sizer.AddGrowableRow(6)
        flex_sizer.AddGrowableRow(7)
        
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
        self.property.node.clearObject()