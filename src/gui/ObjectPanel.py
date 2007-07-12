"""\
A base wx.Panel class for all other Game Object panels
To inherit from. It will include a few convenience functions.
For now it's pretty small, but I'm sure it will grow in the future.
"""

import wx

class Panel(wx.Panel):
    def IsEditEvent(self, event):
        #ignore special keys special keys and ctrl combos except for paste
        return not (event.GetKeyCode() >= 300 and event.GetKeyCode() <= 396) \
               and not (event.ControlDown() and event.GetKeyCode() != 86)
               
    def OnTextEdit(self, event):
        if self.IsEditEvent(event):
            self.object.node.SetModified(True)
        event.Skip()
        
    def CreateChoiceMonitor(self, original_text):
        def ChoiceMonitor(event):
            choice = event.GetEventObject().GetStringSelection()        
            if choice != original_text:
                self.object.node.SetModified(True)
            event.Skip()
        return ChoiceMonitor
        
    def BindEditWatchers(self, widgets):
        """\
        Takes a list of widgets and binds an event handler to the KEY_DOWN
        event to check for changes being made to it.
        """
        for w in widgets:
            w.Bind(wx.EVT_KEY_UP, self.OnTextEdit)