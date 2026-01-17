from copy import deepcopy
from os import path

from engine.constants import Custom_Default_Faction


def menu_custom_preset(self):
    if self.preset_back_button.event_press or self.esc_press:  # back to start_set menu
        self.menu_state = "custom"
        self.add_to_ui_updater(self.custom_battle_menu_uis)
        self.remove_from_ui_updater(self.custom_preset_menu_uis)
        self.faction_selector.change_faction(Custom_Default_Faction)
        self.custom_preset_army_setup.change_faction(Custom_Default_Faction)

    elif self.preset_save_button.event_press:
        self.save_data.custom_army_preset_save = deepcopy(self.before_save_preset_army_setup)
        self.save_data.make_save_file(path.join(self.main_dir, "save", "custom_army.dat"),
                                      self.save_data.custom_army_preset_save)

    else:
        if not self.input_delay:
            for key, pressed in self.player_key_hold.items():
                if pressed and key in custom_preset_key_hold:
                    custom_preset_key_hold[key](self)
                    self.input_delay = 0.15


def go_up(self):
    if not self.custom_preset_army_setup.selected_portrait_index:
        self.custom_preset_army_setup.change_portrait_selection((0, 0))
    else:
        if self.custom_preset_army_setup.selected_portrait_index[0] != 0:
            self.custom_preset_army_setup.change_portrait_selection(tuple([value - 1 if not index else value for
                                                                           index, value in enumerate(
                    self.custom_preset_army_setup.selected_portrait_index)]))


def go_down(self):
    if not self.custom_preset_army_setup.selected_portrait_index:
        self.custom_preset_army_setup.change_portrait_selection((0, 0))
    else:
        if self.custom_preset_army_setup.selected_portrait_index[0] != 4:
            self.custom_preset_army_setup.change_portrait_selection(tuple([value + 1 if not index else value for
                                                                           index, value in enumerate(
                    self.custom_preset_army_setup.selected_portrait_index)]))


def go_left(self):
    if not self.custom_preset_army_setup.selected_portrait_index:
        self.custom_preset_army_setup.change_portrait_selection((0, 0))
    else:
        if len(self.custom_preset_army_setup.selected_portrait_index) == 1:  # air to ground
            self.custom_preset_army_setup.change_portrait_selection(
                (self.custom_preset_army_setup.selected_portrait_index[0], 3))
        elif self.custom_preset_army_setup.selected_portrait_index[1]:
            self.custom_preset_army_setup.change_portrait_selection(
                (self.custom_preset_army_setup.selected_portrait_index[0],
                 self.custom_preset_army_setup.selected_portrait_index[1] - 1))


def go_right(self):
    if not self.custom_preset_army_setup.selected_portrait_index:
        self.custom_preset_army_setup.change_portrait_selection((0, 0))
    else:
        if (len(self.custom_preset_army_setup.selected_portrait_index) == 2 and
                self.custom_preset_army_setup.selected_portrait_index[1] == 3):  # ground to air
            self.custom_preset_army_setup.change_portrait_selection(
                (self.custom_preset_army_setup.selected_portrait_index[0],))
        elif len(self.custom_preset_army_setup.selected_portrait_index) == 2:
            self.custom_preset_army_setup.change_portrait_selection(
                (self.custom_preset_army_setup.selected_portrait_index[0],
                 self.custom_preset_army_setup.selected_portrait_index[1] + 1))


custom_preset_key_hold = {"Up": go_up, "Down": go_down, "Left": go_left, "Right": go_right}
