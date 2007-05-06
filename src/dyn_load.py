"""
dyn_load.py
    dynamic load test
"""

import os

def getObjectTypes():
    cfg_filename = "objects.cfg"
    OBJECT_FILE = open("game_objects/" + cfg_filename, "r")
    object_names = OBJECT_FILE.readlines()
    object_modules = {}
    for name in object_names:
        object_modules[name] = __import__("game_objects." + name, globals(), locals(), [''])
    return object_modules

print "Trying to dynamically load Property module"
modules = getObjectTypes()
objects = {}
for name, module in modules.iteritems():
    print "Loading objects of type: " + name
    objects[name] = []
    persistence_dir = "persistence/" + name
    files = os.listdir(persistence_dir)
    for f in files:
        print "Loading File: ", f
        objects[name].append(module.Object(file=persistence_dir + "/" + f))
    print "Object list:"
    for o in objects[name]:
        print o

