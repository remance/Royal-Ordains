def get_damage(self):
    self.power = self.current_moveset["Power"]
    self.penetrate = self.current_moveset["Penetrate"]
    self.element = self.current_moveset["Element"]
    self.impact = (self.current_moveset["Impact X"],
                   self.current_moveset["Impact Y"])
    self.impact_sum = abs(self.impact[0]) + abs(self.impact[1])

    self.critical_chance = self.critical_chance + self.current_moveset["Critical Chance Bonus"]
    self.enemy_status_effect = self.current_moveset["Enemy Status"]

    self.no_defence = False
    if "no_defence" in self.current_moveset["Property"]:
        self.no_defence = True

    self.no_dodge = False
    if "no_dodge" in self.current_moveset["Property"]:
        self.no_dodge = True