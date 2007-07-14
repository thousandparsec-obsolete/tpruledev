"""\
Utilities and common attributes for XML reading and writing.
"""

from elementtree.ElementTree import Element, SubElement, tostring

VERSION = "1.0"

def indent(elem, level=0):
	"""
	Simple helper function to indent an ElementTree before outputing it.
	Passed the root element of the tree.
	"""
	i = "\n" + level*"  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		for elem in elem:
			indent(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i