from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from math import ceil

from engine.constants import Culture_Policy_Integration
from engine.utils.text_making import add_plus_to_number


def cal_faction_income_recruit(self: Grand, faction_id: str):
    current_campaign_state = self.current_campaign_state
    campaign_faction_state = current_campaign_state["faction"][faction_id]
    faction_data = self.faction_list[faction_id]
    total_gold_income = faction_data["Gold Income"]
    total_supply_income = faction_data["Supply Income"]
    total_happiness = 0
    region_control_state = campaign_faction_state["region"]
    region_campaign_state = current_campaign_state["region"]

    list_of_happiness_effect = {"region_income": [], "influence_effect": [], "coexist_effect": [], "event_effect": [],
                                "famine_effect": [], "bankrupt_effect": []}
    list_of_gold_income_effect = {"start_income": total_gold_income, "region_income": [], "army_upkeep": [],
                                  "event_effect": []}
    list_of_supply_income_effect = {"start_income": total_supply_income, "region_income": [], "event_effect": []}

    for event in campaign_faction_state["event"]:
        event_data = event[0]
        event_type = "event_effect"
        if event_data["ID"] == "bankrupt":
            event_type = "bankrupt_effect"
        elif event_data["ID"] == "famine":
            event_type = "famine_effect"
        for effect, effect_value in event_data.items():
            if effect == "happiness":
                total_happiness += effect_value
                list_of_happiness_effect[event_type].append((event_data["ID"], effect_value))
            elif effect == "gold":
                total_gold_income += effect_value
                list_of_gold_income_effect[event_type].append((event_data["ID"], effect_value))
            elif effect == "supply":
                total_supply_income += effect_value
                list_of_supply_income_effect[event_type].append((event_data["ID"], effect_value))

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
    faction_culture_state = current_campaign_state["faction"][faction_id]["culture"]
    for culture, culture_state in faction_culture_state.items():
        culture_influence = culture_state["influence"]
        culture_integration = culture_state["integration"]
        cap_integration = Culture_Policy_Integration[culture_state["policy"]]
        representation_requirement = culture_state["integration"] / 10
        culture_state["penalty"] = 0
        if representation_requirement > culture_influence:  # incur happiness penalty due lack of representation
            # happiness penalty grow along with faction region number
            happiness_penalty = ceil((culture_influence - representation_requirement) * 10 * (
                (len(region_control_state) + 1)))
            culture_state["penalty"] += happiness_penalty
            influence_happiness_penalty += happiness_penalty
            list_of_happiness_effect["influence_effect"].append((culture_state, happiness_penalty))

        if culture_influence > cap_integration:
            # high influence culture that exceed integration cap of policy also cause happiness penalty
            # linear -1 happiness per 1% of influence that exceed integration cap,
            # e.g., culture with 50% influence but 30% integration cap incur -20 happiness
            happiness_penalty = ceil((cap_integration - culture_influence) * 100)

            culture_state["penalty"] += happiness_penalty
            influence_happiness_penalty += happiness_penalty
            list_of_happiness_effect["influence_effect"].append((culture_state, happiness_penalty))

        if culture_integration:
            # culture is integrate into faction in any amount begin check for coexistence mod
            coexist_mod = self.culture_list[culture]["Coexistence Modifier"]
            if coexist_mod:
                for culture_modifier, value in coexist_mod.items():
                    if (culture_modifier in faction_culture_state and
                            faction_culture_state[culture_modifier]["integration"]):
                        # add coexistence modifier for other culture with any integration
                        new_value = ceil(value * culture_integration)
                        if new_value != 0:
                            total_happiness += new_value
                            list_of_happiness_effect["coexist_effect"].append((culture_modifier, new_value))

    for region in region_control_state:  # get happiness first
        region_happiness = region_campaign_state[region]["income"]["happiness"]
        total_happiness += region_happiness
        list_of_happiness_effect["region_income"].append((region, region_happiness))

    total_happiness += influence_happiness_penalty
    happiness_effect_modifier = ceil(total_happiness + influence_happiness_penalty)
    if happiness_effect_modifier < -50:  # less than -50 incur no additional penalty
        happiness_effect_modifier = -50
    if happiness_effect_modifier > 50:
        happiness_effect_modifier = 50

    happy_mod_text = add_plus_to_number(happiness_effect_modifier) + "%"
    happiness_effect_modifier = (happiness_effect_modifier / 100) + 1

    campaign_faction_state["recruit"] = {"leader": [], "troop": [], "air": []}
    for region in region_control_state:
        region_income_state = region_campaign_state[region]["income"]
        region_recruit_state = region_campaign_state[region]["recruit"]
        for key, value in region_recruit_state.items():  # add recruit from each region
            campaign_faction_state["recruit"][key] += [item for item in value if
                                                       item not in campaign_faction_state["recruit"][key]]
        region_gold_income = ceil(region_income_state["gold_income"] * happiness_effect_modifier)
        region_supply_income = ceil(region_income_state["supply_income"] * happiness_effect_modifier)
        total_gold_income += region_gold_income
        total_supply_income += region_supply_income
        list_of_gold_income_effect["region_income"].append((region, region_gold_income))
        list_of_supply_income_effect["region_income"].append((region, region_supply_income))

    list_of_gold_income_effect["happiness_modifier"] = happy_mod_text
    list_of_supply_income_effect["happiness_modifier"] = happy_mod_text

    for army in campaign_faction_state["army"]:
        total_gold_income += army.upkeep
        list_of_gold_income_effect["army_upkeep"].append((army.game_id, army.upkeep))

    campaign_faction_state["gold_income"] = total_gold_income
    campaign_faction_state["supply_income"] = total_supply_income
    campaign_faction_state["happiness"] = total_happiness

    campaign_faction_state["happiness_effect"] = list_of_happiness_effect
    campaign_faction_state["gold_effect"] = list_of_gold_income_effect
    campaign_faction_state["supply_effect"] = list_of_supply_income_effect
