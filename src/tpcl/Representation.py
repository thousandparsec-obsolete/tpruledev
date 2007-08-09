"""\
TPCL Python Representation
"""

import copy

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
    def __init__(self, name, description, display="", template=None):
        self.name = name
        self.description = description
        self.display = display
        self.template = template
        if not template:
            self.template = TpclTemplate()
        
    
class TpclTemplate(object):
    """\
    A template defining the structure of a block of TPCL code.
    Each TpclBlock has a template to define the structure of its
    code snippet.
    
    We keep a list of textual elements and tpcl insertion points.
    """
    TEXT = 1
    BLOCK = 2
    INDENT = 4
    EOL = 8
    EXPANSION = 16
    
    def __init__(self):
        self.template = []
        
    def __len__(self):
        return len(self.template)
        
    ##############################
    # Insertion methods
    ##############################
        
    def AppendTextElement(self, text):
        self.template.append((self.TEXT, text))
        
    def InsertTextElement(self, index, text):
        self.template.insert(index, (self.TEXT, text))
        
    def AppendBlockElement(self, block):
        self.template.append((self.BLOCK, block))
        
    def InsertBlockElement(self, index, block):
        self.template.insert(index, (self.BLOCK, block))
        
    def AppendEolElement(self):
        self.template.append((self.EOL, "\n"))
        
    def InsertEolElement(self, index):
        self.template.insert(index, (self.EOL, "\n"))
        
    def AppendIndentElement(self):
        self.template.append((self.INDENT, "\t"))
        
    def InsertIndentElement(self, index):
        self.template.insert(index, (self.INDENT, "\t"))
        
    #expansion options are tuples of the form (name, TpclTemplate)
    def AppendExpansionElement(self, expansion_options):
        self.template.append((self.EXPANSION, "...", expansion_options))
        
    def InsertExpansionElement(self, index, expansion_options):
        self.template.insert(index, (self.EXPANSION, "...", expansion_options))
        
    def FillExpansionElement(self, index, block):
        self.template.insert(index, ((self.BLOCK | self.EXPANSION), block))
        
    def RemoveElement(self, index):
        del self.template[index]
        
    #####################################
    # Type test methods
    #####################################
    
    def IsText(self, index):
        #Simple text, EOL and indents all count as text.
        return (self.template[index][0] & (self.TEXT | self.EOL | self.INDENT) > 0)
               
    def IsSimpletext(self, index):
        return (self.template[index][0] & self.TEXT > 0)
    
    def IsEol(self, index):
        return (self.template[index][0] & self.EOL > 0)
        
    def IsIndent(self, index):
        return (self.template[index][0] & self.INDENT > 0)
        
    def IsBlock(self, index):
        return (self.template[index][0] & self.BLOCK > 0)
    
    def IsExpansionPoint(self, index):
        return (self.template[index][0] & self.EXPANSION > 0)
        
    def IsFilledExpansion(self, index):
        return ((self.template[index][0] & self.EXPANSION > 0) and \
                (self.template[index][0] & self.BLOCK > 0))
    
    #####################################
    # Getters
    #####################################
    
    def GetElementType(self, index):
        return self.template[index][0]
        
    def GetElement(self, index):
        return self.template[index]
        
    def GetElementValue(self, index):
        """\
        Returns the text of the element if it's text
        or the name of the block if it's a block
        """
        return self.template[index][1]
        
    def GetLength(self):
        return len(self.template)
        
    length = property(GetLength, doc="The number of elements in the expression.")
        
    
