from math import ceil


def start_building_raze_or_pillage(self, faction, region, slot, building, pillage=False):
    building_state = self.current_campaign_state["region"]["building"][region][slot]
    if pillage:  # pillage, take half time
        building_state[1] = "pillage"
        building_state[2] = ceil(self.building_list[building]["Build Time"] / 2)
    else:  # raze, take a quater time
        building_state[2] = ceil(self.building_list[building]["Build Time"] / 4)

    if faction == self.player_faction and region == self.region_management_ui.player_selected_region:
        self.region_management_ui.change_selected_region(region)
