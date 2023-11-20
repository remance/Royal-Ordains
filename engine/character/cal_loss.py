from engine.uibattle.uibattle import DamageNumber

infinity = float("inf")


def cal_loss(self, final_dmg, impact, element_effect, hit_angle, dmg_text_pos, critical):
    """
    :param self: Damage receiver Character object
    :param final_dmg: Damage value to health
    :param impact: Impact list value affecting if the target will start damaged or knockdown animation
    :param element_effect: Dict of element effect inflict to target
    :param hit_angle: Angle of hitting side
    :param dmg_text_pos: Point to generate damage text
    :param critical: For checking if damage is from critical hit
    """
    DamageNumber(final_dmg, dmg_text_pos, critical, self.team)
    if final_dmg > self.health:  # dmg cannot be higher than remaining health
        final_dmg = self.health
    super_armour = self.super_armour
    if "moveset" in self.current_action:  # any moveset action make super armour double
        super_armour = self.super_armour * 2
    impact_check = (abs(impact[0]) + abs(impact[1]) - (self.body_mass + super_armour))

    self.engage_combat()
    if not self.not_movable:  # object can be moved
        if impact_check > 10:
            if hit_angle == 90:
                self.x_momentum = -impact[0]
            else:
                self.x_momentum = impact[0]
            self.y_momentum = -impact[1]
        else:
            self.x_momentum = 0

        if "knockdown" not in self.current_action:  # not already in knock down state
            if impact_check > 100 or "heavy damaged" in self.current_action:  # knockdown
                self.interrupt_animation = True
                self.command_action = self.knockdown_command_action
                self.battle.add_sound_effect_queue(self.sound_effect_pool["Knock Down"][0], self.pos,
                                                   self.knock_down_sound_distance,
                                                   self.knock_down_screen_shake,
                                                   volume_mod=self.hit_volume_mod)  # larger size play louder sound

            elif impact_check > 50 or "small damaged" in self.current_action:  # heavy damaged
                self.interrupt_animation = True
                self.command_action = self.heavy_damaged_command_action
                self.battle.add_sound_effect_queue(self.sound_effect_pool["Heavy Damaged"][0], self.pos,
                                                   self.heavy_dmg_sound_distance,
                                                   self.heavy_dmg_screen_shake,
                                                   volume_mod=self.hit_volume_mod)

            elif impact_check > 0:
                self.interrupt_animation = True
                self.command_action = self.damaged_command_action
                self.battle.add_sound_effect_queue(self.sound_effect_pool["Damaged"][0], self.pos,
                                                   self.dmg_sound_distance,
                                                   self.dmg_screen_shake,
                                                   volume_mod=self.hit_volume_mod)

            else:
                self.battle.add_sound_effect_queue(self.sound_effect_pool["Damaged"][0], self.pos,
                                                   self.dmg_sound_distance,
                                                   self.dmg_screen_shake,
                                                   volume_mod=self.hit_volume_mod)
        else:
            self.battle.add_sound_effect_queue(self.sound_effect_pool["Damaged"][0], self.pos,
                                               self.dmg_sound_distance,
                                               self.dmg_screen_shake,
                                               volume_mod=self.hit_volume_mod)

    else:  # play damaged sound when hit for immovable enemy
        self.battle.add_sound_effect_queue(self.sound_effect_pool["Damaged"][0], self.pos,
                                           self.dmg_sound_distance,
                                           self.dmg_screen_shake,
                                           volume_mod=self.hit_volume_mod)
    # if self.current_effect != "Hurt":
    #     self.current_effect = "Hurt"
    #     self.max_effect_frame = self.status_animation_pool[self.current_effect]["frame_number"]
    #     if self.effectbox not in self.battle.battle_camera:
    #         self.battle.battle_camera.add(self.effectbox)

    self.health -= final_dmg
    # self.resource -= self.stamina_dmg_bonus

    for key, value in element_effect.items():
        self.element_status_check[key] += round(final_dmg * value * (100 - self.element_resistance[key] / 100))