class TpclExpression(object):
    """\
    An actual TPCL Expression composed of text and other expressions
    """
    TEXT = 1
    INSERTION_POINT = 2
    EXPRESSION = 4
    EOL = 8
    INDENT = 16
    EXPANSION_POINT = 32
    
    
    def __init__(self, block, parent=None, offset=0, indent=0):
        self.block = block
        self.template = copy.deepcopy(block.template)
        self.parent = parent
        
        self._offset = offset
        self.offsets = [None] * len(self.template)
        
        self.base_indent = indent
        self.indent_level = [None] * len(self.template)
        
        self.expansion_options = [None] * len(self.template)
        
        self.indent_ok = False
        self.offsets_ok = False
        self.length_ok = False
        self.string_ok = False
        
        #initialize our data
        self.data = []
        for i in range(len(self.template)):
            if self.template.IsText(i):
                #text needs no special markup
                self.data.append(self.template.GetElementValue(i))
            else:
                #we markup insertion and expansion points
                self.data.append("*%s*" % self.template.GetElementValue(i))
                if self.template.IsExpansionPoint(i):
                    self.expansion_options[i] = self.template.GetElement(i)[2]
                
        self.RecalculateIndentation()
        self.RecalculateOffsets()
        
    def __str__(self):
        #format ourselves nicely here
        #make sure we add spaces between elements.
        if not self.indent_ok:
            self.RecalculateIndentation()
        if not self.string_ok:
            self.RecalculateString()
        return self._string
        
    def __len__(self):
        """\
        Return the total number of characters in our
        expression so that we have an idea of the length
        """
        if not self.indent_ok:
            self.RecalculateIndentation()
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
    
    def RecalculateIndentation(self):
        #pre-process the block for indent levels
        for i in range(self.template.length):
            curr_indent = self.base_indent
            if i != 0:
                if self.template.GetElementType(i) == self.template.EOL:
                    curr_indent = self.base_indent
                elif self.template.GetElementType(i-1) == self.template.INDENT:
                    curr_indent = self.indent_level[i-1] + 1
                else:
                    curr_indent = self.indent_level[i-1]
                    
            self.indent_level[i] = curr_indent
                
            if self.template.GetElementType(i) == TpclTemplate.EOL:
                #we pad with tabs after a newline to achieve indentation
                self.data[i] = self.template.GetElementValue(i) + ("\t"*self.indent_level[i])
                
        self.string_ok = False
        self.length_ok = False
        self.offsets_ok = False
        
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
        self.indent_ok = False
        if self.parent:
            self.parent.InvalidateState()
            
    def GetElemOffset(self, index):
        """\
        Gets the offset of start of the element at that
        index in our data.
        """
        if not self.indent_ok:
            self.RecalculateIndentation()
        if not self.offsets_ok:
            self.RecalculateOffsets()
        return self.offsets[index]
    
    def GetAbsoluteElemOffset(self, index):
        """\
        Gets the offset of start of the element at that
        index in our data.
        """
        return self.GetElemOffset(index) + self._offset
        
    def IsInsertionPoint(self, offset):
        """
        Returns tuple indicating that the offset is an insertion
        point or not and if it is the parent expression that contains
        that expansion point
        
            retval: (bool b, TpclExpression p)
            where b indicates if the text at offset is an
            expansion point. p is the parent of 
        """
        index = self.GetIndexOfElemAt(offset)
        if self.ElemIsText(index) or self.ElemIsExpansionPoint(index):
            return (False, None)
        elif self.ElemIsInsertionPoint(index):
            return (True, self)
        else:
            return self.data[index].IsInsertionPoint(offset)
            
    def IsExpansionPoint(self, offset):
        """\
        Returns a tuple indicating whether or not the offset lies
        on an expansion point and if so, returns the parent as well.
        """
        index = self.GetIndexOfElemAt(offset)
        if self.ElemIsText(index):
            return (False, None)
        elif self.ElemIsInsertionPoint(index):
            if self.ElemIsExpansionPoint(index):
                return (True, self)
            else:
                return (False, None)
        elif self.ElemIsExpression(index):
            return self.data[index].IsExpansionPoint(offset)
        else:
            return (True, self)
            
    def GetExpansionOptions(self, offset):
        """\
        Returns the options for expansion at a given offset as
        a list of names.
        
        Returns None if this is not an expansion point
        """
        index = self.GetIndexOfElemAt(offset)
        if self.ElemIsText(index) or self.ElemIsInsertionPoint(index):
            return None
        elif self.ElemIsExpression(index):
            return self.data[index].GetExpansionOptions(offset)
        else:
            return [o[0] for o in self.expansion_options[index]]
            
    def Expand(self, offset, option):
        print "In TpclExpression <%s> trying to expand at %d with option %d" % (self.block.name, offset, option)
        index = self.GetIndexOfElemAt(offset)
        if self.ElemIsText(index) or self.ElemIsInsertionPoint(index):
            return None
        elif self.ElemIsExpression(index):
            return self.data[index].Expand(offset, option)
        else:
            exp_opts = self.expansion_options[index]
            if exp_opts:
                exp_template = self.expansion_options[index][option][1]
                if exp_template:
                    #we are expanding
                    expr = TpclExpression(TpclBlock("exp_point", "disp",
                                                    "desc", exp_template))
                    self.offsets.insert(index, 0)
                    self.indent_level.insert(index, 0)
                    self.expansion_options.insert(index, None)
                    self.data.insert(index, expr)
                    self.template.FillExpansionElement(index, "EXPR")
                else:
                    self.DeleteElement(index)
                    
                self.InvalidateState()
                
    def DeleteElement(self, index):
        """\
        Deletes an element completely from our internal represenation
        and the template.
        """
        print "<%s> is deleting element at index %d" % (self.block.name, index)
        print "\telement: %s" % self.data[index]
        del self.offsets[index]
        del self.indent_level[index]
        del self.expansion_options[index]
        del self.data[index]
        self.template.RemoveElement(index)
        self.InvalidateState()
            
    def GetParentOfElemAt(self, offset):
        """\
        Returns the parent of the element at the offset.
        """
        index = self.GetIndexOfElemAt(offset)
        if self.ElemIsText(index):
            return self.parent
        elif self.ElemIsInsertionPoint(index) or self.ElemIsExpansionPoint(index):
            return self
        else:
            return self.data[index].GetParentOfElemAt(offset)
        
        
    #############################################
    # Getters for element types
    #############################################
    
    def ElemIsSimpletext(self, index):
        return self.template.IsSimpletext(index)
        
    def OffsetIsSimpletext(self, offset):
        return self.ElemIsSimpletext(self.GetIndexOfElemAt(offset))
    
    def ElemIsText(self, index):
        return self.template.IsText(index)
        
    def OffsetIsText(self, offset):
        return self.ElemIsText(self.GetIndexOfElemAt(offset))
    
    def ElemIsEol(self, index):
        return self.template.IsEol(index)
        
    def OffsetIsEol(self, offset):
        return self.ElemIsEol(self.GetIndexOfElemAt(offset))
    
    def ElemIsIndent(self, index):
        return self.template.IsIndent(index)
        
    def OffsetIsIndent(self, offset):
        return self.ElemIsIndent(self.GetIndexOfElemAt(offset))
    
    def ElemIsInsertionPoint(self, index):
        if self.template.IsBlock(index):
            return not hasattr(self.data[index], "InvalidateState")
        else:
            return False
            
    def OffsetIsInsertionPoint(self, offset):
        return self.ElemIsInsertionPoint(self.GetIndexOfElemAt(offset))
    
    def ElemIsExpression(self, index):
        if self.template.IsBlock(index):
            return hasattr(self.data[index], "InvalidateState")
        else:
            return False
            
    def OffsetIsExpression(self, offset):
        return self.ElemIsExpression(self.GetIndexOfElemAt(offset))
    
    def ElemIsExpansionPoint(self, index):
        return self.template.IsExpansionPoint(index)
        
    def OffsetIsExpansionPoint(self, offset):
        return self.ElemIsExpansionPoint(self.GetIndexOfElemAt(offset))
        
    def ElemIsFilledExpansion(self, index):
        return self.template.IsFilledExpansion(index)
        
    def OffsetIsFilledExpansion(self, offset):
        return self.ElemIsFilledExpansion(self.GetIndexOfElemAt(offset))
    
    #############################################
    # The public interface that we use to
    # get info about this particular expression
    #############################################
    
    def SetOffset(self, offset):
        """\
        Sets the base offset for this element.
        """
        self.offsets_ok = False
        self._offset = offset
        
    def SetIndentLevel(self, level):
        """\
        Sets the indentation level for this element.
        """
        self.indent_ok = False
        self.base_indent = level
    
    def GetBlockType(self, offset):
        index = self.GetIndexOfElemAt(offset)
        if self.template.IsText(index):
            return self.TEXT
        elif self.template.IsExpansionPoint(index):
            return self.EXPANSION_POINT
        elif hasattr(self.data[index], "GetBlockType"):
            return self.EXPRESSION
        else:
            return self.INSERTION_POINT
            
    def SetElementData(self, index, data):
        """\
        Manually set element data. This could be incredibly messy if we do it
        the wrong way. But we should provide some sort of
        access from outside.
        """
        self.data[index] = data
        self.InvalidateState()
        
    def InsertExpression(self, offset, expression):
        """\
        Inserts an expression at the given offset
        """
        if not self.offsets_ok:
            self.RecalculateOffsets()
            
        type = self.GetBlockType(offset)
        if  type == self.INSERTION_POINT:
            index = self.GetIndexOfElemAt(offset)
            self.data[index] = expression
            expression.SetOffset(self.GetAbsoluteElemOffset(index))
            expression.SetIndentLevel(self.indent_level[index])
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
            
        index = self.GetIndexOfElemAt(offset);
        
        print "<%s> removing expression at offset %d" % (self.block.name, offset)
        if self.ElemIsFilledExpansion(index):    
            print "\texpression is an additional insertion point, deleting it"
            self.DeleteElement(index)
            self.InvalidateState()
        else:
            print "\texpression is text or insertion or expression"
            parent = self.GetParentOfElemAt(offset)
            if  parent != None:
                if parent == self:
                    index = self.GetIndexOfElemAt(offset)
                    self.data[index] = "*%s*" % self.template.GetElementValue(index)
                    self.InvalidateState()
                else:
                    parent.RemoveExpression(offset)            
            else:
                raise ValueError("We are the root expression, can't remove ourself!")


