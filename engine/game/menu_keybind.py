import pygame


def menu_keybind(self, esc_press):
    if self.back_button.event or esc_press:  # back to start_set menu
        self.back_button.event = False

        self.menu_state = "option"
        self.remove_ui_updater(self.keybind_text.values(), self.keybind_icon.values(), self.control_switch,
                               self.control_player_back, self.control_player_next)
        self.add_ui_updater(self.option_menu_button, self.option_menu_sliders.values(), self.value_boxes.values())
        self.add_ui_updater(self.option_text_list)

    elif self.default_button.event:  # revert all keybind of current player to default setting
        self.default_button.event = False
        for setting in self.config["DEFAULT"]:
            if setting == "keybind player " + str(self.control_switch.player):
                self.config["USER"][setting] = self.config["DEFAULT"][setting]
        self.change_keybind()

    elif self.control_player_next.event_press or self.control_player_back.event_press:  # change player
        if self.control_player_next.event_press:
            new_player = self.control_switch.player + 1
            if new_player > 4:
                new_player = 1
        else:
            new_player = self.control_switch.player - 1
            if new_player == 0:
                new_player = 4

        if self.config["USER"]["control player " + str(new_player)] == "joystick":  # joystick control
            self.control_switch.change_control(
                self.player_key_control[new_player] + str(self.player_joystick[new_player]), new_player)
        else:  # keyboard control
            self.control_switch.change_control("keyboard", new_player)

        for key, value in self.keybind_icon.items():
            keybind_name = None
            if self.config["USER"]["control player " + str(new_player)] == "joystick":
                keybind_name = self.joystick_bind_name[self.joystick_name[self.player_joystick[new_player]]]
            value.change_key(self.config["USER"]["control player " + str(new_player)],
                             self.player_key_bind_list[new_player][
                                 self.config["USER"]["control player " + str(new_player)]][key],
                             keybind_name)

    elif self.control_switch.event_press:
        if self.config["USER"]["control player " + str(self.control_switch.player)] == "keyboard":
            if self.joysticks:  # has connected joystick
                found_joy = None
                for joy_id in self.joysticks:
                    if joy_id not in self.player_joystick.values():  # found free joy
                        found_joy = joy_id
                        break
                if found_joy is not None:
                    self.config["USER"]["control player " + str(self.control_switch.player)] = "joystick"
                    self.player_joystick[self.control_switch.player] = found_joy
                    self.joystick_player[found_joy] = self.control_switch.player
                    self.control_switch.change_control("joystick" + str(found_joy), self.control_switch.player)
                    self.change_keybind()
                else:  # no free joy
                    self.activate_input_popup(("confirm_input", "warning"),
                                              "No free joysticks", self.inform_ui_popup)
                    return
            else:  # no joy
                self.activate_input_popup(("confirm_input", "warning"),
                                          "No joysticks", self.inform_ui_popup)

        else:  # change to keyboard
            if self.control_switch.player in self.player_joystick:
                self.joystick_player.pop(self.player_joystick[self.control_switch.player])
                self.player_joystick.pop(self.control_switch.player)
                self.config["USER"]["control player " + str(self.control_switch.player)] = "keyboard"
                self.control_switch.change_control("keyboard", self.control_switch.player)
                self.change_keybind()

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
