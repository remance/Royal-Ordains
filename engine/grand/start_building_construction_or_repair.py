from math import ceil


def start_building_construction_or_repair(self, faction, region, slot, building):
    building_state = self.current_campaign_state["region"]["building"][region][slot]
    if not building_state[1]:  # repair
        building_state[2] = ceil(self.building_list[building]["Build Time"] / 2)
        self.current_campaign_state["faction"][faction]["gold"] -= ceil(self.building_list[building]["Cost"] / 2)
    else:  # construct new building
        building_state[2] = self.building_list[building]["Build Time"]
        self.current_campaign_state["faction"][faction]["gold"] -= self.building_list[building]["Cost"]

    if faction == self.player_faction and region == self.region_management_ui.player_selected_region:
        self.region_management_ui.change_selected_region(region)
