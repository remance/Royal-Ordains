from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.character.character import CombatCharacter, GrandAutoCharacter

from random import choice, uniform
from engine.effect.cal_damage import cal_damage


def check_status(who: CombatCharacter, status: str):
    if status not in who.status_duration:
        return True
    return None


def check_health_lower(who: CombatCharacter, value: (int, float)):
    if who.health <= who.base_health * value:
        return True
    return None


def check_resource_lower(who: CombatCharacter, value: (int, float)):
    if who.resource <= who.base_resource * value:
        return True
    return None


def check_health_higher(who: CombatCharacter, value: (int, float)):
    if who.health >= who.base_health * value:
        return True
    return None


def check_resource_higher(who: CombatCharacter, value: (int, float)):
    if who.resource >= who.base_resource * value:
        return True
    return None


def check_engage(who: CombatCharacter, value: (int, float)):
    """Check if who has enemy in provided range"""
    if who.nearest_enemy_distance > value:
        return True
    return None


def check_target_type(who: CombatCharacter, value: str):
    """Check if who match the target type value"""
    if who.character_type == value:
        return True
    return None


def check_no_stay(who: CombatCharacter, value: bool):
    """Check that commander order is not stay"""
    check = "stay" not in who.commander_order  # require local variable due to comparison chain issue with is boolean
    if check is value:
        return True
    return None


ai_condition_check_dict = {"health>": check_health_higher, "resource>": check_resource_higher,
                           "health<": check_health_lower, "resource<": check_resource_lower,
                           "no_status": check_status, "no_engage": check_engage,
                           "target_type": check_target_type, "no_stay": check_no_stay}


def leader_condition_check(self: CombatCharacter, value):
    """Require leader to meet condition"""
    if self.commander_character:
        for condition2, value2 in value.items():
            if not ai_condition_check_dict[condition2](self.commander_character, value2):
                return None
        return True
    return None


def allies_condition_check(self: CombatCharacter, value):
    """Require all nearby allies to meet condition"""
    for character in self.near_ally:
        for condition2, value2 in value.items():
            if not ai_condition_check_dict[condition2](character[0], value2):
                return None
    return True


def ally_condition_check(self: CombatCharacter, value):
    """Require one nearby ally to meet condition"""
    for character in self.near_ally:
        for condition2, value2 in value.items():
            if ai_condition_check_dict[condition2](character[0], value2):
                return True
    return None


def self_condition_check(self: CombatCharacter, value):
    """Require self to meet condition"""
    for condition2, value2 in value.items():
        if not ai_condition_check_dict[condition2](self, value2):
            return None
    return True


def enemy_condition_check(self: CombatCharacter, value):
    """Require nearest enemy to meet condition"""
    if self.nearest_enemy and self.nearest_enemy.alive:
        for condition2, value2 in value.items():
            if not ai_condition_check_dict[condition2](self.nearest_enemy, value2):
                return None
        return True
    return None


ai_who_check_dict = {"leader": leader_condition_check, "allies": allies_condition_check,
                     "ally": ally_condition_check, "self": self_condition_check,
                     "enemy": enemy_condition_check}


def check_ai_condition(self: CombatCharacter, condition_dict):
    for condition, value in condition_dict.items():
        if not ai_who_check_dict[condition](self, value):
            return None
    return True


def find_move_to_attack(self: CombatCharacter):
    # has enemy to attack and within max range attack
    # blind cause random direction melee attack but will not allow ranged attack
    resource = self.resource
    furthest_enemy_distance = self.furthest_enemy_distance
    possible_attacks = [value for move, value in self.movesets.items() if
                        move not in self.moveset_cooldown and value["Resource Cost"] <= resource and
                        ((not self.blind and (not value["AI Range"] or
                                              ("far_target" not in value["Property"] and
                                               value["AI Range"] >= self.nearest_enemy_distance) or
                                              ("far_target" in value["Property"] and furthest_enemy_distance and
                                               value["AI Range"] >= furthest_enemy_distance))) or
                         (self.blind and not value["Range"])) and
                        (not value["AI Condition"] or self.check_ai_condition(value["AI Condition"]))]

    if possible_attacks:
        self.current_moveset = choice(possible_attacks)  # randomly select move to attack
        self.current_moveset_property = self.current_moveset["Property"]
        if "far_target" not in self.current_moveset_property:
            self.command_action = self.moveset_command_action | {"target": self.nearest_enemy_pos}
        else:
            self.command_action = self.moveset_command_action | {"target": self.furthest_enemy_pos}
        return True


def no_ai(self: CombatCharacter):
    """No attack at all"""
    pass


# def cheer_ai(self):
#     """No attack but check for target action for appropriate cheering"""
#     if "moveset" in self.target.current_action or "submit" in self.target.current_action or \
#             "taunt" in self.target.current_action:
#         # Cheer when target attack or spared in decision
#         if "cheer" not in self.current_action:  # start cheering
#             self.interrupt_animation = True
#         if "special" in self.target.current_action or "submit" in self.target.current_action:
#             # cheer harder for special occasion
#             self.command_action = self.cheer_fast_action
#         else:  # normal cheer
#             self.command_action = self.cheer_action


