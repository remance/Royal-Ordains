import pygame


def get_keybind_button_name(self):
    final_key_bind_dict = {1: {}, 2: {}, 3: {}, 4: {}}
    for player in range(4):
        player_str = "control player " + str(player + 1)
        if self.config["USER"][player_str] == "joystick":
            name_list = self.joystick_bind_name[self.joystick_name[self.player_joystick[player + 1]]]
            key_bind_list = self.player_key_bind_list[player + 1][self.config["USER"][player_str]]
            for key in self.player_key_bind_list[player + 1]["joystick"]:
                final_key_bind_dict[player + 1][key] = name_list[key_bind_list[key]]
        else:
            for key in self.player_key_bind_list[player + 1]["joystick"]:
                final_key_bind_dict[player + 1][key] = pygame.key.name(self.player_key_bind_list[player + 1][
                                                                           self.config["USER"][player_str]][key])
    return final_key_bind_dict
