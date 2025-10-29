import ast

from engine.utils.common import edit_config


def change_keybind(self):
    """Change keybind from config data"""
    self.player_key_bind_list = ast.literal_eval(self.config["USER"]["keybind"])

    self.player_key_bind = self.player_key_bind_list
    self.player_key_bind_name = {value: key for key, value in self.player_key_bind.items()}
    self.player_key_press = {key: False for key in self.player_key_bind}
    self.player_key_hold = {key: False for key in self.player_key_bind}  # key that consider holding
    self.player_key_bind_button_name = self.get_keybind_button_name()

    edit_config("USER", "keybind", self.config["USER"]["keybind"],
                self.config_path, self.config)

    for key, value in self.keybind_icon.items():
        value.change_key(self.player_key_bind_list[key])
