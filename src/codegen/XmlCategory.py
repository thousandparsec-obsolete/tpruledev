"""\
The XML I/O module for Category objects.
"""

from game_objects import Category
from elementtree.ElementTree import ElementTree, Comment, SubElement, Element
from rde.Exceptions import MalformedXmlError
import XmlUtils

def GenerateCode(prop, save_location):
    """\
    Writes a component out to an XML file
    """
    #make base tag and supply attributes as necessary
    root = Element(Category.GetName().lower(),
                    {"name": prop.name,
                     "description": prop.description})
    et = ElementTree(root)
    et.write(save_location)
    
def ParseCode(cat, save_location):
    """\
    Returns the component serialized to the given XML file
    """
    et = ElementTree(file=save_location)
    root = et.getroot()
    try:
        cat.description = root.get("description")
    except KeyError:
        raise MalformedXmlError()