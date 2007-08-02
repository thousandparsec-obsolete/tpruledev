"""\
TPCL Python Representation
"""

class TpclBlocktype(object):
    """\
    A category for tpcl expressions
    """
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.members = []
    
    def AddMember(self, blocktype):
        if not blocktype in self.members:
            self.members.append(blocktype)
            
    def IsMember(self, blocktype, parents=None):
        """\
        Determines whether a given blocktype is a member
        of this category of blocktypes
        """
    
        #gah this is going to be horribly inefficient
        
        #first check if it's in our members list
        if self.members == []:
            return False
        elif blocktype in self.members:
            return True
        
        #now deal with our members list
        if parents == None:
            parents = [self]
        else:
            parents.append(self)
            
        for member in self.members:
            if not member in parents:
                if member.IsMember(blocktype, parents):
                    return True
    
        #should never get here, but just in case                
        return False

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
    BLOCK = 1
    
    def __init__(self):
        self.template = []
        
    def AppendTextElement(self, text):
        self.template.append((self.TEXT, text))
        
    def InsertTextElement(self, index, text):
        self.template.insert(index, (self.TEXT, text))
        
    def AppendBlockElement(self, block):
        self.template.append((self.BLOCK, block))
        
    def InsertBlockElement(self, index, block):
        self.template.insert(index, (self.BLOCK, block))
    
    def IsText(self, index):
        return (self.template[index][0] == self.TEXT)
    
    def GetElementType(self, index):
        return self.template[index][0]
        
    def GetElement(self, index):
        return self.template[index][1]
        
    def GetElementValue(self, index):
        """\
        Returns the text of the element if it's text
        or the name of the block if it's a block
        """
        if self.IsText(index):
            return self.template[index][1]
        else:
            return self.template[index][1]
        
    def GetLength(self):
        return len(self.template)
        
    length = property(GetLength, doc="The number of elements in the expression.")
        
    
