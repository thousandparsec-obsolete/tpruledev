"""\
The XML I/O module for Category objects.
"""

from game_objects import Category
from rde.Exceptions import MalformedXmlError
import XmlUtils
ElementTree = XmlUtils.ImportElementTree()

def GenerateCode(prop, save_location):
    """\
    Writes a component out to an XML file
    """
    #make base tag and supply attributes as necessary
    root = ElementTree.Element(Category.GetName().lower(),
                    {"name": prop.name,
                     "description": prop.description,
                     "version": XmlUtils.VERSION})
    et = ElementTree.ElementTree(root)
    XmlUtils.WriteElementTree(et, save_location, indent=True)
    
def ParseCode(cat, save_location):
    """\
    Returns the component serialized to the given XML file
    """
    et = ElementTree.ElementTree(file=save_location)
    root = et.getroot()
    XmlUtils.VerifyVersion(root)
    try:
        cat.description = root.get("description")
    except KeyError:
        raise MalformedXmlError()