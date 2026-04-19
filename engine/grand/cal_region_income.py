def cal_region_income(self, region):
    """Calculate region income from each active building based on faction culture influence"""
    total_gold_income = 0
    total_supply_income = 0
    total_happiness = 0
    campaign_region_state = self.current_campaign_state["region"]
    owner = campaign_region_state["control"]["owner"]
    faction_culture_state = self.current_campaign_state["faction"][owner]["culture"]
    for building in campaign_region_state["buildings"][region]:
        if building[1] is True:  # only count active building (not damaged)
            building_id = building[0]
            building_stat = self.building_list[building_id]
            integration_state = faction_culture_state[building_stat["Culture"]][1]
            if integration_state > 0:
                # integration more than 0 will allow building to give resource
                total_gold_income += building_stat["Gold Income"] * integration_state
                total_supply_income += building_stat["Supply Income"] * integration_state
                total_happiness += campaign_region_state["Happiness"] * integration_state

    region_income_state = campaign_region_state["income"][region]

    region_income_state["gold_income"] = total_gold_income
    region_income_state["supply_income"] = total_supply_income
    region_income_state["happiness"] = total_happiness