class TpclExpression(object):
    """\
    An actual TPCL Expression composed of text and other expressions
    """
    TEXT = 0
    EXPANSION_POINT = 1
    EXPRESSION = 2
    
    def __init__(self, block, parent=None, offset=0):
        self.block = block
        self.template = block.template
        self.parent = parent
        self._offset = offset
        
        #initialize our data
        self.data = []
        self.offsets = []
        for i in range(self.template.length):
            if self.template.IsText(i):
                self.data.append(self.template.GetElementValue(i))
            else:
                self.data.append("*%s*" % self.template.GetElementValue(i))
            
            if i == 0:
                self.offsets.append(0)
            else:
                self.offsets.append(self.offsets[i-1] + self.LengthOfElement(i-1))
        
        self.offsets_ok = True
        self.length_ok = False
        self.string_ok = False
        
        self.RecalculateOffsets()
        
    def __str__(self):
        #format ourselves nicely here
        #make sure we add spaces between elements.
        if not self.string_ok:
            self.RecalculateString()
        return self._string
        
    def __len__(self):
        """\
        Return the total number of characters in our
        expression so that we have an idea of the length
        """
        if not self.length_ok:
            self.RecalculateLength()        
        return self._length
        
    #######################################
    # Utility functions for maintaining
    # various state variables such as
    # length and the offsets of elements
    #######################################
        
    def RecalculateLength(self):
        """\
        Calculates the length of the expression,
        accounting for the spaces between elements.
        
        We assume, here, that we have a valid expression
        as we might, in fact, have an expression with
        no elements, which would give us a length of -1
        """
        self._length = 0
        for i in range(len(self.data)):
            self._length += self.LengthOfElement(i)
        self.length_ok = True
                
    def RecalculateOffsets(self):
        """\
        Recalculates the offsets of all elements so
        that they are up to date.
        """
        for i in range(len(self.data)):
            offset = 0
            if i != 0:
                offset = self.offsets[i-1] + self.LengthOfElement(i-1)
            #set our relative offset
            self.offsets[i] = offset
            
            #pass along the absolute offset to the element
            # if it's an expression
            if hasattr(self.data[i], 'SetOffset'):
                self.data[i].SetOffset(offset + self._offset)
            
        self.offsets_ok = True
        
    def LengthOfElement(self, index):
        """\
        Returns the length of the element at the given index
        """
        return len(self.data[index])
        
    def RecalculateString(self):
        self._string = ""
        for i in range(len(self.data)):
            self._string += self.data[i].__str__()
        self.string_ok = True
        
    def GetIndexOfElemAt(self, offset):
        """\
        Gets the index of the element whose text is the given absolute offset
        """
        i = 0
        if offset < self._offset or self._offset + len(self) - 1 < offset:
            raise ValueError('Offset %d not in this expression [%d, %d].' % \
                                (offset, self._offset, self._offset + len(self) - 1))
        while i < len(self.data) - 1 and offset >= self.GetAbsoluteElemOffset(i+1):
            i += 1
        return i
        
    def InvalidateState(self):
        """\
        Invalidate our state so that we recalculate everything.
        """
        #TODO: split this up, perhaps, to make things more efficient
        self.offsets_ok = False
        self.length_ok = False
        self.string_ok = False
        if self.parent:
            self.parent.InvalidateState()
            
    def GetElemOffset(self, index):
        """\
        Gets the offset of start of the element at that
        index in our data.
        """
        if not self.offsets_ok:
            self.RecalculateOffsets()
        return self.offsets[index]
    
    def GetAbsoluteElemOffset(self, index):
        """\
        Gets the offset of start of the element at that
        index in our data.
        """
        return self.GetElemOffset(index) + self._offset
        
    def ElemIsExpression(self, index):
        """\
        Returns with a bool indicating whether or not
        the element at the given offset is an expression or block
        """
        return not self.template.IsText(index)
        
    def IsExpansionPoint(self, offset):
        """
        Returns tuple indicating that the offset is an expansion
        point or not and if it is the parent expression that contains
        that expansion point
        
            retval: (bool b, TpclExpression p)
            where b indicates if the text at offset is an
            expansion point. p is the parent of 
        """
        type = GetBlockType(offset)
        if type == self.TEXT:
            return (False, None)
        elif type == self.EXPANSION_POINT:
            return (True, self)
        else:
            return self.data[self.GetIndexOfElemAt(offset)].IsExpansionPoint(offset)
            
    def GetParentOfElemAt(self, offset):
        """\
        Returns the parent of the element at the offset.
        """
        type = self.GetBlockType(offset)
        if type == self.TEXT:
            return self.parent
        elif type ==self.EXPANSION_POINT:
            return self
        else:
            return self.data[self.GetIndexOfElemAt(offset)].GetParentOfElemAt(offset)
        
    #############################################
    # The public interface that we use to
    # get info about this particular expression
    #############################################
    
    def SetOffset(self, offset):
        """\
        Sets the base offset for this element.
        """
        print "Setting offset to - %d" % offset
        self.offsets_ok = False
        self._offset = offset
        
    def IsExpression(self, offset):
        """\
        Returns with a bool indicating whether or not the
        text at the given (absolute) offset is part of an expression
        """
        return self.ElemIsExpression(self.GetIndexOfElemAt(offset))
        
    def GetBlockType(self, offset):
        index = self.GetIndexOfElemAt(offset)
        if self.template.IsText(index):
            return self.TEXT
        elif hasattr(self.data[index], "GetBlockType"):
            return self.EXPRESSION
        else:
            return self.EXPANSION_POINT
        
    def InsertExpression(self, offset, expression):
        """\
        Inserts an expression at the given offset
        """
        if not self.offsets_ok:
            self.RecalculateOffsets()
            
        type = self.GetBlockType(offset)
        if  type == self.EXPANSION_POINT:
            index = self.GetIndexOfElemAt(offset)
            self.data[index] = expression
            expression.SetOffset(self.GetAbsoluteElemOffset(index))
            #todo: need to start guarding against multiple parents
            expression.parent = self
            self.InvalidateState()
        elif type == self.EXPRESSION:
            self.data[self.GetIndexOfElemAt(offset)].InsertExpression(offset, expression)
        else:
            raise ValueError('There is no expression at offset %d' % offset)
        
    def RemoveExpression(self, offset):
        """\
        Removes the expression at the given offset
        """
        if not self.offsets_ok:
            self.RecalculateOffsets()
            
        parent = self.GetParentOfElemAt(offset)
        if  parent != None:
            if parent == self:
                index = self.GetIndexOfElemAt(offset)
                self.data[index] = "*%s*" % self.template.GetElementValue(index)
                self.InvalidateState()    
            else:
                parent.RemoveExpression(offset)            
        else:
            raise ValueError("You can't remove the top level expression!")
