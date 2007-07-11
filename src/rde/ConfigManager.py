"""\
ConfigManager for the RDE.
"""

from ConfigParser import ConfigParser

NUM_STORED_PROJECTS = 5

config = None
project_history = []

def LoadRDEConfig(file_location):
    """\
    Loads the configuration data from the given file, appending
    it to any data that has already been loaded
    """
    global config
    global project_history
    if not config:
        config = ConfigParser()
    FILE = open(file_location, 'r')
    config.readfp(FILE)
    #restore the project history
    if config.has_option('Global', 'project_history'):
        project_history = eval(config.get('Global', 'project_history'))
    
def LoadProjectConfig(file_location):
    """\
    Load a project's configuration
    """
    global config
    if not config:
        config = ConfigParser()
    FILE = open(file_location, 'r')
    config.readfp(FILE)
    
def WriteRDEConfig(file_location):
    """\
    Writes out the RDE's configuration sections
    """
    global config
    global project_history
    #insert updated last file list into the Config
    config.set("Global", "project_history", project_history.__repr__())
    #write out the file
    WriteConfigData(file_location, ["Global", "Object Types"])
    
def WriteProjectConfig(file_location):
    """\
    Writes out the current project's configuration sections
    """
    WriteConfigData(file_location, ["Current Project"])    

def WriteConfigData(file_location, sections=None):
    """\
    Writes out the stored configuration data. Sections
    is a list of the sections to write out. If it is not
    None then only those sections will be written out,
    otherwise all sections will be written.
    """
    global config
    if sections != None:
        import copy
        conf = copy.deepcopy(config)
        if not isinstance(sections, list):
            sections = [sections]
        for sec in conf.sections():
            if not sec in sections:
                conf.remove_section(sec)
        FILE = open(file_location, 'w')
        conf.write(FILE)
    else:
        FILE = open(file_location, 'w')
        config.write(FILE)
    pass
    
def AddToProjectHistory(proj_info):
    """\
    Takes a tuple of (project_name, project_config_location)
    and adds it to the project history, removing the oldest
    entry if we are already at the maximum number of stored
    projects.
    """
    global project_history
    print "Inserting %s into project history: %s" % (proj_info, project_history)
    last_idx = -1
    try:
        last_idx = project_history.index(proj_info)        
    except ValueError:
        pass
        
    if last_idx > -1 or len(project_history) >= NUM_STORED_PROJECTS:
        project_history.pop(last_idx)
    project_history.insert(0, proj_info)
    print "Result - project history: %s" % project_history

def GetProjectHistory():
    """\
    Returns the project history as a list of
    (project_name, project_config_location) tuples.
    """
    global project_history
    return project_history

def GetSection(section):
    """\
    Convenience function that returns an object that knows
    about only the section requested.
    """
    global config
    if config.has_section(section):
        return ConfigSection(config, section)
    else:
        raise KeyError("No such section")
    
def ConfigSection(object):
    def __init__(self, config, section):
        self.config = config
        self.section = section
        
    def get(self, option):
        return self.config.get(self.section, option)
        
    def items(self):
        return self.config.items(self.section)
        
    def set(self, option, value):
        self.config.set(self.section, option, value)
        
    def options(self):
        return self.config.options()
    
    def has_option(option):
        return self.config.has_option(self.section, option)