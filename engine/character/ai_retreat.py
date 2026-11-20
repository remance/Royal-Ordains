from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.character.character import CombatCharacter, GrandAutoCharacter


def common_ai(self: CombatCharacter, *args):
    if not self.command_action and not self.no_move:
        self.command_action = self.run_command_action
        self.command_action["x_momentum"] = self.run_speed
        if self.retreat_pos <= 0:
            self.command_action["direction"] = "left"
        else:
            self.command_action["direction"] = "right"


ai_retreat_dict = {"default": common_ai}


def auto_common_ai(self: GrandAutoCharacter, *args):
    if not self.no_move:
        if self.retreat_pos <= 0:
            self.base_pos[0] -= self.run_speed
        else:
            self.base_pos[0] += self.run_speed

auto_ai_retreat_dict = {"default": common_ai}
