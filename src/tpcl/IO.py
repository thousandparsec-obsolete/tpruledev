import os
#from elementtree.ElementTree import ElementTree

import codegen.XmlUtils
ET = codegen.XmlUtils.ImportElementTree()
from tpcl.Representation import TpclBlocktype, TpclBlock, TpclTemplate
from tpcl.BlockManagement import TpclBlockstore
from rde.Exceptions import *

def ConstructExpression(block_store, xml_expr_elem=None, expr_str=""):
    """\
    Constructs a TPCL Expression from a persistence definition
    that has been written to XML
    """
    
    if expr_str and xml_expr_elem:
        raise ValueError("Must pass either a string or an XML element, not both")
    elif expr_str:
        #process string
        return ExpressionFromXml(block_store, ET.fromstring(expr_str))
    elif xml_expr_elem:
        #process xml element
        return ExpressionFromXml(block_store, xml_expr_elem)
    else:
        return None
        
def ExpressionFromXml(block_store, expr):
    """\
    Constructs a complext expression from its persistence XML
    Returns a TPCL Expression
    """
    if expr.tag != "expression":
        raise MalformedXmlError("Not a valid expression XML format - expression tag isn't main tag")
        
    block_id = elem.get("block_id")
    if not block_id:
        raise MalformedXmlError("Not a valid expression XML format - No block_id")
    
    base_expression = TpclExpression(block_store.GetBlock(int(block_id)))    
    ProcessSubExpressions(block_store, expr, base_expression)
    return base_expression
    

def ProcessSubExpressions(block_store, expr, parent):
    for subexpr in expr.findall("subexpression"):
        block_id = subexpr.get("block_id")
        if not block_id:
            raise MalformedXmlError("Not a valid expression XML format - No block_id")
        idx = subexpr.get("index")
        if not idx:
            raise MalformedXmlError("Not a valid expression XML format - No index")
            
        sub = TpclExpression(block_store.GetBlock(int(block_id)), parent)
        ProcessSubExpressions(block_store, subexpr, sub)
        
        parent._InsertExpressionAt(int(idx), sub)
        
    for expansionexpr in expr.findall("expansion_expression"):
        expansion_option = expansionexpr.get("expansion_option")
        if not expansion_option:
            raise MalformedXmlError("Not a valid expression XML format - No expansion_option")
        idx = expansionexpr.get("index")
        if not idx:
            raise MalformedXmlError("Not a valid expression XML format - No index")
            
        parent._ExpandElement(int(idx), int(expansion_option))
        ProcessSubExpressions(block_store, expansionexpr, parent._GetElement(int(idx)))
   
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