from math import ceil


def start_building_construction_or_repair(self, faction, region, slot, building):
    building_state = self.current_campaign_state["region"]["building"][region][slot]
    building_state[2] = 0
    if not building_state[1]:  # cancel repair
        self.current_campaign_state["faction"][faction]["gold"] += ceil(self.building_list[building]["Cost"] / 2)
    else:  # cancel construct new building
        building_state[0] = self.building_list[building_state[0]]["Precede"]  # return to precede
        self.current_campaign_state["faction"][faction]["gold"] += self.building_list[building]["Cost"]

    if faction == self.player_faction and region == self.region_management_ui.player_selected_region:
        self.region_management_ui.change_selected_region(region)
