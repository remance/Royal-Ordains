"""Culture integration level affect army and building effectiveness,
culture gain influence from building stat based on policy level

policy affect influence -> influence affect integration rate -> integration affect unit
cost/upkeep and building resource generation

culture with higher influence than integration cap will reduce happiness 100% integration require for 10% influence  

When happiness is low, regions with high influence and low integration are more likely to rebel 

Culture influence in faction then affect unit upkeep and purchase cost, the lower the influence increase value upto
triple the original value if culture is entirely removed from all regions in the game then it is considered extinct
and any units are automatically removed from destroyed army"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from engine.constants import Culture_Default_New


def cal_faction_culture(self: Grand, faction_id: str):
    """Calculate each culture influence in the faction based on weight and integration percentage level"""
    culture_weight = {}
    faction_campaign_state = self.current_campaign_state["faction"][faction_id]
    faction_culture_campaign_state = faction_campaign_state["culture"]
    region_campaign_state = self.current_campaign_state["region"]
    for region in faction_campaign_state["region"]:
        region_culture_campaign_state = region_campaign_state[region]["culture"]
        region_culture_campaign_state.clear()
        for building_state in region_campaign_state[region]["building"]:
            if building_state and building_state[1] is True and not building_state[2]:
                # building is in active state and not destroyed/constructing state
                building_id = building_state[0]
                culture = self.building_list[building_id]["Culture"]
                if culture != "all":  # building belong to a specific culture
                    if culture not in faction_culture_campaign_state:
                        # new culture, add to faction culture list with default policy
                        faction_culture_campaign_state[culture] = {
                            "policy": Culture_Default_New, "influence": 0, "weight": 0, "integration": 0, "penalty": 0}

                    if culture not in culture_weight:
                        culture_weight[culture] = 0
                    if culture not in region_culture_campaign_state:
                        region_culture_campaign_state[culture] = 0

                    culture_integration = faction_culture_campaign_state[culture]["integration"]
                    if culture_integration > 0:
                        building_culture = self.building_list[building_id]["Influence"] * culture_integration
                        culture_weight[culture] += building_culture
                        region_culture_campaign_state[culture] += building_culture

    # culture weight cannot be less than 0
    total_diversity_weight = sum([weight for weight in culture_weight.values() if weight > 0])

    # if any([key for key in culture_weight not in self.current_campaign_state[faction]["culture"]]):
    # culture is removed from faction because it no longer exist in the game
    faction_campaign_state["total_culture_weight"] = total_diversity_weight

    for culture, culture_value in faction_culture_campaign_state.items():

        culture_value["weight"] = 0
        if culture in culture_weight and culture_weight[culture] > 0:
            culture_value["weight"] = culture_weight[culture]

        if total_diversity_weight:
            culture_value["influence"] = culture_value["weight"] / total_diversity_weight
        else:
            culture_value["influence"] = 0
