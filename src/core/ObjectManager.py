"""
ObjectManager.py
Manager of game objects. Specifically, this is the model
of our object data and also the controller (meh).
"""

class ObjectManger:
    def __init__(self, save_location, tree=None):
        self.save_location = save_location
        telf.tree = tree
        self.objects = {}
        return
    
    def setSaveLocation(self, save_location):
        self.save_location = save_location
        
    def setTreeRoot(self, tree):
        self.tree = None

    def add(self, type, obj):
        if not self.objects.has_key(type):
            self.objects[type] = []
        self.objects[type].append(obj)

    def remove(self, type, obj):
        try:
            del self.objects[type].remove(obj)
        except:
            #no such object

