import types


def common_initiate(self):
    pass


def nayedien_initiate(self):
    from engine.character.engage_combat import nayedien_engage_combat
    from engine.character.check_move_existence import nayedien_check_move_existence
    self.engage_combat = types.MethodType(nayedien_engage_combat, self)
    self.check_move_existence = types.MethodType(nayedien_check_move_existence, self)
    self.health_as_resource = True
    self.moveset_reset_when_relax_only = True
    self.can_combo_with_no_hit = True
    self.special_relax_command = tuple([{"name": "Relax" + str(state), "low level": True} for state in range(8)])


initiate_dict = {"Nayedien": nayedien_initiate}
