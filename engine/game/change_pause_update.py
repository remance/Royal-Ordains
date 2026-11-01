from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game.game import Game


def change_pause_update(self: Game, pause: bool, except_list: (tuple, list) = ()):
    for item in self.ui_menu_updater:
        if item not in except_list:
            item.pause = pause
