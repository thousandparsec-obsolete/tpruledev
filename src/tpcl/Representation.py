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
        

class TpclTemplateNode(object):
    """\
    Container class for all TpclTemplate data.
    
    We track the original value here, as well
    as the original type. Offsets and indentation
    levals are stored here.
    
    We also handle padding  EOL's with indentation
    """
    
    def __init__(self, type, value, data=None):
        self.type = type
        self.value = value
        self.data = data
        self.offset = 0
        self.indent_level = 0
        
    def GetValue(self):
        return self.__value            
        
    def SetValue(self, new_val):
        if not hasattr(self, "original_value"):
            try:
                self.original_value = self.value
            except AttributeError:
                pass
        self.__value = new_val
        
    value = property(GetValue, SetValue)
    
    def GetType(self):
        return self.__type
    
    def SetType(self, new_val):
        if not hasattr(self, "original_type"):
            try:
                self.original_type = self.type
            except AttributeError:
                pass
        self.__type = new_val
        
    type = property(GetType, SetType)
    
    def GetIndent(self):
        return self.__indent_level
        
    def SetIndent(self, value):
        try:
            if self.type == TpclTemplate.EOL:
                self.value = "\n" + ("\t" * value)
        except AttributeError:
            pass
        self.__indent_level = value
        
    indent_level = property(GetIndent, SetIndent)
        
class TpclTemplate(object):
    """\
    A template defining the structure of a block of TPCL code.
    Each TpclBlock has a template to define the structure of its
    code snippet.
    
    We keep a list of textual elements and tpcl insertion points.
    """
    TEXT = 1
    INSERTION_POINT = 2
    EXPRESSION = 4
    INDENT = 8
    EOL = 16
    EXPANSION = 32
    ADDED = 64
    
    def __init__(self):
        self.data = []
        
    def __len__(self):
        return len(self.data)
        
    def GetElemString(self, index):
        return str(self.data[index].value)
    
    def GetElemLength(self, index):
        return len(self.data[index].value)
        
    def GetElemOffset(self, index):
        return self.data[index].offset
    
    def SetElemOffset(self, index, offset):
        self.data[index].offset = offset
    
    def GetElemIndent(self, index):
        return self.data[index].indent_level
    
    def SetElemIndent(self, index, indent):
        self.data[index].indent_level = indent
        
    def SetText(self, index, value):
        if self.IsPlaintext(index):
            self.data[index].value = value
        else:
            raise ValueError("Element at %d is not plaintext" % index)
        
    ##############################
    # Insertion methods
    ##############################
        
    def AppendText(self, text):
        self.data.append(TpclTemplateNode(self.TEXT, text))
        
    def InsertText(self, index, text):
        self.data.insert(index, TpclTemplateNode(self.TEXT, text))
        
    def AppendInsertionPoint(self, block):
        self.data.append(TpclTemplateNode(self.INSERTION_POINT, "*%s*" % block))
        
    def InsertInsertionPoint(self, index, block):
        self.data.insert(index, TpclTemplateNode(self.INSERTION_POINT, "*%s*" % block))
        
    def FillInsertionPoint(self, index, expression):
        if self.IsInsertionPoint(index):
            self.data[index].value = expression
            self.data[index].type = self.EXPRESSION
        else:
            raise ValueError("No insertion point at index %d" % index)
        
    def ResetInsertionPoint(self, index):
        if self.IsExpression(index):
            self.data[index].value = self.data[index].original_value
            self.data[index].type = self.data[index].original_type
        else:
            raise ValueError("No expression point at index %d" % index)
        
    def AppendEol(self):
        self.data.append(TpclTemplateNode(self.EOL, "\n"))
        
    def InsertEol(self, index):
        self.data.insert(index, TpclTemplateNode(self.EOL, "\n"))
        
    def AppendIndent(self):
        self.data.append(TpclTemplateNode(self.INDENT, "\t"))
        
    def InsertIndent(self, index):
        self.data.insert(index, TpclTemplateNode(self.INDENT, "\t"))
        
    #expansion options are tuples of the form (name, TpclTemplate)
    def AppendExpansionPoint(self, expansion_options):
        self.data.append(TpclTemplateNode(self.EXPANSION, "*...*", expansion_options))
        
    def InsertExpansionPoint(self, index, expansion_options):
        self.data.insert(index, TpclTemplateNode(self.EXPANSION, "*...*", expansion_options))
        
    def ExpandExpansionPoint(self, index, expr, continue_expansion):
        if self.IsExpansionPoint(index):
            if not continue_expansion:
                del self.template[index]
            self.data.insert(index, TpclTemplateNode((self.EXPRESSION | self.ADDED), expr))
        else:
            raise ValueError("No expansion point at index %d" % index)
        
    def RemoveElement(self, index):
        del self.data[index]
        
    #####################################
    # Type test methods
    #####################################
    
    def IsText(self, index):
        #Simple text, EOL and indents all count as text.
        return self.data[index].type & (self.TEXT | self.EOL | self.INDENT)
               
    def IsSimpletext(self, index):
        return self.data[index].type & self.TEXT
    
    def IsEol(self, index):
        return self.data[index].type & self.EOL
        
    def IsIndent(self, index):
        return self.data[index].type & self.INDENT
        
    def IsInsertionPoint(self, index):
        return self.data[index].type & self.INSERTION_POINT
    
    def IsExpression(self, index):
        return self.data[index].type & self.EXPRESSION
    
    def IsExpansionPoint(self, index):
        return self.data[index].type & self.EXPANSION
        
    def IsAddedInsertionPoint(self, index):
        return (self.data[index].type & self.ADDED) and \
                (self.data[index].type & self.INSERTION_POINT)
        
    #was IsFilledExpansion
    def WasAddedByExpansion(self, index):
        return (self.data[index].type & self.ADDED and \
                self.data[index].type & self.EXPRESSION)
    
    #####################################
    # Getters
    #####################################
        
    def GetNode(self, index):
        return self.data[index]
        
    def GetElementValue(self, index):
        """\
        Returns the text of the element if it's text
        or the name of the block if it's a block
        """
        return self.data[index].value
        
    def SetElementValue(self, index, value):
        self.data[index].value = value
        
    def GetElementData(self, index):
        return self.data[index].data
        
    
