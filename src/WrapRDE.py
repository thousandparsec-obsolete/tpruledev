#!/usr/bin/env python

"""
Wraps the RDE in PyCrust for interactive development and testing
"""

import wx, sys
from wx.py import PyWrap
import RDE

rde = RDE.App(redirect=False)
PyWrap.wrap(rde)
