from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from math import ceil

from engine.constants import Turn_To_Phase

time_per_phase = 1 / Turn_To_Phase  # 1 cosmic time is 1 turn


def change_phase(self: Grand, phase_change: bool = True):
    current_campaign_state = self.current_campaign_state
    region_campaign_state = current_campaign_state["region"]

    if phase_change:
        current_campaign_state["cosmic_time"] += time_per_phase
        if current_campaign_state["cosmic_time"] != 3141.6:  # reset cosmos time
            self.cosmic_ui.phase_change()
        else:
            current_campaign_state["cosmic_time"] = 0
            self.cosmic_ui.reset(0)
        current_campaign_state["cosmic_event"] = {key: value - 1 for key, value in
                                                  current_campaign_state["cosmic_event"].items() if value > 1}

    # process respective faction ai assigned to the phase

    # process faction state
    building_path_for_requirement_check = self.building_path_for_requirement_check
    for faction, faction_state in current_campaign_state["faction"].items():
        if phase_change:
            for army in faction_state["army"]:
                army.change_phase()

        if faction != "free":
            for region in faction_state["region"]:
                building_state_change = []
                region_building_state = region_campaign_state[region]["building"]
                if phase_change:
                    region_state_change = False
                    for index, building_state in enumerate(region_building_state):
                        # update building state process involving razing/pillaging/construction/repair
                        building = building_state[0]
                        if building_state[2]:  # ongoing razing/pillaging/construction/repair
                            building_state[2] -= 1
                            building_state_change.append((index, building_state))
                            if not building_state[2]:  # finish progress
                                region_state_change = True
                                if not building_state[1]:
                                    building_state[1] = True
                                else:
                                    turn_text = str(current_campaign_state["turn"]) + "." + str(
                                        current_campaign_state["phase"])
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
                                        # if self.building_list[building]["Technology"]:

                                    else:  # finish construction
                                        if faction == self.player_faction:
                                            self.event_notification_ui.add_new_event((
                                                "event_build", building_text +
                                                self.grab_text(("ui", "info_text_construction_done")),
                                                turn_text, self.region_list[region]["Settlement POS"]))
                else:
                    # recal for region state anyway if phase change is false
                    region_state_change = True

                require_active_change_check = True
                while require_active_change_check:
                    require_active_change_check = False
                    for building_state in region_building_state:
                        # now check for requirement satisfaction
                        building = building_state[0]
                        if self.building_list[building]["Requirement"]:  # has requirement
                            satisfy_check = [True if any([building_path in region_building_state for
                                                          building_path in
                                                          building_path_for_requirement_check[require_building]]) else
                                             False for require_building in self.building_list[building]["Requirement"]]
                            if False in satisfy_check:
                                new_active_state = False
                            else:
                                new_active_state = True
                        else:
                            new_active_state = True

                        if new_active_state != building_state[3]:
                            building_state[3] = new_active_state
                            region_state_change = True

                if building_state_change:
                    # building state change (like progress value change) may not affect entire region stat
                    if (faction == self.player_faction and
                            region == self.region_management_ui.player_selected_region):
                        self.region_management_ui.change_selected_region(region)

                if region_state_change:
                    self.cal_region_income_recruit(faction, region)
                    if faction == self.player_faction:
                        settlement_object = self.settlement_object_list[region]
                        for index, building_state in building_state_change:
                            settlement_object.change_building_state(index, building_state)
                        # update settlement object in map
                        settlement_object.change_state(settlement_object.building_state)

                        # update building management ui to reflect new state
                        if (self.building_management_ui in self.outer_ui_updater and
                                region == self.building_management_ui.player_selected_region):
                            self.building_management_ui.change_selected_building(
                                self.building_management_ui.selected_building_index)

            # if faction == self.player_faction and self.player_grand_character_selector in self.outer_ui_updater:
            #     self.player_grand_character_selector
            #     self.player_grand_preset_army_setup

            self.cal_faction_income_recruit(faction)

        for battle in current_campaign_state["battle"]["auto"]:  # process all auto battle
            pass

    if self.player_faction:
        self.faction_culture_list_ui.culture_change()
        if self.culture_management_ui in self.outer_ui_updater:
            # reset culture management ui every phase if open
            self.culture_management_ui.reset()
        elif self.diplomacy_management_ui in self.outer_ui_updater:
            self.diplomacy_management_ui.reset()