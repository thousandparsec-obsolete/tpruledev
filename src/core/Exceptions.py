"""
Custom exceptions used by the RDE
"""

class NoSuchTypeError(Exception):
    """\
    Used to indicate that an object type that was used is not valid.
    """
    
class DuplicateObjectError(Exception):
    """\
    Used to indicate that an object name is already in use if an attempt
    is made to create another.
    """
    
class NoSuchObjectError(Exception):
    """\
    Used to indicate that an object that was requested does not exist.
    """
    
class NoSuchIDError(Exception):
    """\
    Used to indicate that an ID used in a function call was invalid.
    """
    
class DuplicateProjectError(Exception):
    """\
    Used to indicate that a project already exists in a location when trying
    to create or move another one at that location.
    """