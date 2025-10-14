def get_damage(self):
    self.dmg = self.current_moveset["Power"]
    self.penetrate = self.current_moveset["Penetrate"]
    self.element = self.current_moveset["Element"]
    self.impact = (self.current_moveset["Impact X"] * self.impact_modifier,
                   self.current_moveset["Impact Y"] * self.impact_modifier)
    self.impact_sum = abs(self.impact[0]) + abs(self.impact[1])

    self.critical_chance = self.critical_chance + self.current_moveset["Critical Chance Bonus"]
    self.enemy_status_effect = self.current_moveset["Enemy Status"]

    self.no_defence = False
    if "no defence" in self.current_moveset["Property"]:
        self.no_defence = True

    self.no_dodge = False
    if "no dodge" in self.current_moveset["Property"]:
        self.no_dodge = True