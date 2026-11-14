def deploy_army_from_reserve(self, region, max_supply):
    """deploy army from reserve"""
    grand = self.grand
    self.base_pos = grand.region_list[region]["Settlement POS"]
    self.current_region = region
    self.max_supply = max_supply

    self.reset_stat()
    faction_state = grand.current_campaign_state["faction"][self.faction]
    faction_state["reserve"].remove(self)
    faction_state["gold"] -= self.cost
    grand.create_new_army(faction_state, self.to_dict, no_enemy_check=False)
