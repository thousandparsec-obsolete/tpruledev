"""
ObjectManagement.py
Manager of game objects. Specifically, this is the model
of our object data and also the controller (meh).
"""

import os

class ObjectManager:
    def __init__(self, save_location, tree=None):
        self.save_location = save_location
        self.tree = tree
        self.objects = {}
        self.object_modules = {}
        return

    """
    fills the treectrl in the main window with
    the objects loaded from persistence
    """
    def populateTree(self, tree=None):
        if (tree):
            self.tree = tree

        #TODO add a check here for a non-None tree

        root = tree.GetRootItem()
        for name, module in self.object_modules.iteritems():
            main_node = tree.AppendItem(root, name)
            tree.SetPyData(main_node, module)

            for obj in self.objects[name]:
                object_node = tree.AppendItem(main_node, obj.name)
                tree.SetPyData(object_node, obj)
            

    def initObjectTypes(self):
        #print "Trying to initialize object types"
        cfg_filename = "objects.cfg"
        #TODO following line prone to breaking likely...fix it
        OBJECT_FILE = open(os.getcwd() + "/game_objects/" + cfg_filename, "r")
        object_modules = {}
        for name in OBJECT_FILE:
            name = name.strip()
            object_modules[name] = __import__("game_objects." + name, globals(), locals(), [''])
        return object_modules

    def loadObjectsFromStorage(self):
        #print "Trying to dynamically load objects from storage"
        self.object_modules = self.initObjectTypes()
        for name, module in self.object_modules.iteritems():
            print "Loading objects of type: " + name
            self.objects[name] = []
            persistence_dir = os.getcwd() + "/persistence/" + name
            files = os.listdir(persistence_dir)
            for f in files:
                #print "Loading File: ", f
                self.objects[name].append(module.Object(file=persistence_dir + "/" + f))
            #print "Object list:"
            #for o in self.objects[name]:
            #    print o

    def add(self, obj_type, obj):
        if not self.objects.has_key(obj_type):
            self.objects[obj_type] = []
        self.objects[obj_type].append(obj)

    def remove(self, obj_type, obj):
        try:
            self.objects[obj_type].remove(obj)
        except:
            #no such object - so...uh...through an exception, hey?
            print "No such object to be removed."

