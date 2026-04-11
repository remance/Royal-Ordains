from math import ceil


def cancel_building_construction_or_repair(self, faction, region, slot, building):
    building_state = self.current_campaign_state["region"][region]["building"][slot]
    building_state[2] = 0
    if not building_state[1]:  # cancel repair
        self.current_campaign_state["faction"][faction]["gold"] += ceil(self.building_list[building]["Cost"] / 2)
    else:  # cancel construct new building
        building_state[0] = self.building_list[building_state[0]]["Precede"]  # return to precede
        self.current_campaign_state["faction"][faction]["gold"] += self.building_list[building]["Cost"]

    if faction == self.player_faction:
        # self.region_dots
        if region == self.region_management_ui.player_selected_region:
            self.region_management_ui.change_selected_region(region)

    self.settlement_object_list[region].change_building_state(slot, building_state, also_change_state=True)
