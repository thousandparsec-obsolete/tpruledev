import os
#from elementtree.ElementTree import ElementTree

import codegen.XmlUtils
ET = codegen.XmlUtils.ImportElementTree()
from tpcl.Representation import TpclBlocktype, TpclBlock, TpclTemplate
from tpcl.BlockManagement import TpclBlockstore
   
def InitializeBlockstore(filename=None):
    if not filename:
        from rde import ConfigManager
        filename = os.path.join(ConfigManager.config.get('Global', 'tprde_dir'),
                            'tpcl', 'data', 'tpcl_base.xml')
                            
    et = ET.ElementTree(file=filename)
    bs = TpclBlockstore()
    category_stack = []
    for cat_elem in et.findall('category'):
        ReadCategory(cat_elem, bs, category_stack)
    return bs
        
def ReadCategory(element, bs, category_stack):
    cid = 0
    if len(category_stack):
        parent_id = category_stack[-1]
    else:
        parent_id = 0
        
    cid = bs.AddCategory(element.get('name'), parent_id)
                
    category_stack.append(cid)
        
    for cat_elem in element.findall('category'):
        ReadCategory(cat_elem, bs, category_stack)
        
    for expr_elem in element.findall('expression'):
        ReadExpression(expr_elem, bs, category_stack)
        
    category_stack.pop()
    
def ReadExpression(expr_elem, bs, category_stack):
    name = expr_elem.get('name')
    description = expr_elem.get('description')
    if not description:
        description = expr_elem.findtext('multiline_desc')
    tpcl_block = TpclBlock(name, description)
    template_elem = expr_elem.find('template')
    if template_elem:
        tpcl_block.template = ReadTemplate(template_elem)
    else:
        raise ValueError("No template for expression: %s" % name)
    tpcl_block.on_insert = expr_elem.findtext('oninsert')
    tpcl_block.expansion_menu = expr_elem.findtext('expansion_menu')
    
    if len(category_stack):
        parent_id = category_stack[-1]
    else:
        parent_id = 0
    bs.AddBlock(tpcl_block, parent_id)
    
def ReadTemplate(template_elem):
    if not template_elem:
        return None
        
    template = TpclTemplate()
    for elem in template_elem.findall('elem'):
        if elem.get('type') == "text":
            template.AppendText(elem.get('val'))
        elif elem.get('type') == "eol":
            template.AppendEol()
        elif elem.get('type') == "indent":
            template.AppendIndent()
        elif elem.get('type') == "exp_point":
            option_list = []
            for item in elem.findall('menu_option'):
                name = item.get('name')
                if item.get('close_expansion'):
                    option_list.append((name, False, ReadTemplate(item.find('template'))))
                else:
                    t_elem = item.find('template')
                    if t_elem:
                        option_list.append((name, True, ReadTemplate(t_elem)))
                    else:
                        raise ValueError("ExpPoint item %s doesn't have template" % name)
            template.AppendExpansionPoint(option_list)
        else:
            template.AppendInsertionPoint(elem.get('val'))
    return template