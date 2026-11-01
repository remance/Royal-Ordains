from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game.game import Game

import ast

from engine.utils.common import edit_config


def change_keybind(self: Game):
    """Change keybind from config data"""
    config = self.config
    self.player_key_bind_list = ast.literal_eval(config["USER"]["keybind"])

    self.player_key_bind = self.player_key_bind_list
    self.player_key_bind_name = {value: key for key, value in self.player_key_bind.items()}
    self.player_key_press = {key: False for key in self.player_key_bind}
    self.player_key_hold = {key: False for key in self.player_key_bind}

    edit_config("USER", "keybind", config["USER"]["keybind"],
                self.config_path, config)

    for key, value in self.keybind_icon.items():
        value.change_key(self.player_key_bind_list[key])
