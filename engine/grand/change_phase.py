from engine.constants import Turn_To_Phase

time_per_phase = 1 / Turn_To_Phase  # 1 cosmic time is 1 turn


def change_phase(self, phase_change=True):
    if phase_change:
        current_campaign_state = self.current_campaign_state
        self.cosmic_ui.phase_change()
        current_campaign_state["cosmic_time"] += time_per_phase

        # process respective faction ai assigned to the phase
        for faction, faction_state in current_campaign_state["faction"].items():
            for army in faction_state["army"]:
                army.change_phase()

                region_state_change = False
                for region in faction_state["region"]:
                    for building_state in current_campaign_state["region"]["building"][region]:
                        building = building_state[0]
                        if building_state[2]:  # ongoing razing/pillaging/construction/repair
                            building_state[2] -= 1
                            region_state_change = True
                            if not building_state[2]:  # finish progress
                                if not building_state[1]:
                                    building_state[1] = True
                                else:
                                    turn_text = str(current_campaign_state["turn"]) + "." + str(current_campaign_state["phase"])
                                    building_text = (self.grab_text(("region", region, "Name")) + "/ " +
                                                     self.grab_text(("building", building, "Name")))
                                    if building_state[1] == "pillage":
                                        building_state[1] = False
                                        # receive half building cost gold
                                        faction_state["gold"] += self.building_list[building]["Cost"]
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

                    if region_state_change:
                        self.cal_region_income(region)
                        if faction == self.player_faction and region == self.region_management_ui.player_selected_region:
                            self.region_management_ui.change_selected_region(region)

        for battle in current_campaign_state["battle"]["auto"]:  # process all auto battle
            pass

    if self.player_faction:
        self.player_faction_culture_list_ui.culture_change()
