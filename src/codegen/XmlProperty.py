"""\
The XML I/O module for Property objects.
"""

from game_objects import Property
from elementtree.ElementTree import ElementTree, Comment, SubElement, Element
from rde.Exceptions import MalformedXmlError
import XmlUtils

def GenerateCode(prop, save_location):
    """\
    Writes a component out to an XML file
    """
    #make base tag and supply attributes as necessary
    root = Element(Property.GetName().lower(),
                    {"name": prop.name,
                     "description": prop.description,
                     "rank": prop.rank,
                     "display_text": prop.display_text,
                     "category": prop.category,
                     "version": XmlUtils.VERSION})
    #add the tpcl_requirements tag and its text
    tpcl_display_elem = SubElement(root, "tpcl_display")
    tpcl_display_elem.text = prop.tpcl_display
    tpcl_requires_elem = SubElement(root, "tpcl_requires")
    tpcl_requires_elem.text = prop.tpcl_requires
    et = ElementTree(root)
    et.write(save_location, indent=True)
    
def ParseCode(prop, save_location):
    """\
    Returns the component serialized to the given XML file
    """
    et = ElementTree(file=save_location)
    root = et.getroot()
    try:
        prop.description = root.get("description")
        prop.display_text = root.get("display_text")
        prop.rank = root.get("rank")
        prop.category = root.get("category")
        prop.tpcl_display = root.findtext("tpcl_display",
                                    Property.DEFAULT_TPCL_DISPLAY).strip()
        prop.tpcl_requires = root.findtext("tpcl_requires",
                                    Property.DEFAULT_TPCL_REQUIRES).strip()
    except KeyError:
        raise MalformedXmlError()
    