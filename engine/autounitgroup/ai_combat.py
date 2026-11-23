from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.character.character import GrandAutoNonCombatCharacter

from random import choice, uniform
from engine.character.ai_combat import find_move_to_attack, no_ai
from engine.effect.cal_damage import cal_damage


def auto_common_ai(self: GrandAutoNonCombatCharacter):
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
