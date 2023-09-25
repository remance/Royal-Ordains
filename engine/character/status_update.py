from random import randint

infinity = float("inf")


def status_update(self):
    """Calculate stat with effect from skill and status"""
    # Reset to base stat
    self.hp_regen = self.base_hp_regen
    self.resource_regen = self.base_resource_regen

    self.stamina_dmg_bonus = 0
    self.attack_impact_effect = 1
    self.weapon_dmg_modifier = 1

    attack_bonus = 0
    defense_bonus = 0
    speed_bonus = 0
    hp_regen_bonus = 0
    stamina_regen_bonus = 0
    crit_chance_bonus = 0

    if "arrive" in self.current_action:  # update arriving target for ai
        if self.nearest_enemy:
            self.x_momentum = self.nearest_enemy[0].base_pos[0] - self.base_pos[0]
            if abs(self.x_momentum) < 50:
                self.x_momentum = 0
        else:
            self.x_momentum = randint(-1000, 1000)

    for key in tuple(self.status_duration.keys()):  # loop seem to be faster than comprehension
        self.status_duration[key] -= self.timer
        if self.status_duration[key] <= 0:
            self.status_duration.pop(key)

    # Apply effect from skill
    if self.skill_effect:
        for key in tuple(self.skill_effect.keys()):
            self.skill_duration[key] -= self.timer
            if self.skill_duration[key] <= 0:  # skill end
                self.skill_duration.pop(key)
                self.skill_effect.pop(key)

        for cal_effect in self.skill_effect.values():  # apply elemental effect to melee_dmg if skill has element
            attack_bonus += cal_effect["Attack Bonus"]
            defense_bonus += cal_effect["Defense Bonus"]
            speed_bonus += cal_effect["Speed Bonus"]
            hp_regen_bonus += cal_effect["HP Regeneration Bonus"]
            stamina_regen_bonus += cal_effect["Stamina Regeneration Bonus"]

            self.weapon_dmg_modifier += cal_effect["Damage Modifier"]
            crit_chance_bonus += cal_effect["Critical Bonus"]
            self.attack_impact_effect += cal_effect["Weapon Impact Modifier"]

    # Remove status that reach 0 duration or status with conflict to the other status before apply effect
    self.status_effect = {key: val for key, val in self.status_effect.items() if key in self.status_duration and
                          not any(ext in self.status_effect for ext in val["Status Conflict"])}

    # Apply effect and modifier from status effect
    if self.status_effect:
        for cal_effect in self.status_effect.values():
            attack_bonus += cal_effect["Attack Bonus"]
            defense_bonus += cal_effect["Defense Bonus"]
            speed_bonus += cal_effect["Speed Bonus"]
            hp_regen_bonus += cal_effect["HP Regeneration Bonus"]
            self.element_resistance = {element: value + cal_effect[element + " Resistance Bonus"] for
                                       element, value in self.base_element_resistance.items()}
            for effect in cal_effect["Special Effect"]:
                self.special_effect[tuple(self.special_effect.keys())[effect]][0][1] = True

    # Apply effect from weather
    weather = self.battle.current_weather
    if weather.has_stat_effect:
        attack_bonus += weather.atk_buff
        defense_bonus += weather.def_buff
        speed_bonus += weather.speed_buff
        hp_regen_bonus += weather.hp_regen_buff
        for element in weather.element:  # Weather can cause elemental effect such as wet
            self.element_status_check[element[0]] += (element[1] * (100 - self.element_resistance[element[0]]) / 100)

    self.check_element_effect()  # elemental effect

    # Apply modifier to stat
    self.power_bonus = self.base_power_bonus + attack_bonus
    self.defense = (100 - (self.base_defense + defense_bonus)) / 100
    self.speed = self.base_speed + speed_bonus
    self.critical_chance = self.base_critical_chance + crit_chance_bonus
    self.super_armour = self.base_super_armour

    self.body_mass = self.base_body_mass
    if "less mass" in self.current_action:  # knockdown reduce mass
        self.body_mass = int(self.base_body_mass / self.current_action["less mass"])

    if self.defense < 0:  # seem like using if is faster than max()
        self.defense = 0
    if self.dodge < 0:
        self.dodge = 0
    if self.speed < 1:  # prevent speed to be lower than 1
        self.speed = 1

    self.run_speed = self.speed * 100
    self.walk_speed = self.speed * 50

    # Cooldown
    for key in tuple(self.attack_cooldown.keys()):  # loop is faster than comprehension here
        self.attack_cooldown[key] -= self.timer
        if self.attack_cooldown[key] <= 0:  # remove cooldown if time reach 0
            self.attack_cooldown.pop(key)
