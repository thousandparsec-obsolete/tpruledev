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