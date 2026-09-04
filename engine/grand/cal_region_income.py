def cal_region_income(self, region):
    """Calculate region income from each active building based on faction culture influence"""
    total_gold_income = 0
    total_supply_income = 0
    total_happiness = 0
    income_mod = {"gold": 1.0, "supply": 1.0, "happiness": 1.0}
    campaign_region_state = self.current_campaign_state["region"]
    owner = campaign_region_state["control"][region]
    faction_culture_state = self.current_campaign_state["faction"][owner]["culture"]
    for building in campaign_region_state["buildings"][region]:
        if building and building[1]:  # only count active building (not damaged)
            building_id = building[0]
            building_stat = self.building_list[building_id]
            integration_state = 1
            if building_stat["Culture"] != "all":
                integration_state = faction_culture_state[building_stat["Culture"]]["integration"]
            if integration_state > 0:
                # integration more than 0 will allow building to give resource, can be negative
                total_gold_income += building_stat["Gold Income"] * integration_state
                total_supply_income += building_stat["Supply Income"] * integration_state
                total_happiness += building_stat["Happiness"] * integration_state

            if building_stat["Income Boost"]:
                for key, value in building_stat["Income Boost"].items():
                    income_mod[key] += value
                    if income_mod[key] < 0:
                        income_mod[key] = 0

    region_income_state = campaign_region_state["income"][region]

    region_income_state["gold_income"] = total_gold_income * income_mod["gold"]
    region_income_state["supply_income"] = total_supply_income * income_mod["supply"]
    region_income_state["happiness"] = total_happiness * income_mod["happiness"]
