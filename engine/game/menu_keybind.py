import pygame


def menu_keybind(self):
    if self.back_button.event_press or self.esc_press:  # back to start_set menu
        self.menu_state = "option"
        self.remove_from_ui_menu_updater(self.keybind_text.values(), self.keybind_icon.values())
        self.add_to_ui_menu_updater(self.option_menu_buttons, self.option_menu_sliders.values(),
                                    self.value_boxes.values())
        self.add_to_ui_menu_updater(self.option_text_list)

    elif self.default_button.event_press:  # revert all keybind of current player to default setting
        for setting in self.config["DEFAULT"]:
            if setting == "keybind":
                self.config["USER"][setting] = self.config["DEFAULT"][setting]
        self.change_keybind()

    else:  # click on key bind button
        for key, value in self.keybind_icon.items():
            if value.event_press:
                self.activate_input_popup(("keybind_input", key),
                                          self.grab_text(("ui", "input_key_assign")) + key,
                                          self.inform_popup_uis)
                current_key = self.player_key_bind_list[key]
                if type(current_key) == int:
                    current_key = pygame.key.name(current_key)
                self.static_input_box.render_text(
                    self.grab_text(("ui", "info_header_current_key")) + current_key)
