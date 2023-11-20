from random import randint

from engine.uibattle.uibattle import DamageNumber


def hit_register(self, target, body_part):
    """Calculate whether target dodge hit, then calculate damage"""
    from engine.effect.effect import Effect
    hit_angle = -90
    if self.rect.centerx > target.base_pos[0] * self.screen_scale[0]:
        hit_angle = 90
    dmg_text_pos = body_part.rect.midtop
    if self.dmg:
        if target.current_action and "parry" in target.current_action:  # target parrying
            # play next action after parry
            target.interrupt_animation = True
            target.command_action = target.current_action["next action"]
            if target.crash_haste:
                target.apply_status(45)  # get haste buff
            if self.owner.player_control:
                Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
            else:
                Effect(None, ("Crash Enemy", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
            if self.stick_reach and not self.penetrate:
                self.stick_timer = 5
        else:
            chance = randint(0, 100)
            if chance > target.dodge:  # not miss, now cal def and dmg
                critical = False
                if self.critical_chance >= randint(0, 100):
                    critical = True
                attacker_dmg, element_effect = self.cal_dmg(target, critical)
                self.owner.special_damage(self.owner, attacker_dmg)

                if self.owner.hit_resource_regen:  # regen resource when hit
                    self.owner.resource += self.owner.resource1  # regen
                    if self.owner.resource > self.owner.max_resource:  # resource cannot exceed the max resource
                        self.owner.resource = self.owner.max_resource

                if not target.guarding or target.angle == hit_angle:  # guard bypass if hit from behind
                    if self.owner.player_control:  # count dmg from player for data record
                        self.battle.player_damage[self.owner.player_control] += attacker_dmg
                    target.cal_loss(attacker_dmg, self.impact, element_effect, hit_angle, dmg_text_pos, critical)
                    if not self.penetrate:
                        if self.stick_reach == "stick":  # stuck at body part
                            self.stuck_part = body_part
                            self.stick_timer = 3
                            self.travel_distance = 0
                            self.current_animation = self.animation_pool["Base"]  # change image to base
                            self.base_image = self.current_animation[self.show_frame]
                            self.adjust_sprite()
                            self.battle.all_damage_effects.remove(self)
                            self.base_stuck_stat = (self.pos - self.stuck_part.rect.center, self.angle,
                                                    self.stuck_part.data, self.stuck_part.owner.angle)
                        elif self.stick_reach == "bounce":
                            self.stick_timer = 5
                    if self.enemy_status_effect:
                        for effect in self.enemy_status_effect:
                            target.apply_status(effect)

                else:  # guarded hit, reduce meter
                    if target.guarding > 0.5:  # not perfect guard (guard within 0.5 secs before taking hit)
                        target.guard_meter -= attacker_dmg * target.guard_cost_modifier
                        if target.crash_guard_resource_regen:
                            target.resource += target.resource1  # regen
                            if target.resource > target.max_resource:  # resource cannot exceed the max resource
                                target.resource = target.max_resource

                        if target.guard_meter < 0:  # guard depleted, break with heavy damaged animation
                            if self.owner.player_control:
                                Effect(None,
                                       ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                            else:
                                Effect(None,
                                       ("Crash Enemy", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                            target.guard_meter = 0
                            target.interrupt_animation = True
                            target.command_action = target.heavy_damaged_command_action
                            # target.battle.add_sound_effect_queue(target.sound_effect_pool["Guard Break"][0],
                            #                                      target.base_pos, target.heavy_dmg_sound_distance,
                            #                                      target.heavy_dmg_sound_shake,
                            #                                      volume_mod=target.hit_volume_mod)
                        else:
                            if self.owner.player_control:  # player hit enemy guard
                                Effect(None,
                                       ("Crash Enemy", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                            else:  # enemy hit player guard
                                Effect(None,
                                       ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle),
                                       0)
                            target.show_frame -= 3
                            if self.stick_reach and not self.penetrate:
                                self.stick_timer = 5
                    else:  # perfect guard, not reduce meter
                        Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                        if self.stick_reach and not self.penetrate:
                            self.stick_timer = 5
                # if self.stat["Enemy Status"]:
                #     for status in self.stat["Enemy Status"]:
                #         this_unit.apply_status(status, this_unit.status_list[status],
                #                                this_unit.status_effect, this_unit.status_duration)

            else:
                DamageNumber("MISS", dmg_text_pos, False, target.team)

                if target.current_moveset and "parry" in target.current_moveset[
                    "Property"]:  # target parrying even with dodge
                    # play next action after parry
                    target.interrupt_animation = True
                    target.command_action = target.current_action["next action"]
                    if self.owner.player_control:
                        Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                    else:
                        Effect(None, ("Crash Enemy", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
