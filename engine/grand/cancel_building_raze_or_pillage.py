def cancel_building_raze_or_pillage(self, faction, region, slot):
    building_state = self.current_campaign_state["region"][region]["building"][slot]
    building_state[1] = True
    building_state[2] = 0

    if faction == self.player_faction and region == self.region_management_ui.player_selected_region:
        self.region_management_ui.change_selected_region(region)

    self.settlement_object_list[region].change_building_state(slot, building_state, also_change_state=True)
