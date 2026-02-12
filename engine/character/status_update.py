def status_update(self):
    """Calculate stat with effect from weather, skill, and status"""
    # Reset to base stat
    self.offence = self.base_offence
    self.defence = self.base_defence
    self.speed = self.base_speed
    self.animation_frame_play_time = self.Base_Animation_Frame_Play_Time
    self.health_regen = self.base_health_regen
    self.resource_regen = self.base_resource_regen
    self.element_resistance = {element: value for
                               element, value in self.base_element_resistance.items()}
    self.resource_cost_modifier = self.base_resource_cost_modifier
    self.blind = False
    self.false_order = False

    self.status_duration = {key: value - 0.1 for key, value in self.status_duration.items() if value > 0.1}
    self.move_cooldown = {key: value - 0.1 for key, value in self.move_cooldown.items() if value > 0.1}

    current_weather = self.battle.current_weather
    # Apply effect from weather
    if not self.immune_weather:
        if current_weather.has_stat_effect:
            if self.character_type == "air":
                self.offence *= current_weather.air_offence_modifier
                self.defence *= current_weather.air_defence_modifier
                self.speed *= current_weather.air_speed_modifier
            else:
                self.offence *= current_weather.offence_modifier
                self.defence *= current_weather.defence_modifier
                self.speed *= current_weather.speed_modifier
            self.health_regen += current_weather.health_regen_bonus
            self.resource_regen += current_weather.resource_regen_bonus
            if current_weather.status_effect:
                for status in current_weather.status_effect:
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
    self.low_speed = self.speed * 0.75
    self.run_speed = 9 * self.speed
    self.walk_speed = 4 * self.speed

    if self.no_run:
        self.run_speed = self.walk_speed

    if self.nearest_enemy_distance and self.nearest_enemy_distance < self.sprite_width:
        # enemy collide with this character, make it have trouble moving around because of traffic congestion
        if (self.base_pos[0] >= self.nearest_enemy_pos[0] and self.direction == "left") or (
                self.base_pos[0] < self.nearest_enemy_pos[0] and self.direction == "right"):  # running toward enemy
            self.run_speed *= 0.25
            self.walk_speed *= 0.25
        else:  # running from enemy, less penalty
            self.run_speed *= 0.5
            self.walk_speed *= 0.5

    if self.run_speed < 0:
        self.run_speed = 0
    if self.walk_speed < 0:
        self.walk_speed = 0

    # if self.is_summon:  # summon reduce hp based on time
    #     self.health -= 0.1
    #     if self.health < 0:
    #         self.health = 0
