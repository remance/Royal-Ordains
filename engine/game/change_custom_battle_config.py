from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game.game import Game

from engine.utils.common import edit_config


def change_custom_battle_config(self: Game):
    config_path = self.config_path
    config = self.config
    edit_config("USER", "selected_custom_stage_battle", self.selected_custom_stage_battle,
                config_path, config)
    edit_config("USER", "team1_supply_limit_custom_battle", self.team1_supply_limit_custom_battle,
                config_path, config)
    edit_config("USER", "team2_supply_limit_custom_battle", self.team2_supply_limit_custom_battle,
                config_path, config)
    edit_config("USER", "team1_gold_limit_custom_battle", self.team1_gold_limit_custom_battle,
                config_path, config)
    edit_config("USER", "team2_gold_limit_custom_battle", self.team2_gold_limit_custom_battle,
                config_path, config)
    edit_config("USER", "selected_weather_custom_battle", self.selected_weather_custom_battle,
                config_path, config)
    edit_config("USER", "selected_weather_strength_custom_battle",
                self.selected_weather_strength_custom_battle, config_path, config)
