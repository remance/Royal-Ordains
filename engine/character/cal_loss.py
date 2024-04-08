from engine.uibattle.uibattle import DamageNumber

infinity = float("inf")


def cal_loss(self, attacker, final_dmg, impact, hit_angle, dmg_text_pos, critical):
    """
    :param self: Damage receiver Character object
    :param attacker: Damage dealer Character object
    :param final_dmg: Damage value to health
    :param impact: Impact list value affecting if the target will start damaged or knockdown animation
    :param hit_angle: Angle of hitting side
    :param dmg_text_pos: Point to generate damage text
    :param critical: For checking if damage is from critical hit
    """
    if self.health:  # prevent multiple damage against already dead character in that update
        DamageNumber(final_dmg, dmg_text_pos, critical, self.team)

        if final_dmg > self.health:  # dmg cannot be higher than remaining health
            final_dmg = self.health
        super_armour = self.super_armour
        if "moveset" in self.current_action:  # any moveset action make super armour double
            super_armour = self.super_armour * 2
        impact_check = (abs(impact[0]) + abs(impact[1]) - (self.body_mass + super_armour))

        self.engage_combat()
        if not self.no_forced_move:  # object can be forced moved
            if impact_check > 10:
                if hit_angle == 90:
                    self.x_momentum = -impact[0]
                else:
                    self.x_momentum = impact[0]
                self.y_momentum = -impact[1]
                if self.y_momentum < -3000:  # maximum y up momentum to prevent too long knock
                    self.y_momentum = -3000
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
            if self.is_boss:  # boss add stun value to play stun animation
                self.stun_value += impact_check
                if self.stun_value >= self.stun_threshold:
                    self.interrupt_animation = True
                    self.command_action = self.stun_command_action
                    self.stun_value = 0
                    self.stun_threshold *= 2
            self.battle.add_sound_effect_queue(self.sound_effect_pool["Damaged"][0], self.pos,
                                               self.dmg_sound_distance,
                                               self.dmg_screen_shake,
                                               volume_mod=self.hit_volume_mod)

        self.health -= final_dmg
        if not self.health and attacker:
            self.killer = attacker
