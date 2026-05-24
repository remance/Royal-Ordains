from copy import deepcopy
from os import path

from engine.constants import Custom_Default_Culture


custom_army_character_type_list = ("commander", "leader", "troop", "air")
custom_army_character_type_max_index = {"commander": 0, "retinue": 2, "leader": 2, "troop": 4, "air": 4}  # len - 1


def menu_custom_preset(self):
    if self.preset_back_button.event_press or self.esc_press:  # back to start_set menu
        self.menu_state = "custom"
        self.add_to_ui_menu_updater(self.custom_battle_menu_uis)
        self.remove_from_ui_menu_updater(self.custom_preset_menu_uis)
        self.custom_preset_faction_selector.change_faction(Custom_Default_Culture)
        self.custom_preset_army_setup.change_faction(Custom_Default_Culture)

    elif self.preset_save_button.event_press:
        self.save_data.custom_army_preset_save = deepcopy(self.before_save_preset_army_setup)
        self.save_data.make_save_file(path.join(self.main_dir, "save", "custom_army.dat"),
                                      self.save_data.custom_army_preset_save)
    elif self.character_selector_scroll.event:
        if self.character_selector_scroll.current_row is not None:
            self.character_selector.current_row = self.character_selector_scroll.current_row
            self.character_selector.add_character()
    else:
        if not self.input_delay:
            for key, pressed in self.player_key_hold.items():
                if pressed and key in custom_preset_key_hold:
                    custom_preset_key_hold[key](self)
                    self.input_delay = 0.15


def go_up(self):
    selected_portrait_index = self.custom_preset_army_setup.selected_portrait_index
    if not selected_portrait_index:
        self.custom_preset_army_setup.change_portrait_selection("commander", 0)
    else:
        current_selected_type = selected_portrait_index[0]
        current_index = custom_army_character_type_list.index(current_selected_type)
        if current_index:
            new_type = custom_army_character_type_list[current_index - 1]
            new_index = selected_portrait_index[1]
            if custom_army_character_type_max_index[new_type] < new_index:
                new_index = custom_army_character_type_max_index[new_type]
            self.custom_preset_army_setup.change_portrait_selection(new_type, new_index)


def go_down(self):
    selected_portrait_index = self.custom_preset_army_setup.selected_portrait_index
    if not selected_portrait_index:
        self.custom_preset_army_setup.change_portrait_selection("commander", 0)
    else:
        current_selected_type = selected_portrait_index[0]
        current_index = custom_army_character_type_list.index(current_selected_type)
        if current_index < len(custom_army_character_type_list) - 1:
            new_type = custom_army_character_type_list[current_index + 1]
            new_index = selected_portrait_index[1]
            if custom_army_character_type_max_index[new_type] < new_index:
                new_index = custom_army_character_type_max_index[new_type]
            self.custom_preset_army_setup.change_portrait_selection(new_type, new_index)


def go_left(self):
    selected_portrait_index = self.custom_preset_army_setup.selected_portrait_index
    if not selected_portrait_index:
        self.custom_preset_army_setup.change_portrait_selection("commander", 0)
    else:
        current_selected_type = selected_portrait_index[0]
        new_index = selected_portrait_index[1] - 1
        if new_index < 0:
            new_index = custom_army_character_type_max_index[current_selected_type]
        self.custom_preset_army_setup.change_portrait_selection(current_selected_type, new_index)


def go_right(self):
    selected_portrait_index = self.custom_preset_army_setup.selected_portrait_index
    if not selected_portrait_index:
        self.custom_preset_army_setup.change_portrait_selection("commander", 0)
    else:
        current_selected_type = selected_portrait_index[0]
        new_index = selected_portrait_index[1] + 1
        if new_index > custom_army_character_type_max_index[current_selected_type]:
            new_index = 0
        self.custom_preset_army_setup.change_portrait_selection(current_selected_type, new_index)


custom_preset_key_hold = {"Up": go_up, "Down": go_down, "Left": go_left, "Right": go_right}
