#ifndef PROPFAC_H
#define PROPFAC_H

class PropertyFactory {
 public:
  PropertyFactory();
  
  void initPropertyObjects();
  
 private:
  void initArmourProperty();
  void initBuildTimeProperty();
  void initColoniseProperty();
  void initSpeedProperty();
  void initWeaponDrawProperty();
  void initWeaponWinProperty();
  void init_num_componentsProperty();
};

#endif
