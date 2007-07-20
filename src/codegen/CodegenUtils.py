class InterpolationEvaluationException(KeyError):
    """\
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496885
    """
    pass 

class ExpressionDictionary(dict):
    """\
    A lightweight and powerful way to evaluate expressions embedded in strings during interpolation.
    
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496885
    """
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            try:
                return eval(key,self)
            except Exception, e:
                raise InterpolationEvaluationException(key, e)
                
def ReplaceInvalidCharacters(name):
    name = name.replace('-', '_')
    return name.replace(' ', '_')
    
def EscapeQuotes(text):
    return text.replace('"', '\\"')

import re
tpcl_regex = re.compile('\s*\r?\n\s*')
def FormatTpclCode(code):
    global tpcl_regex
    return " ".join(tpcl_regex.split(code))