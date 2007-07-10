#!/usr/bin/env python

"""\
Manually transforms all existing persistence files to the new format.
Should be run before opening the RDE.
Pass the relative or absolute path of a project directory as the first
argument to transform all object persistence files.
"""

import os, sys
from elementtree.ElementTree import ElementTree, Element, Comment, SubElement

if len(sys.argv) < 2:
    print "USAGE: ./transform_objects PATH/TO/PROJECT/DIR"
    exit(0)

persistence_path = os.path.join(sys.argv[1], "persistence")
cat_path = os.path.join(persistence_path, "Category")
comp_path = os.path.join(persistence_path, "Component")
prop_path = os.path.join(persistence_path, "Property")
if not os.path.exists(persistence_path) or \
        not os.path.exists(cat_path) or \
        not os.path.exists(comp_path) or \
        not os.path.exists(prop_path):
    print "INVALID PROJECT DIRECTORY"
    exit(0)
    
et = ElementTree()
    
#transform categories
print "Transforming Categories..."
for cat_fname in os.listdir(cat_path):
    fpath = os.path.join(cat_path, cat_fname)
    et.parse(fpath)
    if not et.getroot().get("version"):
        print "\tTransforming %s..." % cat_fname
        root = Element("category",
                        {"version": "1.0",
                         "name": et.find("name").text.strip(),
                         "description": et.find("description").text.strip()})
        et = ElementTree(root)
        et.write(fpath)
    else:
        print "\tSkipping %s - Not the version this script was written to transform." % cat_fname
    
#transform components
print "Transforming Components..."
for comp_fname in os.listdir(comp_path):
    fpath = os.path.join(comp_path, comp_fname)
    et.parse(fpath)
    if not et.getroot().get("version"):
        print "\tTransforming %s..." % comp_fname
        root = Element("component",
                        {"version": "1.0",
                         "name": et.find("name").text.strip(),
                         "description": et.find("description").text.strip(),
                         "category": et.find("category").text.strip()})
        tpcl_req = SubElement(root, "tpcl_requirements")
        tpcl_req.text = et.find("tpcl_requirements").text.strip()
        root.append(Comment("propertylist"))
        for prop in et.findall("property"):
            propelem = SubElement(root, "property",
                                    {"name": prop.find("name").text.strip()})
            tpcl_cost = SubElement(propelem, "tpcl_cost")
            tpcl_cost.text = prop.find("tpcl_cost").text.strip()
        et = ElementTree(root)
        et.write(fpath)
    else:
        print "\tSkipping %s - Not the version this script was written to transform." % comp_fname
    
#transform properties
print "Transforming Properties..."
for prop_fname in os.listdir(prop_path):
    fpath = os.path.join(prop_path, prop_fname)
    et.parse(fpath)
    if not et.getroot().get("version"):
        print "\tTransforming %s..." % prop_fname
        root = Element("prop",
                        {"version": "1.0",
                         "name": et.find("name").text.strip(),
                         "description": et.find("description").text.strip(),
                         "category": et.find("category").text.strip(),
                         "rank": et.find("rank").text.strip(),
                         "display_text": et.find("display_text").text.strip()})
        tpcl_disp = SubElement(root, "tpcl_display")
        tpcl_disp.text = et.find("tpcl_display").text.strip()
        tpcl_req = SubElement(root, "tpcl_requires")
        tpcl_req.text = et.find("tpcl_requires").text.strip()
        et = ElementTree(root)
        et.write(fpath)
    else:
        print "\tSkipping %s - Not the version this script was written to transform." % prop_fname
