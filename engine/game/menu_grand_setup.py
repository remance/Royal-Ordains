from engine.army.army import Army
from engine.constants import Grand_Default_Faction


def menu_grand_setup(self):
    if self.setup_back_button.event_press or self.esc_press:  # back to start_set menu
        self.remove_from_ui_updater(self.grand_menu_uis)
        self.grand_faction_selector.change_faction(Grand_Default_Faction)
        self.back_mainmenu()

    elif self.grand_setup_start_button.event_press:
        army_state = {}
        for army in self.map_data.start_army_list.values():
            army_object = Army(army["Faction"], self.character_list[army["Commander"]]["Culture"], army["Commander"],
                               [army["Leader 1"], army["Leader 2"], army["Leader 3"]],
                               [army["Troop 1"], army["Troop 2"], army["Troop 3"], army["Troop 4"],
                                army["Troop 5"]], [army["Air 1"], army["Air 2"], army["Air 3"], army["Air 4"],
                                army["Air 5"]],
                               [army["Retinue 1"], army["Retinue 2"], army["Retinue 3"]], army["Supply"])
            if army_object.faction not in army_state:
                army_state[army_object.faction] = []
            army_state[army_object.faction].append(army_object)

        game_state = {"region_control": {key: value["Control"] for key, value in
                                         self.map_data.region_by_colour_list.items()},
                      "region_buildings": {key: [value["Build Slot " + str(index)] for index in range(1, 11)] for
                                           key, value in self.map_data.region_by_colour_list.items()},
                      "region_objects": {key: value["Object"] for key, value in
                                         self.map_data.region_by_colour_list.items()},
                      "player_camera_pos": None, "player_faction": None,
                      "faction": {"army": army_state, "order": {}, "plan": {}, "culture": {}}}

        self.grand.prepare_new_campaign("main", self.grand_faction_selector.selected_faction, game_state)

        self.remove_from_ui_updater(self.grand_menu_uis)
        self.grand_faction_selector.change_faction(Grand_Default_Faction)
        self.back_mainmenu()

        self.grand.run_grand()
