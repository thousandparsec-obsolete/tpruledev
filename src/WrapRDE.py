#!/usr/bin/env python

"""
Wraps the RDE in PyCrust for interactive development and testing
"""

import wx
from wx.py import PyWrap
from RDE import RDE

rde = RDE(redirect=False)
PyWrap.wrap(rde)
