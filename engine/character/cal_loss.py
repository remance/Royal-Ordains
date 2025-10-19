from random import uniform

from engine.uibattle.uibattle import DamageNumber
import engine.effect.effect

infinity = float("inf")


def cal_loss(self, attacker, final_damage, impact, hit_angle, critical):
    """
    :param self: Damage receiver Character object
    :param attacker: Damage dealer Character object
    :param final_damage: Damage value to health
    :param impact: Impact list value affecting if the target will start damaged or knockdown animation
    :param hit_angle: Angle of hitting side
    :param critical: For checking if damage is from critical hit
    """
    if self.health:  # prevent multiple damage against already dead character in that update
        if self.show_dmg_number:
            DamageNumber(final_damage, self.rect.midtop, critical, self.team)

        if final_damage > self.health:  # dmg cannot be higher than remaining health
            final_damage = self.health
        elif final_damage > self.health10:  # big hurt speech
            if not self.battle.ai_battle_speak_timer and "hurt" in self.ai_speak_list and uniform(0, 10) > 8:
                self.ai_speak("bighurt")
        elif final_damage > self.health1:  # hurt speech
            if not self.battle.ai_battle_speak_timer and "hurt" in self.ai_speak_list and uniform(0, 10) > 8:
                self.ai_speak("hurt")
        impact_check = (abs(impact[0]) + abs(impact[1])) - self.body_mass

        self.health -= final_damage
        if not self.health and attacker:
            # TODO Killer effect function
            pass

        if impact_check > self.body_mass:
            if impact_check > self.knockdown_mass and ((not self.health and not self.main_character) or
                                                       not self.no_forced_move):
                # object can be forced moved via damage, also will not play damaged animation
                # no_force_move is not considered for dying character but sub characters can not be forced move at all
                if hit_angle == 90:  # hit from right side
                    self.x_momentum = -impact[0] + self.knockdown_mass
                else:
                    self.x_momentum = impact[0] - self.knockdown_mass
                self.y_momentum = impact[1]
                if self.y_momentum > 100000:  # maximum y up momentum to prevent too long knock
                    self.y_momentum = 100000

                if "knockdown" not in self.current_action:  # not already in knock down state
                    self.interrupt_animation = True
                    self.command_action = self.knockdown_command_action
                    engine.effect.effect.Effect(None, ("Damaged", "Base", self.rect.center[0],
                                                       self.rect.center[1],
                                                       uniform(0, 360), 0, 0, 1, 1),
                                                from_owner=False)
                    self.battle.add_sound_effect_queue(self.sound_effect_pool["Knock Down"][0], self.pos,
                                                       self.knock_down_sound_distance,
                                                       self.knock_down_screen_shake,
                                                       volume_mod=self.hit_volume_mod)  # larger size play louder sound
            else:
                if "damaged" not in self.current_action:  # not already in damaged state
                    if not self.y_momentum:
                        self.x_momentum = 0
                    self.interrupt_animation = True
                    self.command_action = self.damaged_command_action
                    engine.effect.effect.Effect(None, ("Damaged", "Base", self.rect.center[0],
                                                       self.rect.center[1], uniform(0, 360), 0, 0, 1, 1),
                                                from_owner=False)
                    self.battle.add_sound_effect_queue(self.sound_effect_pool["Damaged"][0], self.pos,
                                                       self.dmg_sound_distance,
                                                       self.dmg_screen_shake,
                                                       volume_mod=self.hit_volume_mod)


