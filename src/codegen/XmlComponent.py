"""\
The XML I/O module for Component objects.
"""

from game_objects import Component
from elementtree.ElementTree import ElementTree, Comment, SubElement, Element
from rde.Exceptions import MalformedXmlError
import XmlUtils

def GenerateCode(comp, save_location):
    """\
    Writes a component out to an XML file
    """
    #make base tag and supply attributes as necessary
    root = Element(Component.GetName().lower(),
                    {"name": comp.name,
                     "description": comp.description,
                     "version": XmlUtils.VERSION})
    #add the tpcl_requirements tag and its text
    tpcl_req_elem = SubElement(root, "tpcl_requirements")
    tpcl_req_elem.text = comp.tpcl_requirements
    #add the categories
    root.append(Comment("categories"))
    for cat in comp.categories:
        cat_elem = SubElement(root, "category", {'name': cat})
    #add the properties
    root.append(Comment("properties"))
    for name, tpcl_cost in comp.properties.iteritems():
        propelem = SubElement(root, "property",
                                {"name": name})
        tpcl_cost_elem = SubElement(propelem, "tpcl_cost")
        tpcl_cost_elem.text = tpcl_cost
    et = ElementTree(root)
    et.write(save_location, indent=True)
    
def ParseCode(comp, save_location):
    """\
    Returns the component serialized to the given XML file
    """
    et = ElementTree(file=save_location)
    root = et.getroot()
    XmlUtils.VerifyVersion(root)
    try:
        comp.description = root.get("description")
        comp.category = root.get("category")
        comp.categories = []
        for cat in root.findall("category"):
            comp.categories.append(cat.get("name"))
        comp.tpcl_requirements = root.findtext("tpcl_requirements",
                                    Component.DEFAULT_TPCL_REQUIREMENTS).strip()
        comp.properties = {}
        for prop in root.findall("property"):
            comp.properties[prop.get("name")] = prop.findtext("tpcl_cost", '(lambda (design) 0)').strip()
    except KeyError:
        raise MalformedXmlError()
    