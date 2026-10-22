from engine.constants import Culture_Policy_Integration
from engine.utils.text_making import convert_modifier_number_to_percent_text, add_plus_to_number


def cal_faction_income_recruit(self, faction):
    current_campaign_state = self.current_campaign_state
    faction_data = current_campaign_state["faction"][faction]
    total_gold_income = self.faction_list[faction]["Gold Income"]
    total_supply_income = self.faction_list[faction]["Supply Income"]
    total_happiness = 0
    region_control_state = faction_data["region"]
    region_campaign_state = current_campaign_state["region"]

    list_of_happiness_effect = {"region_income": [], "influence_effect": [], "coexist_effect": [], "event_effect": []}
    list_of_gold_income_effect = {"start_income": total_gold_income, "region_income": [], "army_upkeep": [],
                                  "event_effect": []}
    list_of_supply_income_effect = {"start_income": total_supply_income, "region_income": [], "event_effect": []}

    for event in faction_data["event"]:  # add happiness from event first
        for effect, effect_value in self.map_data.event_list[event]["Effect"]:
            if effect == "happiness":
                total_happiness += effect_value
                list_of_happiness_effect["event_effect"].append((event, effect_value))
            elif effect == "gold":
                total_gold_income += effect_value
                list_of_gold_income_effect["event_effect"].append((event, effect_value))
            elif effect == "supply":
                total_supply_income += effect_value
                list_of_supply_income_effect["event_effect"].append((event, effect_value))

    for event in current_campaign_state["cosmic_event"]:
        for effect, effect_value in self.cosmic_event_list[event]["Effect"].items():
            if effect == "happiness":
                total_happiness += effect_value
                list_of_happiness_effect["event_effect"].append((event, effect_value))
            elif effect == "gold":
                total_gold_income += effect_value
                list_of_gold_income_effect["event_effect"].append((event, effect_value))
            elif effect == "supply":
                total_supply_income += effect_value
                list_of_supply_income_effect["event_effect"].append((event, effect_value))

    influence_happiness_penalty = 0
    faction_culture_state = current_campaign_state["faction"][faction]["culture"]
    for culture, culture_state in faction_culture_state.items():
        culture_influence = culture_state["influence"]
        cap_integration = Culture_Policy_Integration[culture_state["policy"]]
        representation_requirement = culture_state["integration"] / 10
        culture_state["penalty"] = 0
        if representation_requirement > culture_influence:  # incur happiness penalty due lack of representation
            # happiness penalty grow along with faction region number
            happiness_penalty = int((representation_requirement - culture_influence) * 10 * (
                (len(region_control_state) + 1)))
            culture_state["penalty"] += happiness_penalty
            influence_happiness_penalty += happiness_penalty
            list_of_happiness_effect["influence_effect"].append((culture_state, happiness_penalty))

        if culture_influence > cap_integration:
            # high influence culture that exceed integration cap of policy also cause happiness penalty
            # linear -1 happiness per 1% of influence that exceed integration cap,
            # e.g., culture with 50% influence but 30% integration cap incur -20 happiness
            happiness_penalty = int((cap_integration - culture_influence) * 100)
            culture_state["penalty"] += happiness_penalty
            influence_happiness_penalty += happiness_penalty
            list_of_happiness_effect["influence_effect"].append((culture_state, happiness_penalty))

        coexist_mod = self.culture_list[culture]["Coexistence Modifier"]
        if coexist_mod:
            for culture_modifier, value in coexist_mod.items():
                if culture_modifier in faction_culture_state:
                    total_happiness += value
                    list_of_happiness_effect["coexist_effect"].append((culture_modifier, value))

    for region in region_control_state:  # get happiness first
        region_happiness = region_campaign_state[region]["income"]["happiness"]
        total_happiness += region_happiness
        list_of_happiness_effect["region_income"].append((region, region_happiness))

    total_happiness += influence_happiness_penalty
    happiness_effect_modifier = int(total_happiness + influence_happiness_penalty)
    if happiness_effect_modifier < -50:  # less than -50 incur no additional penalty
        happiness_effect_modifier = -50
    if happiness_effect_modifier > 50:
        happiness_effect_modifier = 50

    happy_mod_text = add_plus_to_number(happiness_effect_modifier) + "%"
    happiness_effect_modifier = (happiness_effect_modifier / 100) + 1

    faction_data["recruit"] = {"leader": [], "troop": [], "air": []}
    for region in region_control_state:
        region_income_state = region_campaign_state[region]["income"]
        region_recruit_state = region_campaign_state[region]["recruit"]
        for key, value in region_recruit_state.items():  # add recruit from each region
            faction_data["recruit"][key] += [item for item in value if value not in faction_data["recruit"][key]]
        region_gold_income = region_income_state["gold_income"] * happiness_effect_modifier
        region_supply_income = region_income_state["supply_income"] * happiness_effect_modifier
        total_gold_income += region_gold_income
        total_supply_income += region_supply_income
        list_of_gold_income_effect["region_income"].append((region, region_gold_income))
        list_of_supply_income_effect["region_income"].append((region, region_supply_income))

    list_of_gold_income_effect["happiness_modifier"] = happy_mod_text
    list_of_supply_income_effect["happiness_modifier"] = happy_mod_text

    for army in faction_data["army"]:
        total_gold_income += army.upkeep
        list_of_gold_income_effect["army_upkeep"].append((army.game_id, army.upkeep))

    faction_data["gold_income"] = total_gold_income
    faction_data["supply_income"] = total_supply_income
    faction_data["happiness"] = total_happiness

    faction_data["happiness_effect"] = list_of_happiness_effect
    faction_data["gold_effect"] = list_of_gold_income_effect
    faction_data["supply_effect"] = list_of_supply_income_effect
