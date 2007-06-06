import wx
from wx.py import PyWrap
from RDE import RDE

rde = RDE(redirect=False)
PyWrap.wrap(rde)
