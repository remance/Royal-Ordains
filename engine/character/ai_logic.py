from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.character.character import CombatCharacter, GrandAutoNonCombatCharacter

from engine.constants import Phase_To_Round, Round_To_Battle_Time

Tick_to_Second = Round_To_Battle_Time / Phase_To_Round


def ai_logic(self: CombatCharacter, dt: float):
    if self.ai_timer:
        self.ai_timer -= dt
        if self.ai_timer < 0:
            self.ai_timer = 0
    if not self.broken and "broken" not in self.commander_order:
        self.ai_combat()
        if not self.ai_movement_timer:
            self.ai_move()
        else:
            self.ai_movement_timer -= dt
            if self.ai_movement_timer < 0:
                self.ai_movement_timer = 0
    else:
        self.ai_retreat()


def auto_ai_logic(self: GrandAutoNonCombatCharacter):
    if not self.broken and "broken" not in self.commander_order:
        self.ai_prepare()
        if "idle" not in self.commander_order:
            # move first
            self.ai_move()
        if self.nearest_enemy and self.nearest_enemy_distance <= self.ai_max_attack_range:
            # perform attack
            self.ai_combat()
    else:
        self.ai_retreat()
