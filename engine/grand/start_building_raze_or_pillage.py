from math import ceil


def start_building_raze_or_pillage(self, faction, region, slot, building, pillage=False):
    building_state = self.current_campaign_state["region"][region]["building"][slot]
    if pillage:  # pillage, take half time
        building_state[1] = "pillage"
        building_state[2] = ceil(self.building_list[building]["Real Build Time"] / 2)
    else:  # raze, take a quater time
        building_state[1] = "raze"
        building_state[2] = ceil(self.building_list[building]["Real Build Time"] / 4)

    if faction == self.player_faction:
        self.settlement_object_list[region].change_building_state(slot, building_state, also_change_state=True)

        if region == self.region_management_ui.player_selected_region:
            self.region_management_ui.change_selected_region(region)
