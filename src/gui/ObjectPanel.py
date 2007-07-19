"""\
A base wx.Panel class for all other Game Object panels
To inherit from. It will include a few convenience functions.
For now it's pretty small, but I'm sure it will grow in the future.
"""

import wx
from wx.xrc import XmlResource, XRCCTRL

class Panel(wx.Panel):
    def Setup(self):
        self.error_labels = []
        self.loading = False
    
    def CreateAttributeMonitor(self, attribute_name):
        """\
        Monitors an attribute input widget for changes.
        When a change is detected it is recorded into the
        object data and the node is notified of the modification
        """
        def AttributeMonitor(event):
            print "In AttributeMonitor"
            if not self.loading:
                print "\tEventType:", event.GetEventType()
                obj = event.GetEventObject()
                value = ""
                edit = False
                if event.GetEventType() == wx.wxEVT_COMMAND_TEXT_UPDATED:
                    #this is a text field and we have had our text modified
                    print "\tText field event"
                    value = obj.GetValue()
                    edit = True
                elif event.GetEventType() == wx.stc.wxEVT_STC_CHANGE:
                    #stc event
                    print "\tSTC event"
                    value = obj.GetText()
                    edit = True
                elif event.GetEventType() == wx.wxEVT_COMMAND_CHOICE_SELECTED:
                    #choice box
                    print "\tChoice event"
                    value = obj.GetStringSelection()
                    edit = True
                
                if edit:
                    attr = getattr(self.object, attribute_name)
                    print "old value: %s, new value: %s" % (attr, value)
                    if value != attr:
                        print "\tChange detected and saved"
                        self.node.SetModified(True)
                        setattr(self.object, attribute_name, value)
            event.Skip()
        return AttributeMonitor
            
    def SetErrorLabel(self, attr_name, error):
        """\
        Marks the label of the given attribute red and provides
        a tooltip with the error.
        
        This function gets a resource from the XRC file, so
        the labels have to follow the naming convention of
        ATTRIBUTE-NAME_label or else an error will result
        when the label can't be found in the XRC file
        """
        label = XRCCTRL(self, attr_name + "_label")
        label.SetForegroundColour("RED")
        label.SetToolTip(wx.ToolTip(error))
        self.error_labels.append(label)
        
    def CleanupErrorLabels(self):
        """\
        Removes red emphasis from labels of attributes with
        errors and also removes their tooltips.
        """
        for label in self.error_labels:
            label.SetForegroundColour("BLACK")
            label.SetToolTip(None)
            self.error_labels.remove(label)
                