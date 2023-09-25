def add_gear_stat(self):
    for set_index, weapon_set in enumerate(self.weapon_set):
        for weapon_index, weapon in enumerate(weapon_set):
            weapon_stat = self.character_data.weapon_list[weapon[0]]
            dmg_scaling = (weapon_stat["Strength Bonus Scale"], weapon_stat["Dexterity Bonus Scale"])
            dmg_scaling = [item / sum(dmg_scaling) if sum(dmg_scaling) > 0 else 0 for item in dmg_scaling]

            for damage in self.original_weapon_dmg[set_index][weapon_index]:
                damage_name = damage + " Damage"
                if damage_name in weapon_stat:
                    if weapon_stat["Damage Stat Scaling"]:
                        damage_with_attribute = weapon_stat[damage_name] + \
                                                (weapon_stat[damage_name] * (self.strength * dmg_scaling[0] / 100) +
                                                 (weapon_stat[damage_name] * (self.dexterity * dmg_scaling[1] / 100)))
                    else:  # weapon damage not scale with user attribute
                        damage_with_attribute = weapon_stat[damage_name]
                self.original_weapon_dmg[set_index][weapon_index][damage] = [
                    damage_with_attribute * weapon_stat["Damage Balance"] *
                    (1 + self.character_data.equipment_grade_list[weapon[1]]["Stat Modifier"]),
                    damage_with_attribute * (1 + self.character_data.equipment_grade_list[weapon[1]]["Stat Modifier"])]
            self.original_weapon_dmg[set_index][weapon_index] = {key: value for key, value in  # remove 0 damage element
                                                                 self.original_weapon_dmg[set_index][
                                                                     weapon_index].items() if value}
            if weapon_stat["Damage Stat Scaling"]:  # impact get bonus from quality and strength
                self.weapon_impact[set_index][weapon_index] = weapon_stat["Impact"] * \
                                                              (1 + self.character_data.equipment_grade_list[weapon[1]][
                                                                  "Stat Modifier"]) + \
                                                              (weapon_stat["Impact"] * (
                                                                      self.strength * dmg_scaling[0] / 100))
            else:
                self.weapon_impact[set_index][weapon_index] = weapon_stat["Impact"] * \
                                                              (1 + self.character_data.equipment_grade_list[weapon[1]][
                                                                  "Stat Modifier"])

            self.weapon_penetrate[set_index][weapon_index] = weapon_stat["Armour Penetration"] * \
                                                             (1 + self.character_data.equipment_grade_list[weapon[1]][
                                                                 "Stat Modifier"])

            if self.original_weapon_speed[set_index][weapon_index] < 0:
                self.original_weapon_speed[set_index][weapon_index] = 0

            if weapon_stat["Magazine"] == 0:  # weapon is melee weapon with no magazine to load ammo
                self.original_melee_range[set_index][weapon_index] = weapon_stat["Range"]
                self.original_melee_def_range[set_index][weapon_index] = weapon_stat["Range"] * 3
            else:
                self.original_melee_range[set_index][weapon_index] = 0  # for distance to move closer check
                self.original_melee_def_range[set_index][weapon_index] = 0

            self.weight += weapon_stat["Weight"]
