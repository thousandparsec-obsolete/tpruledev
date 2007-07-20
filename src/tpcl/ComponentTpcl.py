"""\
The validation and evaluation functions
for Component TPCL code.
"""

import pyscheme as scheme
from pyscheme.symbol import Symbol
from pyscheme.error import SchemeError
import copy
import tpcl

COMP_ENV = None

def TpclCodeIsValid(comp):
    """\
    Checks the TPCL code for the given component.
    Returns boolean indicating whether an error is present or not.
    """
    interp = tpcl.GetInterpreter()
    old_env = interp.get_environment()
    new_env = GetComponentEnv(comp.node.object_database)
    interp._env = new_env
    #actually check the code
    #check the tpcl requirements function
    valid = True
    if not tpcl.TpclSyntaxIsValid(comp.tpcl_requirements):
        comp.errors['tpcl_requirements'] = "Syntax error"
        valid = False
    else:
        try:
            interp.eval(scheme.parse("(%s design)" % comp.tpcl_requirements))
        except SchemeError, e:
            comp.errors['tpcl_requirements'] = e.message
            valid = False
    
    #check the tpcl cost functions
    cost_msg = "Cost Function Errors:"
    err_in_cost = False
    for prop_name, cost_func in comp.properties.iteritems():
        if not tpcl.TpclSyntaxIsValid(cost_func):
            cost_msg = cost_msg + "\n   %s - Syntax error" % prop_name
            err_in_cost = True
        else:
            try:
                interp.eval(scheme.parse("(%s design)" % cost_func))
            except SchemeError, e:
                cost_msg = cost_msg + "\n   %s - %s" % (prop_name, e.message)
                err_in_cost = True
    if err_in_cost:
        comp.errors['properties'] = cost_msg
        valid = False
        
    interp._env = old_env
    return valid
    
def GetComponentEnv(object_database):
    global COMP_ENV
    if not COMP_ENV:
        #we have to define symbols so that we don't get eval errors
        COMP_ENV = tpcl.GetBaseEnvironment()
        #define the design variable
        scheme.environment.defineVariable(Symbol('design'), {}, COMP_ENV)
        #add property accessors for every property
        print "Setting up designtype accessors in Component environment"
        for node in object_database.getObjectsOfType("Property"):
            print "\tMaking accessor for %s" % node.name
            def t(design):
                return 0
            scheme.builtins.installPythonFunction('designtype.' + node.name, t, COMP_ENV)
    return COMP_ENV