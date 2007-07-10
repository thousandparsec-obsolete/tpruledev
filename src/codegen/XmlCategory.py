"""\
The XML I/O module for Category objects.
"""

from game_objects import Category
from elementtree.ElementTree import ElementTree, Comment, SubElement, Element
from rde.Exceptions import MalformedXmlError
import XMLUtils

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
    
def ParseCode(node, name, save_location):
    """\
    Returns the component serialized to the given XML file
    """
    et = ElementTree(file=save_location)
    root = et.getroot()
    prop = Category(node, name)
    try:
        prop.description = root.get("description")
    except KeyError:
        raise MalformedXmlError()
    return comp