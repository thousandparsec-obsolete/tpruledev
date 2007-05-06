import pprint

import xml.dom.minidom
from xml.dom.minidom import Node, Document

doc = xml.dom.minidom.parse("PropTest.xml")
mapping = {}

root = doc.getElementsByTagName("property")[0]
print "name: " + root.getElementsByTagName("name")[0].childNodes[0].data
print "rank: " + root.getElementsByTagName("rank")[0].childNodes[0].data
print "property_id: " + root.getElementsByTagName("property_id")[0].childNodes[0].data
print "category_id: " + root.getElementsByTagName("category_id")[0].childNodes[0].data
print "description: " + root.getElementsByTagName("description")[0].childNodes[0].data
print "display_text: " + root.getElementsByTagName("display_text")[0].childNodes[0].data
print "tpcl_display: " + root.getElementsByTagName("tpcl_display")[0].childNodes[0].data
print "tpcl_requires: " + root.getElementsByTagName("tpcl_requires")[0].childNodes[0].data
print "cdata_test: " + root.getElementsByTagName("cdata_test")[0].childNodes[0].data
