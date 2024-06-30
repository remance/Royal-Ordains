from math import log2

from pygame.sprite import spritecollide, collide_mask


def hit_collide_check(self, check_damage_effect=True):
    from engine.effect.effect import Effect
    """
    Check for collision with enemy effect and body parts
    @param self: Effect object
    @param check_damage_effect: Check for damage effect collision before body parts, also check for bodypart that deal damage
    @return: Boolean whether the object is killed from collision
    """
    if check_damage_effect:
        hit_list = spritecollide(self, self.battle.all_damage_effects, False,
                                 collided=collide_mask)  # check for effect collision
        if hit_list:
            for this_effect in hit_list:
                if this_effect.owner.team != self.owner.team and this_effect.dmg:
                    if impact_crash_check(self, this_effect):  # lose in crash
                        return True

    hit_list = spritecollide(self, self.owner.enemy_part_list, False,
                             collided=collide_mask)  # check body part collision
    if hit_list:
        for enemy_part in hit_list:
            enemy = enemy_part.owner
            if enemy_part.dmg and check_damage_effect:  # collide attack parts
                if impact_crash_check(self, enemy_part):  # lose in crash
                    return True

            elif enemy_part.can_hurt and enemy not in self.already_hit and \
                    ("no dmg" not in enemy.current_action or not enemy.player_control):  # collide body part
                collide_pos = collide_mask(self, enemy_part)
                if collide_pos:  # in case collide change
                    self.owner.hit_enemy = True
                    self.hit_register(enemy, enemy_part, collide_pos)
                    self.already_hit.append(enemy)

                    if not self.penetrate and not self.owner.attack_penetrate and not self.stick_reach:
                        self.reach_target()
                        return True
    if self.stick_timer and not self.stuck_part:  # bounce off after reach if not stuck on enemy part
        sprite_bounce(self)


def impact_crash_check(self, crashed_part):
    from engine.effect.effect import Effect

    if self.owner.crash_guard_resource_regen:  # crash regen resource, 2% instead of normal 1%
        self.owner.resource += self.owner.resource2  # regen
        if self.owner.resource > self.owner.base_resource:  # resource cannot exceed the max resource
            self.owner.resource = self.owner.base_resource

    if self.owner.crash_haste:
        self.owner.apply_status(self.owner, 45)  # get haste buff
    impact = 0
    if self.impact_sum:
        impact = log2(self.impact_sum)
    enemy_impact = 0
    if crashed_part.impact_sum:
        enemy_impact = log2(crashed_part.impact_sum)
    impact_diff = impact - enemy_impact
    if -1 < impact_diff < 1:  # both dmg quite near in power
        self.can_deal_dmg = False
        crashed_part.can_deal_dmg = False
        crashed_part.already_hit.append(self.owner)
        self.already_hit.append(crashed_part.owner)
        if crashed_part.object_type == "body":  # play damaged animation if crash part is not effect
            crashed_part.owner.interrupt_animation = True
            if not self.owner.no_forced_move:
                crashed_part.owner.command_action = crashed_part.owner.heavy_damaged_command_action
        if self.object_type == "body":
            self.owner.interrupt_animation = True
            if not crashed_part.owner.no_forced_move:
                self.owner.command_action = self.owner.heavy_damaged_command_action
        Effect(None, ("Crash Player", "Base", self.rect.centerx, self.rect.centery, -self.angle, 1, 0, 1), 0)
        if self.object_type == "effect":  # end effect
            if self.stick_reach:  # bounce off
                self.stick_timer = 5
                sprite_bounce(self)
                return True
            else:
                self.reach_target()
                return True
        if crashed_part.object_type == "effect":  # end enemy effect
            if crashed_part.stick_reach:  # bounce off
                crashed_part.stick_timer = 5
                sprite_bounce(crashed_part)
            else:
                crashed_part.reach_target()
    elif impact_diff > 1:  # collided enemy damage is much lower than this object, enemy lose
        crashed_part.can_deal_dmg = False
        if self.owner.player_control:
            Effect(None, ("Crash Player", "Base", self.rect.centerx, self.rect.centery, -self.angle, 1, 0, 1), 0)
        else:
            Effect(None, ("Crash Enemy", "Base", self.rect.centerx, self.rect.centery, -self.angle, 1, 0, 1), 0)
        crashed_part.already_hit.append(self.owner)
        if crashed_part.object_type == "body":  # collided with enemy body part
            crashed_part.owner.interrupt_animation = True
            if not crashed_part.owner.no_forced_move:
                crashed_part.owner.command_action = crashed_part.owner.heavy_damaged_command_action
        elif crashed_part.object_type == "effect":  # end enemy effect
            if crashed_part.stick_reach:  # bounce off
                crashed_part.stick_timer = 5
                sprite_bounce(crashed_part)
            else:
                crashed_part.reach_target()
    else:  # this object dmg is much lower, enemy win
        self.can_deal_dmg = False
        Effect(None, ("Crash Enemy", "Base", self.rect.centerx, self.rect.centery, -self.angle, 1, 0, 1), 0)
        self.already_hit.append(crashed_part.owner)
        if self.object_type == "body":  # body part object collide with enemy
            self.owner.interrupt_animation = True
            if not self.owner.no_forced_move:
                self.owner.command_action = self.owner.heavy_damaged_command_action
        elif self.object_type == "effect":  # end effect
            if self.stick_reach:  # bounce off
                self.stick_timer = 5
                sprite_bounce(self)
                return True
            else:
                self.reach_target()
                return True


def sprite_bounce(self):
    if self.angle > 0:
        self.x_momentum = 100
    else:
        self.x_momentum = -100
    self.y_momentum = 100
    self.current_animation = self.animation_pool["Base"][self.scale]  # change image to base
    self.base_image = self.current_animation[self.show_frame][self.flip]
    self.adjust_sprite()
    self.battle.all_damage_effects.remove(self)
