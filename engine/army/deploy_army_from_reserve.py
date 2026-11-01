def deploy_army_from_reserve(self, region, max_supply):
    """deploy army from reserve"""
    grand = self.grand
    self.base_pos = self.region_list[region]["Settlement POS"]
    self.max_supply = max_supply

    self.reset_stat()
    grand.current_campaign_state[self.faction]["army"].append(self)
    grand.current_campaign_state[self.faction]["reserve"].remove(self)
