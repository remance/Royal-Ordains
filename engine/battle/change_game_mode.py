from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle.battle import Battle

from types import MethodType


def change_game_mode(self: Battle, new_state: str):
    self.game_mode = new_state
    self.mode_process = MethodType(self.mode_process_list[new_state], self)
    self.player_interact.reset()  # reset rubberband select ui
