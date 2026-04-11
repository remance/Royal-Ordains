from copy import deepcopy
from os import path

from engine.constants import Custom_Default_Culture


def menu_custom_preset(self):
    if self.preset_back_button.event_press or self.esc_press:  # back to custom battle setup menu
        self.menu_state = "custom"
        self.add_to_ui_menu_updater(self.custom_battle_menu_uis)
        self.remove_from_ui_menu_updater(self.custom_preset_menu_uis)
        self.custom_preset_culture_selector.change_culture_preset(Custom_Default_Culture)
        self.custom_preset_army_setup.change_culture_preset(Custom_Default_Culture)

    elif self.preset_save_button.event_press:
        self.save_data.make_save_file(path.join(self.main_dir, "save", "custom_army.dat"),
                                      self.before_save_preset_army_setup)
        self.save_data.player_custom_army_preset_save = self.before_save_preset_army_setup
        self.before_save_preset_army_setup = deepcopy(self.save_data.player_custom_army_preset_save)

    elif self.character_selector.scroll.event:
        if self.character_selector.scroll.current_row is not None:
            self.character_selector.current_row = self.character_selector.scroll.current_row
            self.character_selector.add_character()
