def get_damage(self):
    """Get action stat for character attack that use its own sprite"""
    current_moveset = self.current_moveset
    self.power = current_moveset["Power"]
    self.penetrate = current_moveset["Penetrate"]
    self.element = current_moveset["Element"]
    self.impact = (current_moveset["Impact X"],
                   current_moveset["Impact Y"])
    self.impact_sum = abs(self.impact[0]) + abs(self.impact[1])

    self.critical_chance = self.base_critical_chance + current_moveset["Critical Chance Bonus"]
    self.enemy_status_effect = current_moveset["Enemy Status"]

    self.no_defence = False
    if "no_defence" in self.current_moveset_property:
        self.no_defence = True

    self.no_dodge = False
    if "no_dodge" in self.current_moveset_property:
        self.no_dodge = True
