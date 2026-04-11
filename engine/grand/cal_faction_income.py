def cal_faction_income(self, faction):
    faction_data = self.current_campaign_state["faction"][faction]
    total_gold_income = 0
    total_supply_income = 0
    total_happiness = 0
    if faction in faction_data["region"]["control"]:
        for region in faction_data["region"]["control"][faction]:
            region_state_data = self.grand.current_campaign_state["region"][region]
            total_gold_income += region_state_data["gold_income"]
            total_supply_income += region_state_data["supply_income"]
            total_happiness += region_state_data["happiness"]

    for army in faction_data["army"]:
        total_gold_income -= army.upkeep

    faction_data["gold_income"] = total_gold_income
    faction_data["supply_income"] = total_supply_income
    faction_data["happiness"] = total_happiness

