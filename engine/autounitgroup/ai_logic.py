from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.autounitgroup.autounitgroup import AutoUnitGroup


def auto_ai_logic(self: AutoUnitGroup):
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
