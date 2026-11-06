from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from engine.game.activate_input_popup import activate_input_popup as game_activate_input_popup


def activate_input_popup(self: Grand, input_popup, instruction, input_ui_list):
    game_activate_input_popup(self, input_popup, instruction, input_ui_list)
    self.add_to_ui_menu_updater(self.cursor)
