from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.autounitgroup.autounitgroup import AutoUnitGroup

from random import uniform, random
from engine.effect.cal_damage import cal_damage


def cal_damage_and_loss(self: AutoUnitGroup, moveset: dict, enemy_unit: AutoUnitGroup, offence, low_offence):
    effect_list = self.effect_list
    move_id = moveset["Move"]
    self.power = moveset["Power"]
    penetrate = moveset["Penetrate"]
    self.element = moveset["Element"]
    enemy_status = moveset["Enemy Status"]
    effect_enemy_status = moveset["Effect Enemy Status"]
    impact_x = moveset["Impact X"]
    impact_y = moveset["Impact Y"]
    ai_condition = moveset["AI Condition"]
    moveset_property = moveset["Property"]
    critical_chance = self.base_critical_chance + moveset["Critical Chance Bonus"]

    self.no_defence = False
    if "no_defence" in moveset_property:
        self.no_defence = True

    self.no_dodge = False
    if "no_dodge" in moveset_property:
        self.no_dodge = True

    if ("enemy" in ai_condition and "target_type" in ai_condition["enemy"] and
            ai_condition["enemy"]["target_type"] == "air"):
        # effect intend to hit air enemy only
        self.enemy_collision_grids = self.battle.all_team_air_enemy_collision_grids[self.team]

    self.moveset_cooldown[move_id] = moveset["Cooldown"]

    print(self.animation_load_index)
    # effects = [effect for effect in self.animation_load_index[move_id]["effect"] if effect_list[effect]["Damage"]]

    # if effect_enemy_status:

    front_hit = False
    if self.base_pos[0] >= enemy_unit.base_pos[0]:
        if enemy_unit.direction == "right":  # frontal attack
            front_hit = True
    elif enemy_unit.direction == "left":
        front_hit = True

    if enemy_status:  # apply enemy status to target enemy
        for status in enemy_status:
            enemy_unit.apply_status(status)

    enemy_unit_character = enemy_unit.group_character
    enemy_dodge_chance = enemy_unit.dodge_chance
    for _ in self.group_character:  # all characters in group do damage with same moveset
        for enemy_character in sorted(enemy_unit_character, key=lambda x: random()):
            if (uniform(low_offence, offence) >
                    uniform(0, enemy_dodge_chance * 2)):  # make dodge chance a bit higher in auto battle for balance
                if self.power:
                    critical = False
                    if self.critical_chance >= uniform(0, 1):
                        critical = True
                    final_damage = cal_damage(self, enemy_unit, critical, front_hit)
                    if final_damage >= enemy_character["health"]:
                        # character die remove from unit group
                        enemy_unit.character_die(enemy_character)
                    else:
                        enemy_character["health"] -= final_damage

                penetrate -= enemy_unit.body_mass
                if penetrate <= 0:
                    break

    if enemy_unit_character:
        impact_check = (abs(impact_x) + abs(impact_y)) - enemy_unit.body_mass
        if impact_check > enemy_unit.damaged_mass:
            # auto battle impact give status instead
            if impact_check > enemy_unit.knockdown_mass and not enemy_unit.no_forced_move:
                enemy_unit.apply_status("knockdown")

            else:
                enemy_unit.apply_status("damaged")

        # health of group is based on average
        enemy_unit.health = sum(character["health"] for character in enemy_unit_character) / len(enemy_unit_character)
    else:  # entire group is dead
        enemy_unit.group_die()
