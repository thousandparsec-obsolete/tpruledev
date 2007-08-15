class TpclBlockstore(object):
    """\
    Stores all TPCL Blocks and allows for searching
    and retrieval of them.
    """
    CATEGORY = 0
    BLOCK = 1
    
    #######################
    # block storage
    #
    # self.root => ([category_ids], [block_ids)
    # self._items => [category, block, ...}
    # category => (name, [category_ids], [block_ids])
    # block => (name, block)
    ############################## 
    
    def __init__(self):
        self.root = CategoryNode(0, None, "Root")
        self._items = [self.root]
        self._rootid = 0
        
    def iterblocks(self):
        return BlockstoreBlockIterator(self)
        
    def AddCategory(self, cat_name, parent_id=0):
        """\
        Adds a category to the block store.
        """
        id = len(self._items)
        self._items[parent_id].AddCategory(id)
        self._items.append(CategoryNode(id, parent_id, cat_name))
        return id
        
    def AddBlock(self, block, parent_id=0):
        """\
        Adds a block to the block store.
        With no category ID given we go to the root
        """
        id = len(self._items)
        self._items[parent_id].AddBlock(id)
        
        self._items.append(BlockNode(id, parent_id, block))
        return id
        
    def GetRootId(self):
        return self._rootid
        
    def GetChildCategories(self, item_id):
        item = self._items[item_id]
        if item.IsCategory():
            return item.categories
        else:
            return None
            
    def GetChildBlocks(self, item_id):
        item = self._items[item_id]
        if item.IsCategory():
            return item.blocks
        else:
            return None
        
    def GetItemName(self, item_id):
        return self._items[item_id].name
        
    def GetNode(self, item_id):
        return self._items[item_id]
    
    def GetBlock(self, block_id):
        """\
        Returns the TpclBlock associated with
        the given block_id
        """
        block = self._items[block_id]
        return block.block

    def GetParent(self, item_id):
        return self._items[item_id].parent_id
        
    def FindBlock(self, name, parent_id=0):
        """\
        Returns the id of the first TPCL Block found whose name
        matches that given
        """
        for block_id in self.GetChildBlocks(parent_id):
            block = self.GetBlock(block_id)
            if block.name == name:
                return block_id
        
        for cat_id in self.GetChildCategories(parent_id):
            retval = self.FindBlock(name, cat_id)
            if retval:
                return retval
        
        return False
        
    def FindCategory(self, name, parent_id=0):
        """\
        Returns the id of the first category whose name
        matches the one given
        """
        for cat_id in self.GetChildCategories(parent_id):
            if self.GetItemName(cat_id) == name:
                return cat_id
                
        for cat_id in self.GetChildCategories(parent_id):
            retval = self.FindCategory(name, cat_id)
            if retval:
                return retval
        
        return False
        
class BlockstoreNode(object):
    CATEGORY = TpclBlockstore.CATEGORY
    BLOCK = TpclBlockstore.BLOCK
    
    def __init__(self, id, parent_id, name, type):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.type = type
        
    def IsCategory(self):
        return self.type == self.CATEGORY
        
    def IsBlock(self):
        return self.type == self.BLOCK
        
class CategoryNode(BlockstoreNode):
    def __init__(self, id, parent_id, name):
        BlockstoreNode.__init__(self, id, parent_id, name, BlockstoreNode.CATEGORY)
        self.categories = []
        self.blocks = []
        
    def AddCategory(self, cat_id):
        self.categories.append(cat_id)
    
    def AddBlock(self, block_id):
        self.blocks.append(block_id)
        
class BlockNode(BlockstoreNode):
    def __init__(self, id, parent_id, block):
        BlockstoreNode.__init__(self, id, parent_id, block.name, BlockstoreNode.BLOCK)
        self.block = block
    
    
class BlockstoreBlockIterator(object):
    """\
    Iterator for a blockstore
    Iterates through the elements of the blockstore in pre-order.
    """
    def __init__(self, blockstore):
        self.bs = blockstore
        self.node_stack = [IteratorNode(id, True) for id in \
                                self.bs.GetChildCategories(self.bs.GetRootId())]
        self.node_stack.extend([IteratorNode(id, False) for id in \
                                self.bs.GetChildBlocks(self.bs.GetRootId())])
        self.node_stack.reverse()
        print "Node stack", self.node_stack
        
    def __iter__(self):
        return self
        
    def next(self):
        if self.node_stack:
            node = self.node_stack.pop()
            print "Node:", node
            if node.has_children:
                block_children = [IteratorNode(id, False) for id in \
                                    self.bs.GetChildBlocks(node.id)]
                block_children.reverse()
                cat_children = [IteratorNode(id, True) for id in \
                                self.bs.GetChildCategories(node.id)]
                cat_children.reverse()
                self.node_stack.extend(block_children)
                self.node_stack.extend(cat_children)
            return self.bs.GetNode(node.id)
        else:
            raise StopIteration()
        
        
class IteratorNode(object):
    def __init__(self, id, has_children=True):
        self.id = id
        self.has_children = has_children