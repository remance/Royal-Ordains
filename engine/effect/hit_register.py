from random import randint

from engine.uibattle.uibattle import DamageNumber


def hit_register(self, target, dmg_text_pos):
    """Calculate whether target dodge hit, then calculate damage"""
    from engine.effect.effect import Effect
    hit_angle = -90
    if self.rect.centerx > target.base_pos[0] * self.screen_scale[0]:
        hit_angle = 90
    if self.dmg:
        chance = randint(0, 100)
        if chance > target.dodge:  # not miss, now cal def and dmg
            critical = False
            if self.critical_chance >= randint(0, 100):
                critical = True
            attacker_dmg, element_effect = self.cal_dmg(target, critical)
            self.owner.special_damage(self.owner, attacker_dmg)

            if not target.guarding or target.angle == hit_angle:  # guard bypass if hit from behind
                if self.owner.player_control:
                    self.battle.player_damage[self.owner.player_control] += attacker_dmg
                target.cal_loss(attacker_dmg, self.impact, element_effect, hit_angle, dmg_text_pos, critical)
                if self.enemy_status_effect:
                    for effect in self.enemy_status_effect:
                        target.apply_status(effect)

            else:  # guarded hit, reduce meter
                if target.guarding > 0.5:  # not perfect guard (guard within 0.5 secs before taking hit)
                    target.guard_meter -= attacker_dmg
                    if target.guard_meter < 0:  # guard depleted, break with heavy damaged animation
                        if self.owner.player_control:
                            Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                        else:
                            Effect(None, ("Crash Enemy", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                        target.guard_meter = 0
                        target.interrupt_animation = True
                        target.command_action = target.heavy_damaged_command_action
                        # target.battle.add_sound_effect_queue(target.sound_effect_pool["Guard Break"][0],
                        #                                      target.base_pos, target.heavy_dmg_sound_distance,
                        #                                      target.heavy_dmg_sound_shake,
                        #                                      volume_mod=target.hit_volume_mod)
                    else:
                        if self.owner.player_control:  # player hit enemy guard
                            Effect(None, ("Crash Enemy", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                        else:  # enemy hit player ghard
                            Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                        target.show_frame -= 3
                else:  # perfect guard, not reduce meter
                    Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
            # if self.stat["Enemy Status"]:
            #     for status in self.stat["Enemy Status"]:
            #         this_unit.apply_status(status, this_unit.status_list[status],
            #                                this_unit.status_effect, this_unit.status_duration)

        else:
            DamageNumber("MISS", dmg_text_pos, False, target.team)
    else:
        pass
        # if self.stat["Enemy Status"]:
        #     for status in self.stat["Enemy Status"]:
        #         this_unit.apply_status(status, this_unit.status_list[status],
        #                                this_unit.status_effect, this_unit.status_duration)

