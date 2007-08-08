import os
from elementtree.ElementTree import ElementTree
from tpcl.Representation import TpclBlocktype, TpclBlock

def LoadBlocktypes(filename=None):
    """\
    Returns a hash containing all of the blocktypes
    that have been defined.
    """
    
    #good golly miss molly but this code is inefficient and not fun
    
    if not filename:
        from rde import ConfigManager
        filename = os.path.join(ConfigManager.config.get('Global', 'tprde_dir'),
                            'tpcl', 'data', 'blocktypes.xml')
    et = ElementTree(file=filename)
    blocktypes = {}
    for blocktype in et.findall('tpcl_blocktype'):
        name = blocktype.get('name')
        description = blocktype.get('description')
        members = []
        for member in blocktype.findall('member'):
            members.append(member.get('name'))
        blocktypes[name] = (TpclBlocktype(name, description), members)
    
    bt = {}    
    for name, (btype, mlist) in blocktypes.iteritems():
        for mname in mlist:
            btype.AddMember(blocktypes[mname][0])
        bt[name] = btype
    del blocktypes
    return bt
    
def LoadBlocks(filename=None):
    """\
    Returns a hash containing all of the blocks
    that have been defined.
    """
    
    if not filename:
        from rde import ConfigManager
        filename = os.path.join(ConfigManager.config.get('Global', 'tprde_dir'),
                            'tpcl', 'data', 'base_blocks.xml')
    et = ElementTree(file=filename)
    blocks = {}
    for blocktype in et.findall('type'):
        type = blocktype.get('name')
        blocks[type] = {}
        for block in blocktype.findall('tpcl_block'):
            name = block.get('name')
            description = block.get('description')
            display = block.get('display')
            tpcl_block = TpclBlock(name, type, description, display)
            template = tpcl_block.template
            temp = block.find('template')
            for elem in temp.findall('elem'):
                if elem.get('type') == "text":
                    template.AppendTextElement(elem.get('val'))
                elif elem.get('type') == "eol":
                    template.AppendEolElement()
                elif elem.get('type') == "indent":
                    template.AppendIndentElement()
                else:
                    template.AppendBlockElement(elem.get('val'))
            blocks[type][name] = (tpcl_block)
    return blocks
    
def LoadBlockIntoTree(tree, filename=None):
    """\
    Bloody mess to only be used during testing.
    
    Manually fills a tree with the blocks, setting
    PyData to the TpclBlock objects for each block
    that we load.
    """
    
    if not filename:
        from rde import ConfigManager
        filename = os.path.join(ConfigManager.config.get('Global', 'tprde_dir'),
                            'tpcl', 'data', 'tpcl_base.xml')
    et = ElementTree(file=filename)
    blocks = {}
    root = tree.AddRoot("Root")
    for cat_elem in et.findall('category'):
        ReadCategory(cat_elem, tree)

def ReadCategory(element, tree, parent_id=None):
    cid = 0
    if parent_id:
        cid = tree.AppendItem(parent_id, element.get('name'))
    else:
        cid = tree.AppendItem(tree.GetRootItem(), element.get('name'))
        
    for cat_elem in element.findall('category'):
        ReadCategory(cat_elem, tree, cid)
        
    for expr_elem in element.findall('expression'):
        ReadExpression(expr_elem, tree, cid)

def ReadExpression(expr_elem, tree, cat_id):
    name = expr_elem.get('name')
    expr_id = tree.AppendItem(cat_id, name)
    description = expr_elem.get('description')
    display = expr_elem.get('display').replace("\\n", "\n").replace("\\t", "\t")
    tpcl_block = TpclBlock(name, type, description, display)
    template = tpcl_block.template
    temp = expr_elem.find('template')
    if not temp:
        raise ValueError("Expression %s has no template!" % name)
    for elem in temp.findall('elem'):
        if elem.get('type') == "text":
            template.AppendTextElement(elem.get('val'))
        elif elem.get('type') == "eol":
            template.AppendEolElement()
        elif elem.get('type') == "indent":
            template.AppendIndentElement()
        elif elem.get('type') == "exp_point":
            template.AppendExpansionElement()
        else:
            template.AppendBlockElement(elem.get('val'))
    tpcl_block.on_insert = expr_elem.findtext('oninsert')
    tpcl_block.expansion_menu = expr_elem.findtext('expansion_menu')
    
    tree.SetPyData(expr_id, tpcl_block)