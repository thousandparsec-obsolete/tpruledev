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
        from rde.ConfigManager import ConfigManager
        file = os.path.join(ConfigManager.config.get('Global', 'tprde_dir'),
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
        from rde.ConfigManager import ConfigManager
        file = os.path.join(ConfigManager.config.get('Global', 'tprde_dir'),
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
                else:
                    template.AppendBlockElement(elem.get('val'))
            blocks[type][name] = (tpcl_block)
    return blocks
