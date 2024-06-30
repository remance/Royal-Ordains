from random import uniform

from engine.uibattle.uibattle import DamageNumber


def hit_register(self, target, enemy_part, collide_pos):
    """Calculate whether target dodge hit, then calculate damage"""
    from engine.effect.effect import Effect
    hit_angle = -90
    if self.rect.centerx > target.base_pos[0] * self.screen_scale[0]:
        hit_angle = 90
    dmg_text_pos = enemy_part.rect.midtop
    if self.dmg:
        if target.current_action and "parry" in target.current_action:  # target parrying
            # play next action after parry
            target.interrupt_animation = True
            target.command_action = target.current_action["next action"]
            if target.crash_haste:
                target.apply_status(target, 45)  # get haste buff
            if self.owner.player_control:
                Effect(None, ("Crash Player", "Base", self.rect.centerx, self.rect.centery, -self.angle, 1, 0, 1), 0)
            else:
                Effect(None, ("Crash Enemy", "Base", self.rect.centerx, self.rect.centery, -self.angle, 1, 0, 1), 0)
            if self.stick_reach and not self.penetrate and not self.owner.attack_penetrate:
                self.stick_timer = 5
        else:
            if self.no_dodge or self.owner.attack_no_dodge or uniform(0,
                                                                      1) > target.dodge:  # not miss, now cal def and dmg
                critical = False
                if self.critical_chance >= uniform(0, 1):
                    critical = True
                attacker_dmg = self.cal_dmg(target, critical)
                self.owner.special_damage(attacker_dmg)

                if not self.duration:  # only damage not from object with duration make target stop falling for a bit
                    target.stop_fall_duration = 1

                if self.owner.hit_resource_regen:  # regen resource when hit
                    self.owner.resource += self.owner.resource05  # regen 0.5% resource per hit
                    if self.owner.resource > self.owner.base_resource:  # resource cannot exceed the max resource
                        self.owner.resource = self.owner.base_resource

                if not target.guarding or target.angle == hit_angle or self.no_guard or self.owner.attack_no_guard:
                    # guard bypass if hit from behind or attack ignore guard
                    if self.dmg:  # effect has damage to deal (some may simply be for apply status)
                        if self.owner.player_control:  # count dmg from player for data record
                            self.battle.player_damage[self.owner.player_control] += attacker_dmg
                        target.cal_loss(self.owner, attacker_dmg, self.impact, hit_angle, dmg_text_pos, critical)
                        Effect(None, (
                        "Damaged", "Base", self.rect.topleft[0] + collide_pos[0], self.rect.topleft[1] + collide_pos[1],
                        self.angle, 1, 0, 1), 0)

                    if not self.penetrate and not self.owner.attack_penetrate:
                        if self.stick_reach == "stick":  # stuck at body part
                            self.stuck_part = enemy_part
                            self.stick_timer = 3
                            self.travel_distance = 0
                            self.current_animation = self.animation_pool["Base"][self.scale]  # change image to base
                            self.base_image = self.current_animation[self.show_frame][self.flip]
                            self.adjust_sprite()
                            self.battle.all_damage_effects.remove(self)
                            self.base_stuck_stat = (self.pos - self.stuck_part.rect.center, self.angle,
                                                    self.stuck_part.data, self.stuck_part.owner.angle)
                        elif self.stick_reach == "bounce":
                            self.stick_timer = 5
                    if self.enemy_status_effect:
                        for effect in self.enemy_status_effect:
                            target.apply_status(self.owner, effect)

                else:  # guarded hit, reduce meter
                    if self.owner.player_control:  # player hit enemy guard
                        Effect(None, ("Crash Enemy", "Base", self.rect.centerx, self.rect.centery,
                                      -self.angle, 1, 0, 1), 0)
                    else:  # enemy hit player guard
                        Effect(None, ("Crash Player", "Base", self.rect.centerx, self.rect.centery,
                                      -self.angle, 1, 0, 1), 0)
                    if target.guarding > 0.5:  # not perfect guard (guard within 0.5 secs before taking hit)
                        target.guard -= attacker_dmg * target.guard_cost_modifier
                        if target.crash_guard_resource_regen:
                            target.resource += target.resource1  # regen
                            if target.resource > target.base_resource:  # resource cannot exceed the max resource
                                target.resource = target.base_resource
                        if target.guard < 0:  # guard depleted, break with heavy damaged animation
                            target.guard = 0
                            target.interrupt_animation = True
                            target.command_action = target.guard_break_command_action
                            # target.battle.add_sound_effect_queue(target.sound_effect_pool["Guard Break"][0],
                            #                                      target.base_pos, target.heavy_dmg_sound_distance,
                            #                                      target.heavy_dmg_sound_shake,
                            #                                      volume_mod=target.hit_volume_mod)
                        else:
                            target.show_frame -= 3
                            if target.show_frame < 0:
                                target.show_frame = 0
                            if self.stick_reach and not self.penetrate and not self.owner.attack_penetrate:
                                self.stick_timer = 5
                    else:  # perfect guard, not reduce meter
                        if self.stick_reach and not self.penetrate and not self.owner.attack_penetrate:
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
                        Effect(None,
                               ("Crash Player", "Base", self.rect.centerx, self.rect.centery, -self.angle, 1, 0, 1), 0)
                    else:
                        Effect(None,
                               ("Crash Enemy", "Base", self.rect.centerx, self.rect.centery, -self.angle, 1, 0, 1), 0)
