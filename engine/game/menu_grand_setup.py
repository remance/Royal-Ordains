from copy import deepcopy
from random import randint

from engine.constants import Culture_Policy_Integration


def menu_grand_setup(self):
    if self.setup_back_button.event_press or self.esc_press:  # back to start_set menu
        self.remove_from_ui_updater(self.grand_menu_uis)
        self.grand_faction_selector.change_faction(self.map_data.default_grand_faction)
        self.back_mainmenu()

    elif self.grand_setup_start_button.event_press:
        all_faction_state = {}
        free_faction_state = {}
        player_faction = self.grand_faction_selector.selected_faction
        for faction, faction_value in self.map_data.faction_list.items():
            # start faction culture set at max level policy and max integration
            faction_state = all_faction_state
            if faction == "free":
                faction_state = free_faction_state
            faction_state[faction] = {"army": [], "reserve": [], "plan": {},
                                      "region": [key for key, value in self.map_data.region_list.items() if
                                                 value["Control"] == faction],
                                      "culture": {
                                          faction_value["Culture"]: {
                                              "policy": tuple(Culture_Policy_Integration.keys())[-1],
                                              "influence": 1, "weight": 1, "integration": 1}},
                                      "character": {},
                                      "gold": faction_value["Start Gold"], "supply": faction_value["Start Supply"],
                                      "gold_income": faction_value["Gold Income"],
                                      "supply_income": faction_value["Supply Income"], "happiness": 0,
                                      "gold_effect": {"start_income": faction_value["Gold Income"],
                                                      "region_income": [], "army_upkeep": []},
                                      "supply_effect": {"start_income": faction_value["Supply Income"],
                                                        "region_income": []},
                                      "happiness_effect": {"region_income": [],
                                                           "influence_effect": [],
                                                           "coexist_effect": [],
                                                           "event_effect": []},
                                      "event": {}, "relation": faction_value["Faction Relation"]}

        for army_id, army in self.map_data.start_army_list.items():
            faction_state = all_faction_state
            if army["Faction"] == "free":
                faction_state = free_faction_state
            faction_state[army["Faction"]]["army"].append(army)
            for character in (army["Commander"], army["Leader 1"], army["Leader 2"], army["Leader 3"],
                              army["Retinue 1"], army["Retinue 2"], army["Retinue 3"]):
                if character and self.character_list[character]["Is Unique"]:
                    # assign starting army id to unique character in it
                    faction_state[army["Faction"]]["character"][character] = army_id

        campaign_state = {"player_camera_pos": None, "player_faction": None,
                          "region": {"control": {key: value["Control"] for key, value in
                                                 self.map_data.region_list.items()},
                                     "buildings": {key: [value["Build Slot " + str(index)] for index in range(1, 11) if
                                                         value["Build Slot " + str(index)]] for key, value in
                                                   self.map_data.region_list.items()},
                                     "objects": {key: value["Object"] for key, value in
                                                 self.map_data.region_list.items()},
                                     "income": {key: {"gold_income": 0, "supply_income": 0, "happiness": 0} for key in
                                                self.map_data.region_list}
                                     },
                          "free_leader": {},
                          "battle": {"armies": {}, "auto": {}, "manual": None},
                          "pathfinding": {}, "possible_events": deepcopy(self.map_data.event_list),
                          "faction": all_faction_state,
                          "free_faction": free_faction_state["free"], "eventlog": [],
                          "time": randint(0, 999999999999999999999999),
                          "turn": 1, "phase": 1}

        self.grand.prepare_new_campaign("main", player_faction, campaign_state)

        # after quit grand campaign
        self.remove_from_ui_updater(self.grand_menu_uis)
        self.grand_faction_selector.change_faction(self.map_data.default_grand_faction)
        self.back_mainmenu()

        self.grand.run_grand()
