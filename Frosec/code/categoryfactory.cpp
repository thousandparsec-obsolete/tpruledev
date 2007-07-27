#include <tpserver/game.h>
#include <tpserver/designstore.h>
#include <tpserver/category.h>

#include <categoryfactory.h>

CategoryFactory::CategoryFactory(){

}

void CategoryFactory::initShipsCategory() {
  Category* cat = new Category();
  DesignStore *ds = Game::getGame()->getDesignStore();

  cat->setName("Ships");
  cat->setDescription("The ship category. For shippy things.");
  ds->addCategory(cat);
  return;
}

void CategoryFactory::initCategoryObjects() {
  initShipsCategory();
  return;
}
