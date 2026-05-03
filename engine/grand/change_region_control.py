def change_region_control(self, region, new_faction):
    old_faction = self.current_campaign_state["region"]["control"][region]

    self.current_campaign_state["faction"][old_faction]["region"].remove(region)
    self.current_campaign_state["faction"][new_faction]["region"].append(region)

    self.current_campaign_state["region"]["control"][region] = new_faction

    # if "culture" not in :
    # if new_faction == self.player_faction:  # add event
