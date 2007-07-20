"""\
The validation and evaluation functions
for Property TPCL code.
"""

import pyscheme as scheme
from pyscheme.symbol import Symbol
from pyscheme.error import SchemeError
import copy
import tpcl

PROP_ENV = None

def TpclCodeIsValid(prop):
    """\
    Checks the TPCL code for the given component.
    Returns boolean indicating whether an error is present or not.
    """
    interp = tpcl.GetInterpreter()
    old_env = interp.get_environment()
    new_env = GetPropertyEnv()
    interp._env = new_env
    #actually check the code
    #check the tpcl requirements function
    valid = True
    if not tpcl.TpclSyntaxIsValid(prop.tpcl_display):
        prop.errors['tpcl_display'] = "Syntax error"
        valid = False
    else:
        expression = "(let ((bits (list 0))) (%s design bits))" % prop.tpcl_display
        try:
            interp.eval(scheme.parse(expression))
        except SchemeError, e:
            print "In Property TPCL Validate:"
            print "\tTPCL Code invalid - %s" % e.message
            print "\t\tcode:<%s>" % expression
            prop.errors['tpcl_display'] = e.message
            valid = False
            
    if not tpcl.TpclSyntaxIsValid(prop.tpcl_requires):
        prop.errors['tpcl_requires'] = "Syntax error"
        valid = False
    else:
        try:
            interp.eval(scheme.parse("(%s design)" % prop.tpcl_requires))
        except SchemeError, e:
            prop.errors['tpcl_requires'] = e.message
            valid = False
            
    interp._env = old_env
    return valid
    
def GetPropertyEnv():
    global PROP_ENV
    if not PROP_ENV:
        #we have to define symbols so that we don't get eval errors
        PROP_ENV = tpcl.GetBaseEnvironment()
        #define the design variable
        scheme.environment.defineVariable(Symbol('design'), {}, PROP_ENV)
    return PROP_ENV