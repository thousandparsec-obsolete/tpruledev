"""
wx.Panel and associated methods for editing
a Property object
"""

import wx
import gui.TextCtrl

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
        name_field = wx.StaticText(self, wx.ID_ANY, str(property.name),
                                        style=wx.ALIGN_LEFT | wx.ALIGN_TOP)
        self.addFieldToFlex(flex_sizer, name_field)

        rank_label = self.createLabel("Rank:")
        self.addLabelToFlex(flex_sizer, rank_label)
        self.rank_field = self.createField(str(property.rank))
        self.addFieldToFlex(flex_sizer, self.rank_field)

        property_id_label = self.createLabel("Property ID:")
        self.addLabelToFlex(flex_sizer, property_id_label)
        self.propid_field = self.createField(str(property.property_id))
        self.addFieldToFlex(flex_sizer, self.propid_field)

        category_id_label = self.createLabel("Category ID:")
        self.addLabelToFlex(flex_sizer, category_id_label)
        self.catid_field = self.createField(str(property.category_id))
        self.addFieldToFlex(flex_sizer, self.catid_field)

        desc_label = self.createLabel("Description:")
        self.addLabelToFlex(flex_sizer, desc_label)
        self.desc_field = self.createField(str(property.description))
        self.addFieldToFlex(flex_sizer, self.desc_field)

        disp_label = self.createLabel("Display Text:")
        self.addLabelToFlex(flex_sizer, disp_label)
        self.disp_field = self.createField(str(property.display_text))
        self.addFieldToFlex(flex_sizer, self.disp_field)

        tpcl_disp_label = self.createLabel("TPCL Display Function:")
        self.addLabelToFlex(flex_sizer, tpcl_disp_label)
        self.tpcl_disp_stc = self.createTextArea(str(property.tpcl_display))
        self.addFieldToFlex(flex_sizer, self.tpcl_disp_stc)

        tpcl_req_label = self.createLabel("TPCL Requires Function:")
        self.addLabelToFlex(flex_sizer, tpcl_req_label)
        self.tpcl_req_stc = self.createTextArea(str(property.tpcl_requires))
        self.addFieldToFlex(flex_sizer, self.tpcl_req_stc)
       
        flex_sizer.AddGrowableCol(1)
        flex_sizer.AddGrowableRow(6)
        flex_sizer.AddGrowableRow(7)
        
        border1 = wx.BoxSizer(wx.HORIZONTAL)
        border1.Add(flex_sizer, 1, wx.ALL | wx.EXPAND)
        border2 = wx.BoxSizer(wx.VERTICAL)
        border2.Add(border1, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(border2)
        
    def CheckForModification(self):
        print "Checking Property %s for modifications" % self.property.name
        mod = False
        #print "\property_id: %s <> %s" % (self.component.property_id, self.property_id.GetValue())
        if str(self.property.property_id) != self.propid_field.GetValue():
            mod = True
            self.property.component_id = self.propid_field.GetValue()
        
        #print "\category_id: %s <> %s" % (self.property.category_id, self.catid_field.GetValue())
        if str(self.property.category_id) != self.catid_field.GetValue():
            mod = True
            self.property.category_id = self.catid_field.GetValue()
        
        #display text
        if self.property.display_text != self.disp_field.GetValue():
            mod = True
            self.property.display_text = self.disp_field.GetValue()
            
        #rank
        if str(self.property.rank) != self.rank_field.GetValue():
            mod = True
            self.property.rank = self.rank_field.GetValue()
        
        #print "\description: %s <> %s" % (self.property.description, self.desc_field.GetValue())
        if self.property.description != self.desc_field.GetValue():
            mod = True
            self.property.description = self.desc_field.GetValue()
            
        #print "\tpcl_requires: %s <> %s" % (self.property.tpcl_requires, self.tpcl_req_ctrl.GetText())
        if self.property.tpcl_requires != self.tpcl_req_stc.GetText():
            mod = True
            self.property.tpcl_requires = self.tpcl_req_stc.GetText()
            
        #print "\tpcl_display: %s <> %s" % (self.property.tpcl_display, self.tpcl_req_ctrl.GetText())
        if self.property.tpcl_display != self.tpcl_disp_stc.GetText():
            mod = True
            self.property.tpcl_display = self.tpcl_disp_stc.GetText()
        
        if mod:
            self.property.node.SetModified(True)
    
    def createLabel(self, text):
        return wx.StaticText(self, wx.ID_ANY, text, style=wx.ALIGN_RIGHT | wx.ALIGN_TOP)
    
    def addLabelToFlex(self, flex, label):
        flex.Add(label, 2, wx.ALIGN_RIGHT | wx.ALIGN_TOP | wx.EXPAND, 5)

    def createField(self, text):
        return wx.TextCtrl(self, wx.ID_ANY, text)
        
    def createTextArea(self, text):
        return gui.TextCtrl.SchemeSTC(self, wx.ID_ANY, text)
        
    def addFieldToFlex(self, flex, field):
        flex.Add(field, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 5)
        
    def cleanup(self):
        self.CheckForModification()
        self.property.node.clearObject()