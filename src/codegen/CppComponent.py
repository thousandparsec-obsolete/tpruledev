import re, os, RDE
from game_objects import Component
from CodegenUtils import InterpolationEvaluationException, ExpressionDictionary

def GenerateCode(object_database):
    """\
    Generates C++ code for use with tpserver-cpp
    Code is placed in the .../ProjectName/code/Component directory.
    """
    
    NAME = Component.GetName()
    FILENAME = NAME.lower() + "factory"
    CLASS_NAME = NAME + "Factory"
    INIT_FUNC_NAME = "init%sObjects" % NAME
    
    print "BEGINNING CODE GENERATION FOR COMPONENTS!"
    outdir = os.path.join(RDE.GlobalConfig.config.get('Current Project', 'project_directory'), 'code')
    if not os.path.exists(outdir):
        os.makedirs(outdir)
                                               
    #we make two files, a header and a cpp file
    hfile_path = os.path.join(outdir, "%s.h" % FILENAME)
    cfile_path = os.path.join(outdir, "%s.cpp" % FILENAME)

    HFILE = open(hfile_path, 'w')
    CFILE = open(cfile_path, 'w')
    
    h_header = \
"""\
#ifndef COMPFAC_H
#define COMPFAC_H

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
#include <tpserver/component.h>

#include <%(FILENAME)s.h>

%(CLASS_NAME)s::%(CLASS_NAME)s(){

}

""" % vars()

    CFILE.write(cpp_header)
    CFILE.flush()

    func_calls =[]
    
    #generate the code
    for comp_node in object_database.getObjectsOfType(NAME):
        comp = comp_node.getObject()
        func_name = "init%s%s()" % (comp.name.replace('-', ''), NAME)
        func_calls.append("%s;" % func_name)
        
        #write to header file
        HFILE.write("  void %(func_name)s;\n" % vars())
        HFILE.flush()
        
        #write to cpp file
        #regex to handle newline stuffs...we write the TPCL code on one line
        regex = re.compile('\s*\r?\n\s*')
        CFILE.write("""
void %(CLASS_NAME)s::%(func_name)s {
  std::map<unsigned int, std::string> propertylist;
  DesignStore *ds = Game::getGame()->getDesignStore();
  Component* comp = new Component();

  comp->setCategoryId(ds->getCategoryByName("%(comp.category)s"));
  comp->setName("%(comp.name)s");
  comp->setDescription("%(comp.description)s");
  comp->setTpclRequirementsFunction("%(" ".join(regex.split(comp.tpcl_requirements)))s");
""" % ExpressionDictionary(vars()))

        #now the properties...
        for name, cost_func in comp.properties.iteritems():
            #NOTE:
            # we here replace hyphens with underscores in the names of properties
            # since hyphens are not valid in variable names in C++
            CFILE.write('  propertylist[ds->getPropertyByName("%s")] = "%s";\n' % \
                (name.replace('-', '_'), " ".join(regex.split(cost_func))))
                
        #set our propertylist and get out of here
        CFILE.write("""\
  comp->setPropertyList(propertylist);
  ds->addComponent(comp);
  return;
}

""")
        CFILE.flush()
        comp_node.clearObject()
    
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
    
    print "ALL DONE GENERATING CODE FOR COMPONENTS!"