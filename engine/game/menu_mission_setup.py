def menu_mission_setup(self):
    if self.setup_back_button.event_press or self.esc_press:  # back to start_set menu
        self.remove_from_ui_updater(self.mission_menu_uis)
        self.back_mainmenu()

    # elif self.mission_setup_start_button.event_press:
    #
    #     self.remove_from_ui_updater(self.mission_menu_uis)
    #     self.back_mainmenu()
    #
    #     self.grand.run_grand()
