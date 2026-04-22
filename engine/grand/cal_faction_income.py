from engine.constants import Culture_Policy_Integration


def cal_faction_income(self, faction):
    faction_data = self.current_campaign_state["faction"][faction]
    total_gold_income = self.faction_list[faction]["Gold Income"]
    total_supply_income = self.faction_list[faction]["Supply Income"]
    total_happiness = 0
    region_control_state = faction_data["region"]
    region_income_state = self.current_campaign_state["region"]["income"]

    list_of_happiness_effect = {"region_income": [], "influence_effect": [], "coexist_effect": [], "event_effect": []}
    list_of_gold_income_effect = {"start_income": total_gold_income, "region_income": [], "army_upkeep": []}
    list_of_supply_income_effect = {"start_income": total_supply_income, "region_income": []}

    for event in faction_data["event"]:  # add happiness from event first
        for effect, effect_value in self.map_data.event_list[event]["Effect"]:
            if effect == "happiness":
                total_happiness += effect_value
                list_of_happiness_effect["event_effect"].append((event, effect_value))

    influence_happiness_modifier = 0
    faction_culture_state = self.current_campaign_state["faction"][faction]["culture"]
    for culture, culture_state in faction_culture_state.items():
        culture_influence = culture_state["influence"]
        cap_integration = Culture_Policy_Integration[culture_state["policy"]]
        representation_requirement = culture_state["integration"] / 10
        if representation_requirement > culture_influence:  # incur happiness penalty due lack of representation
            # happiness penalty grow along with faction region number
            happiness_penalty = (representation_requirement - culture_influence) * (
                    (len(faction_data["region"]) + 1) / 10)

            influence_happiness_modifier -= happiness_penalty
            list_of_happiness_effect["influence_effect"].append((culture_state, happiness_penalty))
        if culture_influence > cap_integration:
            # high influence culture with that exceed integration cap of policy also cause happiness penalty
            # linear -1 happiness per 1% of influence that exceed integration cap,
            # e.g., culture with 50% influence but 30% integration cap incur -20 happiness
            happiness_penalty = (culture_influence - cap_integration) * 100
            influence_happiness_modifier -= happiness_penalty
            list_of_happiness_effect["influence_effect"].append((culture_state, happiness_penalty))

        coexist_mod = self.culture_list[culture]["Coexistence Modifier"]
        if coexist_mod:
            for culture_modifier, value in coexist_mod.items():
                if culture_modifier in faction_culture_state:
                    total_happiness += value
                    list_of_happiness_effect["coexist_effect"].append((culture_modifier, value))

    for region in region_control_state:  # get happiness first
        region_happiness = region_income_state[region]["happiness"]
        total_happiness += region_happiness
        list_of_happiness_effect["region_income"].append((region, region_happiness))

    happiness_modifier = total_happiness - int(influence_happiness_modifier)
    if happiness_modifier < -30:  # less than -30 incur no additional penalty
        happiness_modifier = -30

    happiness_modifier = (happiness_modifier / 100) + 1

    for region in region_control_state:
        region_income_state_data = self.current_campaign_state["region"]["income"][region]
        region_gold_income = region_income_state_data["gold_income"] * happiness_modifier
        region_supply_income = region_income_state_data["supply_income"] * happiness_modifier
        total_gold_income += region_gold_income
        total_supply_income += region_supply_income
        list_of_gold_income_effect["region_income"].append((region, region_gold_income))
        list_of_supply_income_effect["region_income"].append((region, region_supply_income))

    for army in faction_data["army"]:
        total_gold_income += army.upkeep
        list_of_gold_income_effect["army_upkeep"].append((army.game_id, army.upkeep))

    faction_data["gold_income"] = total_gold_income
    faction_data["supply_income"] = total_supply_income
    faction_data["happiness"] = total_happiness

    faction_data["happiness_effect"] = list_of_happiness_effect
    faction_data["gold_effect"] = list_of_gold_income_effect
    faction_data["supply_effect"] = list_of_supply_income_effect
