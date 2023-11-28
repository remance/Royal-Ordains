import types


def common_initiate(self):
    pass


def nayedien_initiate(self):
    from engine.character.engage_combat import nayedien_engage_combat
    self.engage_combat = types.MethodType(nayedien_engage_combat, self)
    self.health_as_resource = True
    self.moveset_reset_when_relax_only = True
    self.combo_with_no_hit = True


initiate_dict = {"Nayedien": nayedien_initiate}
