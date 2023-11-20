from pygame.sprite import spritecollide, collide_mask


def hit_collide_check(self, check_damage_effect=True):
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
                    if dmg_crash_check(self, this_effect):
                        return True

    hit_list = spritecollide(self, self.owner.enemy_part_list, False,
                             collided=collide_mask)  # check body part collision
    if hit_list:
        for enemy_part in hit_list:
            enemy = enemy_part.owner
            if enemy_part.dmg and check_damage_effect:  # collide attack parts
                if dmg_crash_check(self, enemy_part, body_part=True):
                    return True

            elif enemy_part.can_hurt and enemy not in self.already_hit and \
                    ("no dmg" not in enemy.current_action or not enemy.player_control):  # collide body part
                self.owner.hit_enemy = True
                self.hit_register(enemy, enemy_part)
                self.already_hit.append(enemy)

                if not self.penetrate and not self.stick_reach:
                    self.reach_target()
                    return True

    if self.stick_timer and not self.stuck_part:  # bounce off after reach if not stuck on enemy part
        if self.angle > 0:
            self.x_momentum = 100
        else:
            self.x_momentum = -100
        self.y_momentum = 100
        self.current_animation = self.animation_pool["Base"]  # change image to base
        self.base_image = self.current_animation[self.show_frame]
        self.adjust_sprite()
        self.battle.all_damage_effects.remove(self)


def dmg_crash_check(self, crashed_part, body_part=False):
    from engine.effect.effect import Effect

    if self.owner.crash_guard_resource_regen:  # crash regen resource, 2% instead of normal 1%
        self.owner.resource += self.owner.resource2  # regen
        if self.owner.resource > self.owner.max_resource:  # resource cannot exceed the max resource
            self.owner.resource = self.owner.max_resource

    if self.owner.crash_haste:
        self.owner.apply_status(45)  # get haste buff

    dmg_diff = abs(crashed_part.dmg - self.dmg) / 2
    if dmg_diff < self.dmg / 2:  # both dmg quite near in power
        self.can_deal_dmg = False
        crashed_part.can_deal_dmg = False
        if body_part:
            if crashed_part.object_type == "body":  # only add to already hit if crashed object is body part
                self.already_hit.append(crashed_part.owner)
            if self.object_type == "body":
                crashed_part.already_hit.append(self.owner)
        Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
        if not self.penetrate:  # end effect if not penetrate
            if self.stick_reach:  # bounce off
                self.stick_timer = 5
            else:
                self.reach_target()
                return True
    elif dmg_diff < self.dmg / 4:  # collided effect damage is much lower than this object
        crashed_part.can_deal_dmg = False
        if self.owner.player_control:
            Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
        else:
            Effect(None, ("Crash Enemy", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)

        if not body_part:
            if self.object_type == "body":
                crashed_part.already_hit.append(self.owner)
            if not crashed_part.penetrate:  # end effect if not penetrate
                if crashed_part.stick_reach:  # bounce off
                    crashed_part.stick_timer = 5
                else:
                    crashed_part.reach_target()
    else:  # this object dmg is much lower, enemy win
        self.can_deal_dmg = False
        if crashed_part.object_type == "body":  # only add to already hit if crashed object is body part
            self.already_hit.append(crashed_part.owner)
        Effect(None, ("Crash Enemy", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
        if not self.penetrate:  # end effect if not penetrate
            if self.stick_reach:  # bounce off
                self.stick_timer = 5
            else:
                self.reach_target()
                return True
