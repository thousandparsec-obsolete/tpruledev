#include <tpserver/game.h>
#include <tpserver/designstore.h>
#include <tpserver/property.h>

#include <propertyfactory.h>

PropertyFactory::PropertyFactory(){

}

void PropertyFactory::initArmourProperty() {
  Property* prop = new Property();
  DesignStore *ds = Game::getGame()->getDesignStore();

  prop->setCategoryId(ds->getCategoryByName("Ships"));
  prop->setRank(0);
  prop->setName("Armour");
  prop->setDisplayName("Armour");
  prop->setDescription("The amount of armour a ship has.");
  prop->setTpclDisplayFunction("(lambda (design bits) (let ((n (apply + bits))) (cons n (string-append (number->string n) \" HP\")) ) )");
  prop->setTpclRequirementsFunction("(lambda (design) (cons #t \"\"))");
  ds->addProperty(prop);
  return;
}

void PropertyFactory::initBuildTimeProperty() {
  Property* prop = new Property();
  DesignStore *ds = Game::getGame()->getDesignStore();

  prop->setCategoryId(ds->getCategoryByName("Ships"));
  prop->setRank(0);
  prop->setName("BuildTime");
  prop->setDisplayName("Build Time");
  prop->setDescription("The number of turns to build a ship");
  prop->setTpclDisplayFunction("(lambda (design bits) (let ((n (apply + bits))) (cons n (string-append (number->string n) \" turns\")) ) )");
  prop->setTpclRequirementsFunction("(lambda (design) (cons #t \"\"))");
  ds->addProperty(prop);
  return;
}

void PropertyFactory::initColoniseProperty() {
  Property* prop = new Property();
  DesignStore *ds = Game::getGame()->getDesignStore();

  prop->setCategoryId(ds->getCategoryByName("Ships"));
  prop->setRank(0);
  prop->setName("Colonise");
  prop->setDisplayName("Colonise");
  prop->setDescription("Whether a ship can colonise or not.");
  prop->setTpclDisplayFunction("(lambda (design bits) (let ((n (apply + bits))) (cons n (if (= n 1) \"Yes\" \"No\")) ) )");
  prop->setTpclRequirementsFunction("(lambda (design) (cons #t \"\"))");
  ds->addProperty(prop);
  return;
}

void PropertyFactory::initSpeedProperty() {
  Property* prop = new Property();
  DesignStore *ds = Game::getGame()->getDesignStore();

  prop->setCategoryId(ds->getCategoryByName("Ships"));
  prop->setRank(0);
  prop->setName("Speed");
  prop->setDisplayName("Speed");
  prop->setDescription("How fast a ship moves. ");
  prop->setTpclDisplayFunction("(lambda (design bits) (let ((n (apply + bits))) (cons n (string-append (number->string (/ n 1000000)) \" mega-units\")) ) )");
  prop->setTpclRequirementsFunction("(lambda (design) (cons #t \"\"))");
  ds->addProperty(prop);
  return;
}

void PropertyFactory::initWeaponDrawProperty() {
  Property* prop = new Property();
  DesignStore *ds = Game::getGame()->getDesignStore();

  prop->setCategoryId(ds->getCategoryByName("Ships"));
  prop->setRank(0);
  prop->setName("WeaponDraw");
  prop->setDisplayName("Weapon Strength at Draw");
  prop->setDescription("The amount of damage done on a draw");
  prop->setTpclDisplayFunction("(lambda (design bits) (let ((n (apply + bits))) (cons n (string-append (number->string n) \" HP\")) ) )");
  prop->setTpclRequirementsFunction("(lambda (design) (cons #t \"\"))");
  ds->addProperty(prop);
  return;
}

void PropertyFactory::initWeaponWinProperty() {
  Property* prop = new Property();
  DesignStore *ds = Game::getGame()->getDesignStore();

  prop->setCategoryId(ds->getCategoryByName("Ships"));
  prop->setRank(0);
  prop->setName("WeaponWin");
  prop->setDisplayName("Weapon Strength at Win");
  prop->setDescription("The amount of damage done on a win.");
  prop->setTpclDisplayFunction("(lambda (design bits) (let ((n (apply + bits))) (cons n (string-append (number->string n) \" HP\")) ) )");
  prop->setTpclRequirementsFunction("(lambda (design) (cons #t \"\"))");
  ds->addProperty(prop);
  return;
}

void PropertyFactory::init_num_componentsProperty() {
  Property* prop = new Property();
  DesignStore *ds = Game::getGame()->getDesignStore();

  prop->setCategoryId(ds->getCategoryByName("Ships"));
  prop->setRank(0);
  prop->setName("_num-components");
  prop->setDisplayName("Number of Components");
  prop->setDescription("The number of components in a design");
  prop->setTpclDisplayFunction("(lambda (design bits) (let ((n (apply + bits))) (cons n (string-append (number->string n) \" components\"))))");
  prop->setTpclRequirementsFunction("(lambda (design) (cons #t \"\"))");
  ds->addProperty(prop);
  return;
}

void PropertyFactory::initPropertyObjects() {
  initArmourProperty();
  initBuildTimeProperty();
  initColoniseProperty();
  initSpeedProperty();
  initWeaponDrawProperty();
  initWeaponWinProperty();
  init_num_componentsProperty();
  return;
}
