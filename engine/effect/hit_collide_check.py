from math import log2
from random import uniform

from pygame.sprite import collide_mask

import engine.effect.effect

direction_to_angle = {"right": -90, "left": 90}


def hit_collide_check(self):
    """
    Check for collision with enemy character sprite
    @param self: BattleCharacter or DamageEffect object
    @return: Boolean whether the object is deleted from collision
    """
    for grid in self.grid_range:
        for enemy in self.enemy_collision_grids[grid]:
            if enemy.health and collide_mask(self, enemy):
                if not self.is_effect_type and enemy.sprite_deal_damage:
                    # character sprite attack collide with enemy sprite attack
                    if melee_impact_crash_check(self, enemy):  # lose in crash
                        return True
                if enemy not in self.already_hit:
                    self.already_hit.append(enemy)
                    if uniform(self.offence * 0.5, self.offence) > uniform(0, enemy.speed):  # check for dodge
                        self.penetrate -= enemy.body_mass
                        if self.penetrate < 0:
                            self.penetrate = 0
                        self.hit_register(enemy)
                        if not self.penetrate:
                            if self.is_effect_type:
                                if self.remain_check:
                                    if self.remain_reach == "bounce":
                                        sprite_bounce(self)
                                elif len(self.current_animation) == 1:
                                    self.reach_target()
                                    return True
                            else:
                                return


def melee_impact_crash_check(self, enemy):
    impact = 0
    if self.impact_sum:
        impact = log2(self.impact_sum)
    enemy_impact = 0
    if enemy.impact_sum:
        enemy_impact = log2(enemy.impact_sum)
    impact_diff = impact - enemy_impact
    if -1 < impact_diff < 1:  # both impact quite near in value
        engine.effect.effect.Effect(None, ("Crash Player", "Base", self.base_pos[0],
                                     self.base_pos[1], direction_to_angle[self.direction], 0, 0, 1, 1),
                                    from_owner=False)
        engine.effect.effect.Effect(None, ("Crash Enemy", "Base", enemy.base_pos[0],
                                     enemy.base_pos[1], direction_to_angle[enemy.direction], 0, 0, 1, 1),
                                    from_owner=False)
        self.interrupt_animation = True
        self.command_action = self.damaged_command_action
        self.sprite_deal_damage = False
        enemy.interrupt_animation = True
        enemy.command_action = enemy.damaged_command_action
        enemy.sprite_deal_damage = False
    elif impact_diff > 1:  # collided enemy damage is much lower than this object, enemy lose
        engine.effect.effect.Effect(None, ("Crash Player", "Base", self.base_pos[0],
                                     self.base_pos[1], direction_to_angle[self.direction], 0, 0, 1, 1),
                                    from_owner=False)
        enemy.interrupt_animation = True
        enemy.command_action = enemy.damaged_command_action
        enemy.sprite_deal_damage = False
    else:  # this object dmg is much lower, enemy win
        engine.effect.effect.Effect(None, ("Crash Enemy", "Base", enemy.base_pos[0],
                                           enemy.base_pos[1], direction_to_angle[enemy.direction], 0, 0, 1, 1),
                                    from_owner=False)
        self.interrupt_animation = True
        self.command_action = self.damaged_command_action
        self.sprite_deal_damage = False


def sprite_bounce(self):
    if self.angle > 0:
        self.x_momentum /= 2
        if self.x_momentum < 100:
            self.x_momentum = 100
    else:
        self.x_momentum /= -2
        if self.x_momentum > -100:
            self.x_momentum = -100
    self.y_momentum = abs(self.y_momentum / 2)
    if self.y_momentum < 100:
        self.y_momentum = 100

    # change image to base
    self.current_animation = self.animation_pool["Base"][self.sprite_flip][self.width_scale][self.height_scale]
    self.base_image = self.current_animation[self.show_frame]
    self.adjust_sprite()
