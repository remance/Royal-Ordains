import pygame

from engine.utils.common import edit_config


def menu_keybind(self, esc_press):
    if self.back_button.event or esc_press:  # back to start_set menu
        self.back_button.event = False

        self.menu_state = "option"
        self.remove_ui_updater(self.keybind_text.values(), self.keybind_icon.values(), self.control_switch,
                               self.control_player_back, self.control_player_next)
        self.add_ui_updater(self.option_menu_button, self.option_menu_sliders.values(), self.value_boxes.values())
        self.add_ui_updater(self.option_text_list)

    elif self.default_button.event:  # revert all keybind of current player to original
        self.default_button.event = False
        for setting in self.config["DEFAULT"]:
            if setting == "keybind":
                edit_config("USER", setting, self.config["DEFAULT"][setting], self.config_path, self.config)
        control_type = self.config["USER"]["control player " + str(self.control_switch.player)]
        for key, value in self.keybind_icon.items():
            if self.joysticks:
                value.change_key(control_type,
                                 self.config["USER"]["keybind player " + str(self.control_switch.player)][control_type][
                                     key],
                                 self.joystick_bind_name[self.joystick_name[tuple(self.joystick_name.keys())[0]]])
            else:
                value.change_key(control_type,
                                 self.config["USER"]["keybind player " + str(self.control_switch.player)][control_type][
                                     key], None)

    elif self.control_player_next.event_press:
        new_player = self.control_switch.player + 1
        if new_player == 5:
            new_player = 1
        # if self.config["USER"]["control player " + str(new_player)] == "joystick":
        # self.control_switch.change_control("joystick1")
        self.control_switch.change_control(self.control_switch.control_type, new_player)
        for key, value in self.keybind_icon.items():
            keybind_name = None
            if self.config["USER"]["control player " + str(new_player)] == "joystick":
                keybind_name = self.joystick_bind_name[self.joystick_name[tuple(self.joystick_name.keys())[0]]]
            value.change_key(self.config["USER"]["control player " + str(new_player)],
                             self.player_key_bind_list[new_player][
                                 self.config["USER"]["control player " + str(new_player)]][key],
                             keybind_name)

    elif self.control_player_back.event_press:
        new_player = self.control_switch.player - 1
        if new_player == 0:
            new_player = 4
        self.control_switch.change_control(self.control_switch.control_type, new_player)
        for key, value in self.keybind_icon.items():
            keybind_name = None
            if self.config["USER"]["control player " + str(new_player)] == "joystick":
                keybind_name = self.joystick_bind_name[self.joystick_name[tuple(self.joystick_name.keys())[0]]]
            value.change_key(self.config["USER"]["control player " + str(new_player)],
                             self.player_key_bind_list[new_player][
                                 self.config["USER"]["control player " + str(new_player)]][key],
                             keybind_name)

    elif self.control_switch.event_press:
        if self.joysticks:
            if self.config["USER"]["control player " + str(self.control_switch.player)] == "keyboard":
                self.config["USER"]["control player " + str(self.control_switch.player)] = "joystick"
                self.control_switch.change_control("joystick1")
            else:
                # if self.config["USER"]["control player 2"] == "joystick"
                self.config["USER"]["control player " + str(self.control_switch.player)] = "keyboard"
                self.control_switch.change_control("keyboard")
            self.player_key_control[self.control_switch.player] = self.config["USER"][
                "control player " + str(self.control_switch.player)]
            edit_config("USER", "control player " + str(self.control_switch.player),
                        self.config["USER"]["control player " + str(self.control_switch.player)],
                        self.config_path, self.config)
            for key, value in self.keybind_icon.items():
                if self.joysticks:
                    value.change_key(self.config["USER"]["control player " + str(self.control_switch.player)],
                                     self.player_key_bind[self.control_switch.player][
                                         self.config["USER"]["control player " + str(self.control_switch.player)]][key],
                                     self.joystick_bind_name[
                                         self.joystick_name[tuple(self.joystick_name.keys())[0]]])
                else:
                    value.change_key(self.config["USER"]["control player " + str(self.control_switch.player)],
                                     self.player_key_bind[self.control_switch.player][
                                         self.config["USER"]["control player " + str(self.control_switch.player)]][key],
                                     None)

        else:
            self.activate_input_popup(("confirm_input", "warning"),
                                      "No joysticks detected", self.inform_ui_popup)

    else:  # click on key bind button
        for key, value in self.keybind_icon.items():
            if value.event_press:
                self.activate_input_popup(("keybind_input", key),
                                          "Assign key for " + key, self.inform_ui_popup)
                current_key = self.player_key_bind_list[self.control_switch.player][
                    self.config["USER"]["control player " + str(self.control_switch.player)]][key]
                if type(current_key) == int:
                    current_key = pygame.key.name(current_key)
                self.input_box.text_start("Current Key: " + current_key)
