"""\
Utilities and common attributes for XML reading and writing.
"""

from elementtree.ElementTree import Element, SubElement, tostring
from rde.Exceptions import *

VERSION = "1.1"
REQUIRED_VERSION = "1.1"

def VerifyVersion(root):
    """\
    Verifies that we are the correct version of XML
    persistence file
    """
    global VERSION
    global REQUIRED_VERSION
    try:
        if root.get("version") < REQUIRED_VERSION:
            raise XmlVersionError("XML Version must be %s or above, we found %s!" \
                                  % (REQUIRED_VERSION, root.get("version")))
    except KeyError:
        raise MalformedXmlError()