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
    self.false_order = False

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

    # Apply effect and modifier from status effect
    if self.status_duration:
        for status in self.status_duration:
            self.status_apply_funcs[status](self)

    if not self.false_order:
        self.commander_order = self.true_commander_order

    if self.defence < 0:  # seem like using if is faster than min()
        self.defence = 0

    self.low_offence = self.offence * 0.5
    self.low_speed = self.speed * 0.5
    self.run_speed = 5 * self.speed
    self.walk_speed = 3 * self.speed

    if self.nearest_enemy_distance and self.nearest_enemy_distance < self.sprite_width:
        # enemy potentially collide with this character, consider having trouble moving around because of congestion
        self.run_speed *= 0.5
        self.walk_speed *= 0.5

    if self.run_speed < 0:
        self.run_speed = 0
    if self.walk_speed < 0:
        self.walk_speed = 0

    if self.is_summon:  # summon reduce hp based on time
        self.health -= 0.1
        if self.health < 0:
            self.health = 0
