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
    test_code = """(lambda (design) 
	(if (= (designType._num-components design) 1) 
		(cons #t \\"\\") 
		(cons #f \\"This is a complete component, nothing else can be included\\")))"""
    if tpcl_code == test_code:
        print "FOUND TEST CODE MATCH!"
    else:
	    print "len(tpcl_code) = %d, len(test_code) = %d" % (len(tpcl_code), len(test_code))
	    if len(tpcl_code) == 160:
	        print "tpcl_code\ttest_code:"
	        for i in range(len(test_code)):
	            print "%d: %s\t%s" % (i, tpcl_code[i], test_code[i])
    try:
        scheme.parse(tpcl_code)
        return True
    except scheme.parser.ParserError, e:
        print e, e.args
        print "Invalid Scheme syntax: <%s> [-] <%s>" % (tpcl_code, e.message)
        return False
    