from math import ceil
from engine.constants import Turn_To_Phase

time_per_phase = 1 / Turn_To_Phase  # 1 cosmic time is 1 turn


def change_phase(self, phase_change=True):
    if phase_change:
        current_campaign_state = self.current_campaign_state
        self.cosmic_ui.phase_change()
        current_campaign_state["cosmic_time"] += time_per_phase
        current_campaign_state["cosmic_event"] = {key: value - 1 for key, value in
                                                  current_campaign_state["cosmic_event"].items() if value > 1}

        # process respective faction ai assigned to the phase
        for faction, faction_state in current_campaign_state["faction"].items():
            for army in faction_state["army"]:
                army.change_phase()

                for region in faction_state["region"]:  # TODO add requirement check
                    region_state_change = False
                    building_state_change = []
                    for index, building_state in enumerate(current_campaign_state["region"]["building"][region]):
                        building = building_state[0]
                        if building_state[2]:  # ongoing razing/pillaging/construction/repair
                            building_state[2] -= 1
                            building_state_change.append((index, building_state))
                            if not building_state[2]:  # finish progress
                                region_state_change = True
                                if not building_state[1]:
                                    building_state[1] = True
                                else:
                                    turn_text = str(current_campaign_state["turn"]) + "." + str(current_campaign_state["phase"])
                                    building_text = (self.grab_text(("region", region, "Name")) + "/ " +
                                                     self.grab_text(("building", building, "Name")))
                                    if building_state[1] == "pillage":
                                        building_state[1] = False
                                        # receive half building cost gold
                                        faction_state["gold"] += ceil(self.building_list[building]["Cost"] / 2)
                                        if faction == self.player_faction:
                                            self.event_notification_ui.add_new_event((
                                                "event_pillage", building_text +
                                                self.grab_text(("ui", "info_text_pillage_done")),
                                                turn_text, self.region_list[region]["Settlement POS"]))
                                    elif building_state[1] == "raze":
                                        # downgrade after finish razing
                                        building_state[0] = self.building_list[building]["Precede"]
                                        building_state[1] = True
                                        if faction == self.player_faction:
                                            self.event_notification_ui.add_new_event((
                                                "event_raze", building_text +
                                                self.grab_text(("ui", "info_text_raze_done")),
                                                turn_text, self.region_list[region]["Settlement POS"]))
                                    else:  # finish construction
                                        if faction == self.player_faction:
                                            self.event_notification_ui.add_new_event((
                                                "event_build", building_text +
                                                self.grab_text(("ui", "info_text_construction_done")),
                                                turn_text, self.region_list[region]["Settlement POS"]))

                    if building_state_change:
                        # building state change (like progress value change) may not affect entire region stat
                        if (faction == self.player_faction and region == self.region_management_ui.player_selected_region):
                            self.region_management_ui.change_selected_region(region)

                    if region_state_change:
                        self.cal_region_income_recruit(faction, region)
                        if faction == self.player_faction:
                            settlement_object = self.settlement_object_list[region]
                            for index, building_state in building_state_change:
                                settlement_object.change_building_state(index, building_state)
                            # update settlement object in map
                            settlement_object.change_state(settlement_object.building_state)

                            # update building managmenet ui to reflect new state
                            if (self.building_management_ui in self.outer_ui_updater and
                                    region == self.building_management_ui.player_selected_region):
                                self.building_management_ui.change_selected_building(
                                    self.building_management_ui.selected_building_index)

            # if faction == self.player_faction and self.player_grand_character_selector in self.outer_ui_updater:
            #     self.player_grand_character_selector
            #     self.player_grand_preset_army_setup

            self.cal_faction_income(faction)

        for battle in current_campaign_state["battle"]["auto"]:  # process all auto battle
            pass

    if self.player_faction:
        self.player_faction_culture_list_ui.culture_change()