import random
class TpclBlockstore(object):
    """\
    Stores all TPCL Blocks and allows for searching
    and retrieval of them.
    """
    CATEGORY = 0
    BLOCK = 1
    
    #key generation random number bounds
    RAN_LOWER = 0
    RAN_UPPER = 100
    
    #######################
    # block storage
    #
    # self.root => ([category_ids], [block_ids)
    # self._items => {cat_id => category, block_id => block}
    # category => (name, [category_ids], [block_ids])
    # block => (name, block)
    ############################## 
    
    def __init__(self):
        self.root = ("Root", [], [])
        self._rootid = self._GenerateID()
        self._items = {}
        self._items[self._rootid] = root
        
    def iterblocks(self):
        return BlockstoreBlockIterator(self)
        
    def _GenerateID(self):
        #just to avoid sequential values for our
        #hash function which would completely defeat the purpose
        if self.RAN_UPPER <= len(self._items.keys()):
            self.RAN_LOWER = RAN_UPPER+1
            self.RAN_UPPER = self.RAN_UPPER * 2
        ran = random.randint(self.RAN_LOWER, self.RAN_UPPER)
        while ran in self._items.keys():
            ran = random.randint(self.RAN_LOWER, self.RAN_UPPER)
        return ran
        
    def AddCategory(self, cat_name, parent_id=None):
        """\
        Adds a category to the block store.
        """
        id = self._GenerateID()
        self._items[id] = (cat_name, [], [])
        if parent_id:
            parent_cat = self._items[parent_id]
            parent_cat[0].Append(id)
        else:
            self.root[0].Append(id)
        return id
        
    def AddBlock(self, block, category_id=None):
        """\
        Adds a block to the block store.
        With no category ID given we go to the root
        """
        id = self._GenerateID()
        self._items[id] = (block.name, block)
        if category_id:
            parent_cat = self._items[parent_id]
            parent_cat[1].Append(id)
        else:
            self.root[1].Append(id)
        return id
        
    def GetRootId(self):
        return self._rootid
        
    def GetChildren(item_id):
        pass
        
    def GetCategoryName(cat_id):
        return self._items[cat_id][0]
        
    def GetBlockName(block_id):
        return self._items[block_id][0]
    
    def GetBlock(block_id):
        block = self._items[block_id]
        return
        
class BlockstoreNode(object):
    CATEGORY = TpclBlockstore.CATEGORY
    BLOCK = TpclBlockstore.BLOCK
    def __init__(self, name, type):
        self.name = name
        self.type = type
        
    def IsCategory(self):
        return self.type == self.CATEGORY
        
    def IsBlock(self):
        return self.type == self.BLOCK
        
class CategoryNode(BlockstoreNode):
    def __init__(self, name):
        BlockstoreNode.__init__(self, name, BlockstoreNode.CATEGORY)
        self.categories = []
        self.blocks = []        
    
class BlockstoreBlockIterator(object):
    def __init__(self, blockstore):
        self.bs = blockstore
        
    def next(self):
        raise StopIteration()