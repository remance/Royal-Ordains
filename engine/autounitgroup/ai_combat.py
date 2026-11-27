from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.autounitgroup.autounitgroup import AutoUnitGroup

from random import choice
from engine.character.ai_combat import find_move_to_attack
from engine.utils.common import empty_method


def auto_common_ai(self: AutoUnitGroup):
    """Common combat AI"""
    if find_move_to_attack(self):
        # stop interruptable action to attack
        self.direction = "left"
        if not self.blind:
            if self.nearest_enemy_pos[0] >= self.base_pos[0]:
                self.direction = "right"
        else:
            # blind cause random direction attack
            self.direction = choice(("left", "right"))

        current_moveset = self.current_moveset
        status = current_moveset["Status"]
        move_range = current_moveset["Range"]
        enemy_status = current_moveset["Enemy Status"]
        if "far_target" not in current_moveset["Property"]:
            enemy_unit = self.nearest_enemy
        else:
            enemy_unit = self.furthest_enemy
        self.cal_damage_and_loss(self.current_moveset, enemy_unit, self.offence, self.low_offence)

        if status:  # apply status to nearby allies
            for ally, distance in self.near_ally:
                for this_status in status:
                    ally.apply_status(this_status)
                if distance > move_range:
                    break

        if move_range and enemy_status:  # apply status to all enemies within range if moveset has range
            for enemy_group, distance in self.near_enemy.items():
                if move_range > distance:
                    enemy_group.apply_status()
                else:
                    break


auto_ai_combat_dict = {"default": empty_method, "melee": auto_common_ai, "range": auto_common_ai, "mix": auto_common_ai,
                       "flank": auto_common_ai, "nice": auto_common_ai, "curious": auto_common_ai,
                       "territorial": auto_common_ai, "trap": auto_common_ai, "leader": auto_common_ai,
                       "interceptor": auto_common_ai, "fighter": auto_common_ai, "bomber": auto_common_ai}
