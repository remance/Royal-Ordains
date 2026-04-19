def cal_faction_income(self, faction):
    faction_data = self.current_campaign_state["faction"][faction]
    total_gold_income = 0
    total_supply_income = 0
    total_happiness = 0
    region_control_state = faction_data["region"]["control"]
    if faction in region_control_state:
        for region in region_control_state[faction]:  # get happiness first
            total_happiness += self.current_campaign_state["region"]["income"][region]["happiness"]

        influence_happiness_modifier = 0
        for culture in self.current_campaign_state[faction]["culture"].values():
            representation_requirement = culture["integration"] / 10
            if representation_requirement > culture["influence"]:  # incur happiness penalty due lack of representation
                # happiness penalty grow along with faction region number
                influence_happiness_modifier -= (representation_requirement - culture["influence"]) * (
                        (len(region_control_state[faction]) + 1) / 10)

        happiness_modifier = total_happiness - int(influence_happiness_modifier)
        if happiness_modifier < -20:  # less than -20 incur no additional penalty
            happiness_modifier = -20

        happiness_modifier = (happiness_modifier / 100) + 1

        for region in faction_data["region"]["control"][faction]:
            region_income_state_data = self.current_campaign_state["region"]["income"][region]
            total_gold_income += region_income_state_data["gold_income"] * happiness_modifier
            total_supply_income += region_income_state_data["supply_income"] * happiness_modifier

    for army in faction_data["army"]:
        total_gold_income -= army.upkeep

    faction_data["gold_income"] = total_gold_income
    faction_data["supply_income"] = total_supply_income
    faction_data["happiness"] = total_happiness
