"""
ProjectManagement.py

Utilities dealing with the creation, maintenence and moving of RDE Projects.
"""

import os
from Exceptions import DuplicateProjectError

def createNewProject(parent_dir, name, obj_types):
    """\
    Initializes a project directory for the project with name, name, in
    the directory parent_dir. A tprde.cfg file is created as well as
    a persistence directory and subdirectories for each game object type.
    """
    parent_path = parent_dir + '/'
    #check for pre-existing project
    if os.path.exists(parent_path + name):
        raise DuplicateProjectError(parent_path + name)
        
    #create directory structure
    os.mkdir(os.path.join(parent_path, name))
    os.mkdir(os.path.join(parent_path, name, 'persistence'))
    for type in obj_types:
        os.mkdir(os.path.join(parent_path, name, 'persistence', type))
    
    #make our config file
    generateConfigFile(os.path.join(parent_path + name), name)
    
def generateConfigFile(project_dir, name):
    """\
    Generate a configuration file for the project with name, name and a project
    directory of project_dir
    """
    CONF_FILE = open(os.path.join(project_dir, 'tprde.cfg'), 'w')
    CONF_FILE.write('#tpruledev project configuration file\n')
    CONF_FILE.write('\n')
    CONF_FILE.write('[Current Project]\n')
    CONF_FILE.write('project_name:	' + name + '\n')
    CONF_FILE.write('project_directory:	' + project_dir + '\n')
    CONF_FILE.write('persistence_directory: %(project_directory)s' + os.sep + 'persistence\n')
    CONF_FILE.flush()
    CONF_FILE.close()
    
def deleteProject(conf_file):
    """\
    Delete an existing project.
    
    Adapted from the Python Library Reference - http://docs.python.org/lib/os-file-dir.html
    """
    CIN = open('conf_file', 'r')
    if CIN.readline() == "#tpruledev project configuration file\n":
        top = conf_file[:len(conf_file)-9]
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(top)
    
def moveProject(conf_file, new_parent_dir):
    """\
    Move an existing project to a new location.
    """
    pass
    
def updateProjectObjects(conf_file, obj_types):
    """\
    Make sure that there are persistence directories for each
    object type if any new object types have been added to the
    RDE since this project was created.
    """
    pass