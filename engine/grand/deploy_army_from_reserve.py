def deploy_army_from_reserve(self, reserve_army_data, region):
    """deploy army from reserve"""
    self.base_pos = self.region_list[region]["Settlement POS"]

    self.create_new_army(self.current_campaign_state["faction"][reserve_army_data["faction"]], reserve_army_data)
    army = self.current_campaign_state["faction"][reserve_army_data["faction"]][-1]
    self.current_campaign_state[army.faction]["reserved"].remove(reserve_army_data)
