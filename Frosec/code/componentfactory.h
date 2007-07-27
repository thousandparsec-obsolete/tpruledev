#ifndef COMPFAC_H
#define COMPFAC_H

class ComponentFactory {
 public:
  ComponentFactory();
  
  void initComponentObjects();
  
 private:
  void initBattleshipHullComponent();
  void initFrigateHullComponent();
  void initScoutHullComponent();
};
#endif
