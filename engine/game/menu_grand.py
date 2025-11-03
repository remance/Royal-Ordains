def menu_grand(self):
    if self.setup_back_button.event_press or self.esc_press:  # back to start_set menu
        self.remove_ui_updater(self.grand_menu_uis)
        self.faction_selector.update_coa("Castle")
        self.back_mainmenu()

    elif self.grand_setup_confirm_battle_button.event_press:
        pass
