from random import randint

infinity = float("inf")


def status_update(self):
    """Calculate stat with effect from skill and status"""
    # Reset to base stat
    self.stamina_dmg_bonus = 0
    self.attack_impact_effect = 1
    self.weapon_dmg_modifier = 1

    attack_bonus = 0
    defence_bonus = 0
    speed_bonus = 0
    hp_regen_bonus = 0
    resource_regen_bonus = 0
    crit_chance_bonus = 0
    animation_speed_bonus = 0

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

    # Remove status that reach 0 duration or status with conflict to the other status before apply effect
    self.status_effect = {key: val for key, val in self.status_effect.items() if key in self.status_duration and
                          not any(ext in self.status_effect for ext in val["Status Conflict"])}

    # Apply effect and modifier from status effect
    if self.status_effect:
        for cal_effect in self.status_effect.values():
            attack_bonus += cal_effect["Attack Bonus"]
            defence_bonus += cal_effect["Defence Bonus"]
            speed_bonus += cal_effect["Speed Bonus"]
            hp_regen_bonus += cal_effect["HP Regeneration Bonus"]
            resource_regen_bonus += cal_effect["Resource Regeneration Bonus"]
            animation_speed_bonus += cal_effect["Animation Speed Bonus"]
            self.element_resistance = {element: value + cal_effect[element + " Resistance Bonus"] for
                                       element, value in self.base_element_resistance.items()}

            for effect in cal_effect["Special Effect"]:
                self.special_effect[tuple(self.special_effect.keys())[effect]][0][1] = True

    # Apply effect from weather
    if not self.immune_weather:
        weather = self.battle.current_weather
        if weather.has_stat_effect:
            attack_bonus += weather.atk_buff
            defence_bonus += weather.def_buff
            speed_bonus += weather.speed_buff
            hp_regen_bonus += weather.hp_regen_buff
            for element in weather.element:  # Weather can cause elemental effect such as wet
                self.element_status_check[element[0]] += (element[1] * (100 - self.element_resistance[element[0]]) / 100)

    self.check_element_effect()  # elemental effect

    # Apply modifier to stat
    self.power_bonus = self.base_power_bonus + attack_bonus
    self.defence = (100 - (self.base_defence + defence_bonus)) / 100
    self.speed = self.base_speed + speed_bonus
    self.critical_chance = self.base_critical_chance + crit_chance_bonus
    self.super_armour = self.base_super_armour

    self.hp_regen = self.base_hp_regen + hp_regen_bonus
    self.resource_regen = self.base_resource_regen + resource_regen_bonus

    self.animation_play_time = self.original_animation_play_time + animation_speed_bonus

    self.body_mass = self.base_body_mass
    if "less mass" in self.current_action:  # knockdown reduce mass
        self.body_mass = int(self.base_body_mass / self.current_action["less mass"])

    if self.defence < 0:  # seem like using if is faster than max()
        self.defence = 0
    if self.dodge < 0:
        self.dodge = 0
    if self.speed < 1:  # prevent speed to be lower than 1
        self.speed = 1

    self.run_speed = 250 + self.speed
    self.walk_speed = 100 + self.speed

    # Cooldown
    for key in tuple(self.attack_cooldown.keys()):  # loop is faster than comprehension here
        self.attack_cooldown[key] -= self.timer
        if self.attack_cooldown[key] <= 0:  # remove cooldown if time reach 0
            self.attack_cooldown.pop(key)
