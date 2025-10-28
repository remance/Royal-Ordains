def menu_custom_preset(self):
    if self.preset_back_button.event or self.esc_press:  # back to start_set menu
        self.background = self.background_image["background"]
        self.add_ui_updater(self.main_menu_actor)
        self.remove_ui_updater(self.custom_battle_menu_buttons)
        self.back_mainmenu()

    elif self.preset_save_button.event:
        pass