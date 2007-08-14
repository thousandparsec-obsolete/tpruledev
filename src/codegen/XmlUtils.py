"""\
Utilities and common attributes for XML reading and writing.
"""
    
from rde.Exceptions import *
import os

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

ElementTree = None
def ImportElementTree():
    global ElementTree
    elemtree = None
    if not ElementTree:
        errors = []
        try:
            import elementtree.ElementTree as elemtree
        except ImportError, e:
            errors.append(e)
        try:
            import lxml.etree as elemtree
        except ImportError:
            errors.append(e)
        try:
            import xml.etree.ElementTree as elemtree
        except ImportError:
            errors.append(e)
            
        if elemtree is None:
            raise ImportError(str(errors))
        else:
            ElementTree = elemtree
            
    return ElementTree

ET = ImportElementTree()
##
# Writes the element tree to a file, as XML.
#
#   Adapted from ElementTree.py
##
def WriteElementTree(et, file, encoding="us-ascii", indent=False):
    assert et._root is not None
    if hasattr(ET, "_escape_cdata"):
        if not hasattr(file, "write"):
            file = open(file, "wb")
        if not encoding:
            encoding = "us-ascii"
        elif encoding != "utf-8" and encoding != "us-ascii":
            file.write("<?xml version='1.0' encoding='%s'?>\n" % encoding)
        WriteNode(file, et._root, encoding, {}, indent)
    else:
        et.write(file, encoding)

def WriteNode(file, node, encoding, namespaces, indent=False, height=0):
    # write XML to file
    indentation = ""
    linesep = ""
    if indent:
        indentation = height*"   "
        linesep = os.linesep
    tag = node.tag
    if tag is ET.Comment:
        file.write(indentation + "<!-- %s -->%s" % (ET._escape_cdata(node.text, encoding), linesep))
    elif tag is ET.ProcessingInstruction:
        file.write(indentation + "<?%s?>%s" % (ET._escape_cdata(node.text, encoding), linesep))
    else:
        items = node.items()
        xmlns_items = [] # new namespaces in this scope
        try:
            if isinstance(tag, ET.QName) or tag[:1] == "{":
                tag, xmlns = ET.fixtag(tag, namespaces)
                if xmlns: xmlns_items.append(xmlns)
        except TypeError:
            ET._raise_serialization_error(tag)
        file.write(indentation + "<" + ET._encode(tag, encoding))
        if items or xmlns_items:
            items.sort() # lexical order
            for k, v in items:
                try:
                    if isinstance(k, ET.QName) or k[:1] == "{":
                        k, xmlns = ET.fixtag(k, namespaces)
                        if xmlns: xmlns_items.append(xmlns)
                except TypeError:
                    ET._raise_serialization_error(k)
                try:
                    if isinstance(v, ET.QName):
                        v, xmlns = ET.fixtag(v, namespaces)
                        if xmlns: xmlns_items.append(xmlns)
                except TypeError:
                    ET._raise_serialization_error(v)
                file.write(linesep + indentation + "   %s=\"%s\"" % (ET._encode(k, encoding),
                                           ET._escape_attrib(v, encoding)))
            for k, v in xmlns_items:
                file.write(linesep + indentation + "   %s=\"%s\"" % (ET._encode(k, encoding),
                                           ET._escape_attrib(v, encoding)))
        if node.text or len(node):
            file.write(">")
            if node.text:
                file.write(ET._escape_cdata(node.text, encoding))
            else:
                file.write(linesep)
            for n in node:
                WriteNode(file, n, encoding, namespaces, indent, height+1)
            file.write(indentation + "</" + ET._encode(tag, encoding) + ">" + linesep)
        else:
            file.write(" />" + linesep)
        for k, v in xmlns_items:
            del namespaces[v]
    if node.tail:
        file.write(ET._escape_cdata(node.tail, encoding))