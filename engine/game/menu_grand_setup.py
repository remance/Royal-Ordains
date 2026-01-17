from engine.constants import Custom_Default_Faction


def menu_grand_setup(self):
    if self.setup_back_button.event_press or self.esc_press:  # back to start_set menu
        self.remove_from_ui_updater(self.grand_menu_uis)
        self.faction_selector.change_faction(Custom_Default_Faction)
        self.back_mainmenu()

    elif self.load_grand_button.event_press:
        pass

    # elif self.grand_setup_start_button.event_press:
    #     game_state = {"region_control": {key: value["Control"] for key, value in
    #                                      self.map_data.region_by_colour_list.items()},
    #                   "region_buildings": {key: value["Build Slot"] for key, value in
    #                                        self.map_data.region_by_colour_list.items()},
    #                   "region_objects": {key: value["Object"] for key, value in
    #                                      self.map_data.region_by_colour_list.items()},
    #                   "player_camera_pos": None}
    #
    #     self.grand.prepare_new_campaign("main", self.faction_selector.selected_faction, game_state)
    #
    #     self.remove_from_ui_updater(self.grand_menu_uis)
    #     self.faction_selector.change_faction(Custom_Default_Faction)
    #     self.back_mainmenu()
    #
    #     self.grand.run_grand()
