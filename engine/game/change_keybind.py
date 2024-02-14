import ast

from engine.utils.common import edit_config


def change_keybind(self):
    """Change keybind from config data"""
    self.player_key_bind_list = {player: ast.literal_eval(self.config["USER"]["keybind player " + str(player)])
                                 for player in self.player_list}
    self.player_key_control = {player: self.config["USER"]["control player " + str(player)] for player in
                               self.game.player_list}
    self.player_key_bind = {player: self.game.player_key_bind_list[player][self.player_key_control[player]] for
                            player in self.game.player_list}
    self.player_key_bind_name = {player: {value: key for key, value in self.player_key_bind[player].items()} for
                                 player in self.game.player_list}
    self.player_key_press = {player: {key: False for key in self.player_key_bind[player]} for player in
                             self.game.player_list}
    self.player_key_hold = {player: {key: False for key in self.player_key_bind[player]} for player in
                            self.game.player_list}
    self.player_key_bind_button_name = self.get_keybind_button_name()

    edit_config("USER", "control player " + str(self.control_switch.player),
                self.config["USER"]["control player " + str(self.control_switch.player)],
                self.config_path, self.config)
    edit_config("USER", "keybind player " + str(self.control_switch.player),
                self.config["USER"]["keybind player " + str(self.control_switch.player)],
                self.config_path, self.config)

    for key, value in self.keybind_icon.items():
        if self.config["USER"]["control player " + str(self.control_switch.player)] == "joystick":
            value.change_key(self.config["USER"]["control player " + str(self.control_switch.player)],
                             self.player_key_bind_list[self.control_switch.player][
                                 self.config["USER"]["control player " + str(self.control_switch.player)]][key],
                             self.joystick_bind_name[
                                 self.joystick_name[self.player_joystick[self.control_switch.player]]])
        else:
            value.change_key(self.config["USER"]["control player " + str(self.control_switch.player)],
                             self.player_key_bind_list[self.control_switch.player][
                                 self.config["USER"]["control player " + str(self.control_switch.player)]][key],
                             None)
