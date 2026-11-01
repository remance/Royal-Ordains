from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game.game import Game


def back_mainmenu(self: Game):
    self.add_to_ui_menu_updater(self.main_menu_actors)
    self.background = self.background_image["background"]
    self.menu_state = "main_menu"
    self.add_to_ui_menu_updater(*self.main_menu_buttons)
