from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game.game import Game

import pygame


def get_keybind_button_name(self: Game):
    final_key_bind_dict = {}
    for key in self.player_key_bind_list:
        final_key_bind_dict[key] = pygame.key.name(self.player_key_bind_list[key])
    return final_key_bind_dict
