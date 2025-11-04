from copy import deepcopy


def menu_custom_preset(self):
    if self.preset_back_button.event_press or self.esc_press:  # back to start_set menu
        self.menu_state = "custom"
        self.add_ui_updater(self.custom_battle_menu_uis)
        self.remove_ui_updater(self.custom_preset_menu_uis)
        self.faction_selector.update_coa("Castle")

    elif self.preset_save_button.event_press:
        self.save_data.custom_army_preset_save = deepcopy(self.before_save_preset_army_setup)
        self.save_data.make_save_file("custom_army.dat", self.save_data.custom_army_preset_save)

    else:
        if not self.input_delay:
            for key, pressed in self.player_key_hold.items():
                if pressed and key in custom_preset_key_hold:
                    custom_preset_key_hold[key](self)
                    self.input_delay = 0.15


def go_up(self):
    if not self.custom_army_setup.selected_portrait_index:
        self.custom_army_setup.change_portrait_selection((0, 0))
    else:
        if self.custom_army_setup.selected_portrait_index[0] != 0:
            self.custom_army_setup.change_portrait_selection([value - 1 if not index else value for
                                                              index, value in enumerate(self.custom_army_setup.selected_portrait_index)])


def go_down(self):
    if not self.custom_army_setup.selected_portrait_index:
        self.custom_army_setup.change_portrait_selection((0, 0))
    else:
        if self.custom_army_setup.selected_portrait_index[0] != 4:
            self.custom_army_setup.change_portrait_selection([value + 1 if not index else value for
                                                              index, value in enumerate(self.custom_army_setup.selected_portrait_index)])


def go_left(self):
    if not self.custom_army_setup.selected_portrait_index:
        self.custom_army_setup.change_portrait_selection((0, 0))
    else:
        if len(self.custom_army_setup.selected_portrait_index) == 1:  # air to ground
            self.custom_army_setup.change_portrait_selection((self.custom_army_setup.selected_portrait_index[0], 3))
        elif self.custom_army_setup.selected_portrait_index[1]:
            self.custom_army_setup.change_portrait_selection((self.custom_army_setup.selected_portrait_index[0],
                                                              self.custom_army_setup.selected_portrait_index[1] - 1))


def go_right(self):
    if not self.custom_army_setup.selected_portrait_index:
        self.custom_army_setup.change_portrait_selection((0, 0))
    else:
        if (len(self.custom_army_setup.selected_portrait_index) == 2 and
                self.custom_army_setup.selected_portrait_index[1] == 3):  # ground to air
            self.custom_army_setup.change_portrait_selection((self.custom_army_setup.selected_portrait_index[0],))
        elif len(self.custom_army_setup.selected_portrait_index) == 2:
            self.custom_army_setup.change_portrait_selection((self.custom_army_setup.selected_portrait_index[0],
                                                              self.custom_army_setup.selected_portrait_index[1] + 1))


custom_preset_key_hold = {"Up": go_up, "Down": go_down, "Left": go_left, "Right": go_right}
