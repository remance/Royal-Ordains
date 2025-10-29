def menu_custom_preset(self):
    if self.preset_back_button.event or self.esc_press:  # back to start_set menu
        self.menu_state = "custom"
        self.add_ui_updater(self.custom_battle_menu_uis)
        self.remove_ui_updater(self.custom_preset_menu_uis)
        self.faction_selector.update_coa("Castle")

    elif self.preset_save_button.event:
        pass
