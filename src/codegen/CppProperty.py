import os
from rde import ConfigManager
from game_objects import Property
from CodegenUtils import InterpolationEvaluationException, ExpressionDictionary,\
                         FormatTpclCode, ReplaceInvalidCharacters, EscapeQuotes

def GenerateCode(object_database):
    """\
    Generates C++ code for use with tpserver-cpp
    Code is placed in the .../ProjectName/code/ directory.
    """
    
    NAME = Property.GetName()
    FILENAME = NAME.lower() + "factory"
    CLASS_NAME = NAME + "Factory"
    INIT_FUNC_NAME = "init%sObjects" % NAME
    
    print "BEGINNING CODE GENERATION FOR PROPERTIES!"
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
#ifndef PROPFAC_H
#define PROPFAC_H

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
#include <tpserver/property.h>

#include <%(FILENAME)s.h>

%(CLASS_NAME)s::%(CLASS_NAME)s(){

}

""" % vars()

    CFILE.write(cpp_header)
    CFILE.flush()

    func_calls =[]
    
    #generate the code
    for prop_node in object_database.getObjectsOfType(NAME):
        prop = prop_node.GetObject()
        #NOTE:
        # we here replace hyphens with underscores in the names of properties
        # since hyphens are not valid in variable names in C++
        func_name = "init%s%s()" % (ReplaceInvalidCharacters(prop.name), NAME)
        func_calls.append("%s;" % func_name)
        
        #write to header file
        HFILE.write("  void %s;\n" % func_name)
        HFILE.flush()
        
        #write to cpp file
        FORMATTED_TPCL_DISPLAY = EscapeQuotes(FormatTpclCode(prop.tpcl_display))
        FORMATTED_TPCL_REQUIRES = EscapeQuotes(FormatTpclCode(prop.tpcl_requires))
        CFILE.write("""\
void %(CLASS_NAME)s::%(func_name)s {
  Property* prop = new Property();
  DesignStore *ds = Game::getGame()->getDesignStore();

  prop->setRank(%(prop.rank)s);
  prop->setName("%(prop.name)s");
  prop->setDisplayName("%(prop.display_text)s");
  prop->setDescription("%(prop.description)s");
  prop->setTpclDisplayFunction("%(FORMATTED_TPCL_DISPLAY)s");
  prop->setTpclRequirementsFunction("%(FORMATTED_TPCL_REQUIRES)s");""" % ExpressionDictionary(vars()))
  
        #now the categories
        for catname in prop.categories:
            CFILE.write('  prop->addCategoryId(ds->getCategoryByName("%s"));\n' % catname)            
            
        CFILE.write("""\
  ds->addProperty(prop);
  return;
}

""")
        CFILE.flush()
        prop_node.ClearObject()
    
    HFILE.write("""\
};

#endif
""")
    HFILE.flush()
    
    #finish up by adding the initProperties function
    CFILE.write('void %(CLASS_NAME)s::%(INIT_FUNC_NAME)s() {\n' % vars())
    for call in func_calls:
        CFILE.write("  %(call)s\n" % vars())
    CFILE.write('  return;\n}\n')
    CFILE.flush()
    
    CFILE.close()
    HFILE.close()
    
    print "ALL DONE GENERATING CODE FOR PROPERTIES!"