class TpclExpression(object):
    """\
    An actual TPCL Expression composed of text and other expressions
    """    
    
    def __init__(self, block, parent=None, offset=0, indent=0):
        self.block = block
        self.template = copy.deepcopy(block.template)
        self.parent = parent
        self._offset = 0
        self.base_indent = 0
        
        self.indent_ok = False
        self.offsets_ok = False
        self.length_ok = False
        self.string_ok = False
                
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
        for i in range(len(self.template)):
            self._length += self.template.GetElemLength(i)
        self.length_ok = True
                
    def RecalculateOffsets(self):
        """\
        Recalculates the offsets of all elements so
        that they are up to date.
        """
        if not self.indent_ok:
            self.RecalculateIndentation()
        for i in range(len(self.template)):
            offset = 0
            if i != 0:
                offset = self.template.GetElemOffset(i-1) + self.GetElemLength(i-1)
            #set our relative offset
            self.template.SetElemOffset(i, offset)
            
            if self.template.IsExpression(i):
                self.template.GetElementValue(i).SetOffset(offset + self._offset)
            
        self.offsets_ok = True
    
    def RecalculateIndentation(self):
        #pre-process the block for indent levels
        for i in range(len(self.template)):
            curr_indent = self.base_indent
            if i != 0:
                if self.template.IsEol(i):
                    curr_indent = self.base_indent
                elif self.template.IsIndent(i-1):
                    curr_indent = self.template.GetElemIndent(i-1) + 1
                else:
                    curr_indent = self.template.GetElemIndent(i-1)
                    
            self.template.SetElemIndent(i, curr_indent)
                
        self.indent_ok = True
        self.string_ok = False
        self.length_ok = False
        self.offsets_ok = False
        
    def RecalculateString(self):
        self._string = ""
        for i in range(len(self.template)):
            self._string += self.template.GetElemString(i)
        self.string_ok = True
        
    def GetIndexOfElemAt(self, offset):
        """\
        Gets the index of the element whose text is the given absolute offset
        """
        i = 0
        if offset < self._offset or self._offset + len(self) - 1 < offset:
            print "<%s> Offset %d not in this expression" % (self.block.name, offset)
            raise ValueError('Offset %d not in this expression [%d, %d].' % \
                                (offset, self._offset, self._offset + len(self) - 1))
        while i < len(self.template) - 1 and offset >= self.GetAbsoluteElemOffset(i+1):
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
            
    def GetElemLength(self, index):
        if not self.indent_ok:
            self.RecalculateIndentation()
        if not self.length_ok:
            self.RecalculateLength()
        return self.template.GetElemLength(index)
    
    def GetElemIndent(self, index):
        if not self.indent_ok:
            self.RecalculateIndentation()
        return self.template.GetElemIndent(index)
            
    def GetElemOffset(self, index):
        """\
        Gets the offset of start of the element at that
        index in our data.
        """
        if not self.indent_ok:
            self.RecalculateIndentation()
        if not self.offsets_ok:
            self.RecalculateOffsets()
        return self.template.GetElemOffset(index)
    
    def GetAbsoluteElemOffset(self, index):
        """\
        Gets the offset of start of the element at that
        index in our data.
        """
        return self.GetElemOffset(index) + self._offset
        
    def IsAddedInsertionPoint(self, offset):
        """\
        Returns boolean value indicating if the text at the 
        offset is an added insertion point
        """
        print "<%s> Checking if offset %d is an added insertion point" % (self.block.name, offset)
        index = self.GetIndexOfElemAt(offset)
        if self.template.IsExpression(index):
            print "\tIt's an expression!"
            retval = self.template.GetElementValue(index).IsAddedInsertionPoint(offset)
            if retval[0]:
                return retval
            else:
                if self.template.WasAddedByExpansion(index) and \
                   self.template.GetElementValue(index).IsInsertionPoint(offset):
                    return (True, self)
            return (False, None)
        else:
            print "\tIt's neither an expression nor an added insertion point!"
            return (False, None)
        
    def IsInsertionPoint(self, offset):
        """\
        Returns tuple indicating that the offset is an insertion
        point or not and if it is the parent expression that contains
        that expansion point
        
            retval: (bool b, TpclExpression p)
            where b indicates if the text at offset is an
            expansion point. p is the parent of 
        """
        print "<%s> Checking if offset %d is an insertion point" % (self.block.name, offset)
        index = self.GetIndexOfElemAt(offset)
        if self.template.IsInsertionPoint(index):
            print "\tIt's an insertion point!"
            return (True, self)
        elif self.template.IsExpression(index):
            print "\tIt's an expression!"
            return self.template.GetElementValue(index).IsInsertionPoint(offset)
        else:
            print "\tIt's neither an expression nor an insertion point!"
            return (False, None)
            
    def IsExpansionPoint(self, offset):
        """\
        Returns a tuple indicating whether or not the offset lies
        on an expansion point and if so, returns the parent as well.
        """
        index = self.GetIndexOfElemAt(offset)
        if self.template.IsExpansionPoint(index):
            return (True, self)
        elif self.template.IsExpression(index):
            return self.template.GetElementValue(index).IsExpansionPoint(offset)
        else:
            return (False, None)
            
    def GetExpansionOptions(self, offset):
        """\
        Returns the options for expansion at a given offset as
        a list of names.
        
        Returns None if this is not an expansion point
        """
        index = self.GetIndexOfElemAt(offset)
        if self.template.IsText(index) or self.template.IsInsertionPoint(index):
            return None
        elif self.template.IsExpansionPoint(index):
            return [o[0] for o in self.template.GetElementData(index)]
        elif self.template.IsExpression(index):
            return self.template.GetElementValue(index).GetExpansionOptions(offset)
        else:
            return None
            
    def Expand(self, offset, option):
        print "In TpclExpression <%s> trying to expand at %d with option %d" % (self.block.name, offset, option)
        index = self.GetIndexOfElemAt(offset)
        if self.template.IsText(index) or self.template.IsInsertionPoint(index):
            print "\tNot an expansion point!"
            return None
        elif self.template.IsExpression(index):
            print "\tAn expression, delving in!"
            return self.template.GetElementValue(index).Expand(offset, option)
        else:
            print "\tIt's an expansion point"
            exp_opts = self.template.GetElementData(index)[option]
            if exp_opts:
                exp_template = exp_opts[2]
                cont_exp = exp_opts[1]
                if exp_template:
                    #we are expanding
                    print "\tFound template"
                    expr = ExpansionExpression(TpclBlock("exp_point", "disp",
                                                    "desc", exp_template), parent=self)
                    print "\tExpansion expression: %s" % expr
                                                    
                    self.template.ExpandExpansionPoint(index, expr, cont_exp)
                    self.InvalidateState()
                    
                    self.RecalculateOffsets()
                    print "\tSetting offset as %d and indent level as %d" % (self.GetElemOffset(index), self.GetElemIndent(index))
                    print "\tbase_indent =", self.base_indent
                    expr.SetOffset(self.GetElemOffset(index))
                    expr.SetIndentLevel(self.GetElemIndent(index))               

                else:
                    self.DeleteElement(index)
                    
                self.InvalidateState()
                
    def DeleteElement(self, index):
        """\
        Deletes an element completely from our internal represenation
        and the template.
        """
        print "<%s> is deleting element at index %d" % (self.block.name, index)
        print "\telement: %s" % self.template.GetNode(index)
        self.template.RemoveElement(index)
        self.InvalidateState()
            
    def GetParentOfElemAt(self, offset):
        """\
        Returns the parent of the element at the offset.
        """
        index = self.GetIndexOfElemAt(offset)
        if self.template.IsText(index):
            return self.parent
        elif self.template.IsInsertionPoint(index) or self.template.IsExpansionPoint(index):
            return self
        else:
            return self.template.GetElementValue(index).GetParentOfElemAt(offset)
    
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
        
    ##############################
    def SetText(self, index, new_val):
        """\
        Manually set element data. This could be incredibly messy if we do it
        the wrong way. But we should provide some sort of
        access from outside.
        """
        self.template.SetText(i, new_val)
        self.InvalidateState()
        
    def InsertExpression(self, offset, expression):
        """\
        Inserts an expression at the given offset
        """
        if not self.offsets_ok:
            self.RecalculateOffsets()
            
        index = self.GetIndexOfElemAt(offset)
        if  self.template.IsInsertionPoint(index):
            self.template.FillInsertionPoint(index, expression)
            expression.SetOffset(self.GetAbsoluteElemOffset(index))
            expression.SetIndentLevel(self.GetElemIndent(index))
            #todo: need to start guarding against multiple parents
            expression.parent = self
            self.InvalidateState()
        elif self.template.IsExpression(index):
            self.template.GetElementValue(index).InsertExpression(offset, expression)
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
        if self.template.IsAddedInsertionPoint(index):
            print "\texpression is an additional insertion point, deleting it"
            self.DeleteElement(index)
            self.InvalidateState()
        else:
            print "\texpression is text or insertion or expression"
            parent = self.GetParentOfElemAt(offset)
            if  parent != None:
                if parent == self:
                    self.template.ResetInsertionPoint(index)
                    self.InvalidateState()
                else:
                    parent.RemoveExpression(offset)            
            else:
                raise ValueError("We are the root expression, can't remove ourself!")

class ExpansionExpression(TpclExpression):
    def __init__(self, block, parent=None, offset=0, indent=0):
        TpclExpression.__init__(self, block, parent, offset, indent)
        
    def RemoveExpression(self, offset):
        """\
        Removes the expression at the given offset
        """
        if not self.offsets_ok:
            self.RecalculateOffsets()
            
        index = self.GetIndexOfElemAt(offset);
        
        print "<%s> (EE) removing expression at offset %d" % (self.block.name, offset)
        if self.template.IsAddedInsertionPoint(index) or self.template.IsText(index):
            print "\texpression is an additional insertion point, deleting ourselves and it"
            myidx = self.parent.GetIndexOfElemAt(offset)
            self.parent.DeleteElement(myidx)
            self.parent.InvalidateState()
        else:
            parent = self.GetParentOfElemAt(offset)
            if  parent != None:
                if parent == self:
                    self.template.ResetInsertionPoint(index)
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