from pygame.sprite import spritecollide


def hit_collide_check(self, effect=False):
    """
    Check for collision with enemy effect and body parts
    @param self:
    @param effect:
    @return: Boolean whether the object is killed from collision
    """
    from engine.effect.effect import Effect
    hit_list = spritecollide(self, self.battle.all_effects, False)
    if hit_list:
        for this_effect in hit_list:
            if this_effect.owner != self.owner and this_effect.owner.team != self.owner.team and this_effect.dmg:  # TODO add friendly fire check later
                dmg_diff = abs(this_effect.dmg - self.dmg) / 2
                if dmg_diff < self.dmg / 2:  # both dmg quite near in power
                    this_effect.dmg = 0
                    self.dmg = 0
                    self.can_deal_dmg = False
                    this_effect.can_deal_dmg = False
                    Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                    if effect:
                        self.reach_target()
                    return True
                elif dmg_diff < self.dmg / 4:  # effect damage is much lower
                    this_effect.dmg = 0
                    this_effect.can_deal_dmg = False
                    Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                    this_effect.reach_target()
                else:  # this object dmg is much lower
                    self.dmg = 0
                    self.can_deal_dmg = False
                    Effect(None, ("Crash Enemy", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                    if effect:
                        self.reach_target()
                    return True

    hit_list = spritecollide(self, self.owner.enemy_part_list, False)
    if hit_list:
        for enemy_part in hit_list:  # collide check
            enemy = enemy_part.owner
            if enemy_part.dmg:  # collide attack
                dmg_diff = abs(enemy_part.dmg - self.dmg) / 2
                if dmg_diff < self.dmg / 2:  # both dmg quite near in power
                    enemy_part.dmg = 0
                    self.dmg = 0
                    self.can_deal_dmg = False
                    enemy_part.can_deal_dmg = False
                    self.already_hit.append(enemy)
                    enemy_part.already_hit.append(self.owner)
                    Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                    return True
                elif dmg_diff < self.dmg / 4:  # enemy damage is much lower
                    enemy_part.dmg = 0
                    enemy_part.can_deal_dmg = False
                    enemy_part.already_hit.append(self.owner)
                    if self.owner.player_control:
                        Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                    else:
                        Effect(None, ("Crash Enemy", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                else:  # this object dmg is much lower
                    self.dmg = 0
                    self.can_deal_dmg = False
                    self.already_hit.append(enemy)
                    if self.owner.player_control:  # enemy win
                        Effect(None, ("Crash Enemy", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                    else:  # player win
                        Effect(None, ("Crash Player", "Crash", self.rect.centerx, self.rect.centery, -self.angle), 0)
                    return True

                if effect and not self.penetrate:
                    self.reach_target()
                    return True

            elif enemy_part.can_hurt and enemy not in self.already_hit and "no dmg" not in enemy.current_action:
                self.owner.hit_enemy = True
                self.hit_register(enemy, enemy_part.rect.midtop)
                self.already_hit.append(enemy)

                if effect and not self.penetrate:
                    self.reach_target()
                    return True
