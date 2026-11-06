from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game.game import Game
    from engine.grand.grand import Grand


def activate_input_popup(self: (Game, Grand), input_popup, instruction, input_ui_list):
    self.remove_from_ui_menu_updater(self.all_input_popup_uis)  # remove any previous input ui first
    self.change_pause_update(True, except_list=self.all_input_popup_uis)

    self.input_popup = input_popup
    self.input_ui.change_instruction(instruction)
    self.add_to_ui_menu_updater(input_ui_list)
