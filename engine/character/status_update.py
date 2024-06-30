from random import uniform

infinity = float("inf")


def status_update(self):
    """Calculate stat with effect from skill and status"""
    # Reset to base stat
    self.stamina_dmg_bonus = 0
    self.impact_modifier = self.base_impact_modifier
    self.weapon_dmg_modifier = 1

    power_bonus = 0
    defence_bonus = 0
    speed_bonus = 0
    hp_regen_bonus = 0
    resource_regen_bonus = 0
    crit_chance_bonus = 0
    animation_speed_modifier = 1

    self.blind = False

    self.resource_cost_modifier = self.base_resource_cost_modifier
    self.guard_cost_modifier = self.base_guard_cost_modifier

    if "arrive" in self.current_action:  # update arriving target for ai
        if self.nearest_enemy:
            self.x_momentum = self.nearest_enemy.base_pos[0] - self.base_pos[0]
            if abs(self.x_momentum) < uniform(100, 500):
                self.x_momentum = 0
        else:
            self.x_momentum = uniform(-1000, 1000)

    for key in tuple(self.status_duration.keys()):  # loop seem to be faster than comprehension
        self.status_duration[key] -= 0.1
        if self.status_duration[key] <= 0:
            self.status_duration.pop(key)

    # Remove status that reach 0 duration or status with conflict to the other status before apply effect
    self.status_effect = {key: val for key, val in self.status_effect.items() if key in self.status_duration and
                          not any(ext in self.status_effect for ext in val["Status Conflict"])}
    self.status_applier = {key: val for key, val in self.status_applier.items() if key in self.status_effect}

    if 4 in self.status_effect:  # invisible effect
        self.invisible = True
        if self.indicator in self.battle.battle_camera:
            self.battle.battle_camera.remove(self.indicator)
        for team in self.battle.all_team_enemy:
            if team != self.team and self in self.battle.all_team_enemy[team]:
                self.battle.all_team_enemy[team].remove(self)
    elif self.invisible:  # stop being invisible
        self.invisible = False
        if self.indicator and self.indicator not in self.battle.battle_camera:
            # add back indicator and enemy team for ai
            self.battle.battle_camera.add(self.indicator)
        for team in self.battle.all_team_enemy:
            if team != self.team and self not in self.battle.all_team_enemy[team]:
                self.battle.all_team_enemy[team].add(self)

    if 7 in self.status_effect:  # blind effect
        self.blind = True

    # Apply effect and modifier from status effect
    if self.status_effect:
        for cal_effect in self.status_effect.values():
            power_bonus += cal_effect["Power Bonus"]
            defence_bonus += cal_effect["Defence Bonus"]
            speed_bonus += cal_effect["Speed Bonus"]
            hp_regen_bonus += cal_effect["HP Regeneration Bonus"]
            resource_regen_bonus += cal_effect["Resource Regeneration Bonus"]
            animation_speed_modifier += cal_effect["Animation Time Modifier"]
            self.element_resistance = {element: value + cal_effect[element + " Resistance Bonus"] for
                                       element, value in self.base_element_resistance.items()}

    self.element_resistance = {element: value if value <= 0.9 else 0.9 for
                               element, value in self.base_element_resistance.items()}

    if 50 in self.status_effect:  # half resource cost
        self.resource_cost_modifier -= 0.5

    # Apply effect from weather
    if not self.immune_weather:
        weather = self.battle.current_weather
        if weather.has_stat_effect:
            power_bonus += weather.atk_buff
            defence_bonus += weather.def_buff
            speed_bonus += weather.speed_buff
            hp_regen_bonus += weather.hp_regen_buff

    # Apply modifier to stat
    self.power_bonus = self.base_power_bonus + power_bonus
    self.defence = self.base_defence + defence_bonus
    self.speed = self.base_speed + speed_bonus
    self.dodge = self.base_dodge + (speed_bonus / 1000)
    self.critical_chance = self.base_critical_chance + crit_chance_bonus
    self.super_armour = self.base_super_armour + (defence_bonus * 1)  # each 1% defence bonus affect super armour by 1

    self.hp_regen = self.base_hp_regen + hp_regen_bonus
    self.resource_regen = self.base_resource_regen + resource_regen_bonus

    self.animation_play_time = self.base_animation_play_time * animation_speed_modifier
    if self.animation_play_time < 0:  # can not be 0
        self.animation_play_time = 0.01

    if self.defence < 0:  # seem like using if is faster than max()
        self.defence = 0
    elif self.defence > 0.9:
        self.defence = 0.9
    if self.dodge < 0:
        self.dodge = 0
    elif self.dodge > 0.9:
        self.dodge = 0.9
    if self.guard_cost_modifier < 0:
        self.guard_cost_modifier = 0
    elif self.guard_cost_modifier > 1:
        self.guard_cost_modifier = 1
    if self.resource_cost_modifier < 0:
        self.resource_cost_modifier = 0
    elif self.resource_cost_modifier > 1:
        self.resource_cost_modifier = 1

    self.run_speed = 600 + self.speed
    self.walk_speed = 350 + self.speed

    if self.run_speed < 0:
        self.run_speed = 0
    if self.walk_speed < 0:
        self.walk_speed = 0

    if self.is_summon:  # summon reduce hp based on time
        self.health -= 0.1
        if self.health < 0:
            self.health = 0

    # Cooldown
    for key in tuple(self.attack_cooldown.keys()):  # loop is faster than comprehension here
        self.attack_cooldown[key] -= 0.1
        if self.attack_cooldown[key] <= 0:  # remove cooldown if time reach 0
            self.attack_cooldown.pop(key)
