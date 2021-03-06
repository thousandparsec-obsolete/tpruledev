import os
from rde import ConfigManager
from game_objects import Category
from CodegenUtils import InterpolationEvaluationException, ExpressionDictionary, ReplaceInvalidCharacters

def GenerateCode(object_database):
    """\
    Generates C++ code for use with tpserver-cpp
    Code is placed in the .../ProjectName/code/ directory.
    """
    
    NAME = Category.GetName()
    FILENAME = NAME.lower() + "factory"
    CLASS_NAME = NAME + "Factory"
    INIT_FUNC_NAME = "init%sObjects" % NAME
    
    print "BEGINNING CODE GENERATION FOR CATEGORIES!"
    outdir = os.path.join(ConfigManager.config.get('Current Project', 'project_directory'), 'code')
    if not os.path.exists(outdir):
        os.makedirs(outdir)
                                               
    #we make two files, a header and a cpp file
    hfile_path = os.path.join(outdir, "%s.h" % FILENAME)
    cfile_path = os.path.join(outdir, "%s.cpp" % FILENAME)

    HFILE = open(hfile_path, 'w')
    CFILE = open(cfile_path, 'w')
    
    
    
    h_header = \
"""\
#ifndef CATEFAC_H
#define CATEFAC_H

class %(CLASS_NAME)s {
 public:
  %(CLASS_NAME)s();
  
  void %(INIT_FUNC_NAME)s();
  
 private:
""" % vars()

    HFILE.write(h_header)
    HFILE.flush()
    
    cpp_header = \
"""\
#include <tpserver/game.h>
#include <tpserver/designstore.h>
#include <tpserver/category.h>

#include <%(FILENAME)s.h>

%(CLASS_NAME)s::%(CLASS_NAME)s(){

}

""" % vars()
    CFILE.write(cpp_header)
    CFILE.flush()

    func_calls =[]
    
    #generate the code
    for cat_node in object_database.getObjectsOfType(NAME):
        cat = cat_node.GetObject()
        func_name = "init%s%s()" % (ReplaceInvalidCharacters(cat.name), NAME)
        func_calls.append("%s;" % func_name)
        
        #write to header file
        HFILE.write("  void %s;\n" % func_name)
        HFILE.flush()
        
        #write to cpp file
        CFILE.write("""\
void %(CLASS_NAME)s::%(func_name)s {
  Category* cat = new Category();
  DesignStore *ds = Game::getGame()->getDesignStore();

  cat->setName("%(cat.name)s");
  cat->setDescription("%(cat.description)s");
  ds->addCategory(cat);
  return;
}

""" % ExpressionDictionary(vars()))
        CFILE.flush()
        cat_node.ClearObject()
    
    HFILE.write('};\n#endif\n')
    HFILE.flush()
    
    #finish up by adding the initProperties function
    CFILE.write('void %(CLASS_NAME)s::%(INIT_FUNC_NAME)s() {\n' % vars())
    for call in func_calls:
        CFILE.write("  %s\n" % call)
    CFILE.write('  return;\n}\n')
    CFILE.flush()
    
    CFILE.close()
    HFILE.close()
    
    print "ALL DONE GENERATING CODE FOR CATEGORIES!"