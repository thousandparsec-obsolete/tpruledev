#include <tpserver/game.h>
#include <tpserver/designstore.h>
#include <tpserver/component.h>

#include <componentfactory.h>

ComponentFactory::ComponentFactory(){

}


void ComponentFactory::initBattleshipHullComponent() {
  std::map<unsigned int, std::string> propertylist;
  DesignStore *ds = Game::getGame()->getDesignStore();
  Component* comp = new Component();

  comp->setCategoryId(ds->getCategoryByName("Ships"));
  comp->setName("BattleshipHull");
  comp->setDescription("A battleship to destroy things!");
  comp->setTpclRequirementsFunction("(lambda (design) (if (= (designType._num-components design) 1) (cons #t \"\") (cons #f \"This is a complete component, nothing else can be included\")))");
  propertylist[ds->getPropertyByName("BuildTime")] = "(lambda (design) 4)";
  propertylist[ds->getPropertyByName("Armour")] = "(lambda (design) 6)";
  propertylist[ds->getPropertyByName("WeaponWin")] = "(lambda (design) 3)";
  propertylist[ds->getPropertyByName("WeaponDraw")] = "(lambda (design) 1)";
  propertylist[ds->getPropertyByName("Speed")] = "(lambda (design) 300000000)";
  propertylist[ds->getPropertyByName("_num-components")] = "(lambda (design) 1)";
  comp->setPropertyList(propertylist);
  ds->addComponent(comp);
  return;
}


void ComponentFactory::initFrigateHullComponent() {
  std::map<unsigned int, std::string> propertylist;
  DesignStore *ds = Game::getGame()->getDesignStore();
  Component* comp = new Component();

  comp->setCategoryId(ds->getCategoryByName("Ships"));
  comp->setName("FrigateHull");
  comp->setDescription("A frigate to colonise things!");
  comp->setTpclRequirementsFunction("(lambda (design) (if (= (designType._num-components design) 1) (cons #t \"\") (cons #f \"This is a complete component, nothing else can be included\")))");
  propertylist[ds->getPropertyByName("BuildTime")] = "(lambda (design) 2)";
  propertylist[ds->getPropertyByName("_num-components")] = "(lambda (design) 1)";
  propertylist[ds->getPropertyByName("WeaponWin")] = "(lambda (design) 2)";
  propertylist[ds->getPropertyByName("WeaponDraw")] = "(lambda (design) 0)";
  propertylist[ds->getPropertyByName("Colonise")] = "(lambda (design) 1)";
  propertylist[ds->getPropertyByName("Speed")] = "(lambda (design) 200000000)";
  propertylist[ds->getPropertyByName("Armour")] = "(lambda (design) 3)";
  comp->setPropertyList(propertylist);
  ds->addComponent(comp);
  return;
}


void ComponentFactory::initScoutHullComponent() {
  std::map<unsigned int, std::string> propertylist;
  DesignStore *ds = Game::getGame()->getDesignStore();
  Component* comp = new Component();

  comp->setCategoryId(ds->getCategoryByName("Ships"));
  comp->setName("ScoutHull");
  comp->setDescription("A scout to explore things!");
  comp->setTpclRequirementsFunction("(lambda (design) (if (= (designType._num-components design) 1) (cons #t \"\") (cons #f \"This is a complete component, nothing else can be included\")))");
  propertylist[ds->getPropertyByName("BuildTime")] = "(lambda (design) 1)";
  propertylist[ds->getPropertyByName("Armour")] = "(lambda (design) 2)";
  propertylist[ds->getPropertyByName("WeaponWin")] = "(lambda (design) 0)";
  propertylist[ds->getPropertyByName("WeaponDraw")] = "(lambda (design) 0)";
  propertylist[ds->getPropertyByName("Speed")] = "(lambda (design) 500000000)";
  propertylist[ds->getPropertyByName("_num-components")] = "(lambda (design) 1)";
  comp->setPropertyList(propertylist);
  ds->addComponent(comp);
  return;
}

void ComponentFactory::initComponentObjects() {
  initBattleshipHullComponent();
  initFrigateHullComponent();
  initScoutHullComponent();
  return;
}
