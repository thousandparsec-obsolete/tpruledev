"""\
TPCL Python Representation
"""

class TpclBlock(object):
    """\
    The python representation of a block of TPCL code.
    """
    def __init__(self, name, type, description, display=""):
        self.name = name
        self.type = type
        self.description = description
        self.display = display
        self.template = TpclTemplate()
    
    
class TpclTemplate(object):
    """\
    A template defining the structure of a block of TPCL code.
    Each TpclBlock has a template to define the structure of its
    code snippet.
    
    We keep a list of textual elements and tpcl insertion points.
    """
    TEXT = 0
    TPCL = 1
    
    def __init__(self):
        self.template = []
        
    def AppendTextElement(self, text):
        self.template.append((self.TEXT, text))
        
    def InsertTextElement(self, index, text):
        self.template.insert(index, (self.TEXT, text))
        
    def AppendTpclSlot(self, types):
        self.template.append((self.TPCL, types))
        
    def InsertTpclSlot(self, index, types):
        self.template.insert(index, (self.TPCL, types))
    
    def GetElementType(self, index):
        return self.template[index][0]
        
    def GetElementValue(self, index):
        return self.template[index][1]
        
    
class TpclSnippet(object):
    """\
    An actual snippet of TpclCode composed of
    other TpclSnippets
    """
    
    def __init__(self, block):
        self.block = block
        self.template = block.template
        self.data =[]
        