def common_ai(self: CombatCharacter):
    """Common combat AI"""
    if "move" not in self.commander_order:
        if self.nearest_enemy and self.nearest_enemy_distance <= self.ai_max_attack_range:
            if not self.ai_timer and (
                    "interruptable" in self.current_action or (not self.command_action and not self.current_moveset)):
                if find_move_to_attack(self):
                    # stop interruptable action to attack
                    self.ai_movement_timer = uniform(0, 5)
                    self.interrupt_animation = True
                    new_direction = "left"
                    if not self.blind:
                        if self.nearest_enemy_pos[0] >= self.base_pos[0]:
                            new_direction = "right"
                    else:
                        # blind cause random direction attack
                        new_direction = choice(("left", "right"))
                    self.command_action["direction"] = new_direction
                self.ai_timer = 0.5


def air_ai(self: CombatCharacter):
    """air type combat AI"""
    if (self.nearest_enemy_pos and not self.command_action and
            not self.current_moveset and not self.ai_timer and
            self.nearest_enemy_distance <= self.ai_max_attack_range):
        if find_move_to_attack(self):  # air character will only interrupt movement if it can attack
            if "interruptable" in self.current_action:
                # stop interruptable action to attack
                self.interrupt_animation = True
        self.ai_timer = 0.5


ai_combat_dict = {"default": no_ai, "melee": common_ai, "range": common_ai, "mix": common_ai,
                  "flank": common_ai, "nice": common_ai, "curious": common_ai, "territorial": common_ai,
                  "trap": common_ai, "leader": common_ai, "interceptor": air_ai, "fighter": air_ai, "bomber": air_ai}


def auto_common_ai(self: GrandAutoCharacter):
    """Common combat AI"""
    if "move" not in self.commander_order and self.nearest_enemy and self.nearest_enemy_distance <= self.ai_max_attack_range:
        if find_move_to_attack(self):
            # stop interruptable action to attack
            self.direction = "left"
            if not self.blind:
                if self.nearest_enemy_pos[0] >= self.base_pos[0]:
                    self.direction = "right"
            else:
                # blind cause random direction attack
                self.direction = choice(("left", "right"))

            target = self.command_action["target"]
            current_moveset = self.current_moveset
            move_id = current_moveset["Move"]
            self.power = current_moveset["power"]
            penetrate = current_moveset["penetrate"]
            self.element = current_moveset["element"]
            status = current_moveset["status"]
            enemy_status = current_moveset["Enemy Status"]
            effect_enemy_status = current_moveset["Effect Enemy Status"]
            impact_x = current_moveset["impact_x"]
            impact_y = current_moveset["impact_y"]
            ai_condition = current_moveset["AI Condition"]

            self.no_defence = False
            if "no_defence" in self.current_moveset["property"]:
                self.no_defence = True

            self.no_dodge = False
            if "no_dodge" in self.current_moveset["property"]:
                self.no_dodge = True

            if ("enemy" in ai_condition and
                    "target_type" in ai_condition["enemy"] and
                    ai_condition["enemy"]["target_type"] == "air"):
                # effect intend to hit air enemy only
                self.enemy_collision_grids = self.battle.all_team_air_enemy_collision_grids[self.team]

            self.moveset_cooldown[move_id] = current_moveset["Cooldown"]
            base_pos_x = self.base_pos[0]

            # if self.animation_load_index[move_id]["sprite"]:
            #     base_pos_x = self.base_pos[0]
            #
            # else:
            #     base_pos_x = target.base_pos[0]
            #     effects = self.animation_load_index[move_id]
            #
            # if status:
            #
            # if enemy_status:
            if self.power:
                for enemy in [enemy2 for enemy2 in self.near_enemy if abs(self.base_pos[0] - enemy2.base_pos[0])]:
                    hit_angle = -90
                    front_hit = False
                    if self.base_pos[0] >= target.base_pos[0]:
                        hit_angle = 90
                        if target.direction == "right":  # frontal attack collide
                            front_hit = True
                    elif target.direction == "left":
                        front_hit = True

                    critical = False
                    if self.critical_chance >= uniform(0, 1):
                        critical = True

                    final_damage = cal_damage(self, target, critical, front_hit)
                    if final_damage > self.health:  # dmg cannot be higher than remaining health
                        self.health = 0
                    else:
                        self.health -= final_damage

                        impact_check = (abs(impact_x) + abs(impact_y)) - self.body_mass

                        if impact_check > self.damaged_mass:
                            if impact_check > self.knockdown_mass and not self.main_character and not self.no_forced_move:
                                # only main characters (has no main character)
                                # and characters that can be forced move can play knockdown animation
                                if hit_angle == 90:  # hit from right side
                                    self.base_pos[0] -= uniform(impact_x * 0.8, impact_x * 1.2) + self.knockdown_mass
                                else:
                                    self.base_pos[0] += uniform(impact_x * 0.8, impact_x * 1.2) - self.knockdown_mass

                            elif "damaged" not in self.current_action:
                                # not already in damaged state
                                if not self.main_character and not self.no_forced_move:
                                    if hit_angle == 90:  # hit from right side
                                        self.base_pos[0] -= uniform(impact_x * 0.8, impact_x * 1.2) + self.damaged_mass
                                    else:
                                        self.base_pos[0] += uniform(impact_x * 0.8, impact_x * 1.2) - self.damaged_mass

                    penetrate -= enemy.body_mass
                    if penetrate <= 0:
                        break


auto_ai_combat_dict = {"default": no_ai, "melee": auto_common_ai, "range": auto_common_ai, "mix": auto_common_ai,
                       "flank": auto_common_ai, "nice": auto_common_ai, "curious": auto_common_ai,
                       "territorial": auto_common_ai, "trap": auto_common_ai, "leader": auto_common_ai,
                       "interceptor": auto_common_ai, "fighter": auto_common_ai, "bomber": auto_common_ai}
