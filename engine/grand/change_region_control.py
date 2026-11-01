def change_region_control(self, region, new_faction):
    current_campaign_state = self.current_campaign_state
    campaign_region_state = current_campaign_state["region"]

    new_faction_owner_campaign_state = current_campaign_state["faction"][new_faction]

    current_campaign_state["faction"][campaign_region_state[region]["control"]]["region"].remove(region)
    new_faction_owner_campaign_state["region"].append(region)

    campaign_region_state[region]["control"] = new_faction
    for key, value in self.settlement_dots.items():
        if value == region:
            self.dots_settlement_info_banners[key].reset(new_faction)
            break

    # player faction get new culture popup mandatory culture policy input
    if new_faction == self.player_faction and "culture" not in new_faction_owner_campaign_state:
        # if new_faction == self.player_faction:
        pass

    if region == self.region_management_ui.change_selected_region:
        # collapse region management ui if player lose control while opening it
        self.region_management_ui.change_selected_region(None)
    self.mini_map.change_grand_faction(campaign_region_state)
