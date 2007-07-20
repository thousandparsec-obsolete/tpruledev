"""\
The stuff we need to work with TPCL in our environment.
"""

import pyscheme as scheme
import codegen.CodegenUtils
import copy

interp = None
base_env = None

def GetInterpreter():
    """\
    Get the interpreter for TPCL code. Here we can add any
    variables that we need to and make any changes that are
    neccessary for the propert interpretation of TPCL code.
    
    The interpreter follows the singletone pattern, so we
    get it once and set global variables once. Note that we
    must be careful, then, of bleed-over from other uses.
    """
    global interp
    global base_env
    if not interp:
        interp = scheme.make_interpreter()
        base_env = interp.get_environment()
    return interp

def GetBaseEnvironment():
    global base_env
    if not base_env:
        GetInterpreter()
    return base_env    

def TpclSyntaxIsValid(tpcl_code):
    """\
    Ensures that the given piece of TPCL code is syntactically
    valid. Returns True if correct syntax, false otherwise
    
    This will be improved in the future.
    """
    try:
        scheme.parse(tpcl_code)
        return True
    except scheme.parser.ParserError, e:
        return False
    