def status_update(self):
    """Calculate stat with effect from weather, skill, and status"""
    # Reset to base stat
    self.offence = self.base_offence
    self.defence = self.base_defence
    self.speed = self.base_speed
    self.animation_play_time = self.Base_Animation_Play_Time
    self.health_regen = self.base_health_regen
    self.resource_regen = self.base_resource_regen
    self.element_resistance = {element: value for
                               element, value in self.base_element_resistance.items()}
    self.resource_cost_modifier = self.base_resource_cost_modifier
    self.blind = False

    self.status_duration = {key: value - 0.1 for key, value in self.status_duration.items() if value > 0.1}
    self.move_cooldown = {key: value - 0.1 for key, value in self.move_cooldown.items() if value > 0.1}

    # Apply effect from weather
    if not self.immune_weather:
        if self.weather.has_stat_effect:
            if self.character_type == "air":
                self.offence *= self.weather.air_offence_modifier
                self.defence *= self.weather.air_defence_modifier
                self.speed *= self.weather.air_speed_modifier
            else:
                self.offence *= self.weather.offence_modifier
                self.defence *= self.weather.defence_modifier
                self.speed *= self.weather.speed_modifier
            self.health_regen += self.weather.health_regen_bonus
            self.resource_regen += self.weather.resource_regen_bonus
            if self.weather.status_effect:
                for status in self.weather.status_effect:
                    self.apply_status(status)

    # Remove status that reach 0 duration or status with conflict to the other status before apply effect
    if "Invisible" in self.status_duration:  # invisible effect
        self.invisible = True
        self.battle.battle_camera.remove(self)
    elif self.invisible:  # stop being invisible
        self.invisible = False
        self.battle.battle_camera.add(self)

    # Apply effect and modifier from status effect
    if self.status_duration:
        for status in self.status_duration:
            self.status_apply_funcs[status](self)

    if self.defence < 0:  # seem like using if is faster than min()
        self.defence = 0

    self.run_speed = 10 * self.speed
    self.walk_speed = 4 * self.speed

    if self.run_speed < 0:
        self.run_speed = 0
    if self.walk_speed < 0:
        self.walk_speed = 0

    if self.is_summon:  # summon reduce hp based on time
        self.health -= 0.1
        if self.health < 0:
            self.health = 0
