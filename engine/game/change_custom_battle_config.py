from engine.utils.common import edit_config


def change_custom_battle_config(self):
    edit_config("USER", "selected_custom_stage_battle", self.selected_custom_stage_battle,
                self.config_path, self.config)
    edit_config("USER", "team1_supply_limit_custom_battle", self.team1_supply_limit_custom_battle,
                self.config_path, self.config)
    edit_config("USER", "team2_supply_limit_custom_battle", self.team2_supply_limit_custom_battle,
                self.config_path, self.config)
    edit_config("USER", "team1_gold_limit_custom_battle", self.team1_gold_limit_custom_battle,
                self.config_path, self.config)
    edit_config("USER", "team2_gold_limit_custom_battle", self.team2_gold_limit_custom_battle,
                self.config_path, self.config)
    edit_config("USER", "selected_weather_custom_battle", self.selected_weather_custom_battle,
                self.config_path, self.config)
    edit_config("USER", "selected_weather_strength_custom_battle",
                self.selected_weather_strength_custom_battle, self.config_path, self.config)
