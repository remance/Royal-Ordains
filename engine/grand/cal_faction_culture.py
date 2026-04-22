"""Culture integration level affect army and building effectiveness,
culture gain influence from building stat based on policy level

policy affect influence > influence affect integration rate > integration affect unit cost/upkeep and building resource generation

player must choose policy level when gain new region with new culture

culture with higher influence than integration cap will reduce happiness 100% integration require for 10% influence  

When happiness is low, regions with high influence and low integration are more likely to rebel 

Culture influence in faction then affect unit upkeep and purchase cost, the lower the influence increase value upto triple the original value 
if culture is entirely removed from all regions in the game then it is 
considered extinct and any units are automatically removed from destroyed army
"""


def cal_faction_culture(self, faction):
    """Calculate each culture influence in the faction based on weight and integration percentage level"""
    culture_weight = {}
    faction_campaign_state = self.current_campaign_state["faction"][faction]
    for region in faction_campaign_state["region"]:
        for building in self.current_campaign_state["region"]["buildings"][region]:
            if building and building[1]:  # building is in active state and not destroyed state
                building_id = building[0]
                culture = self.building_list[building_id]["Culture"]
                if culture != "all":  # building belong to a specific culture
                    if culture not in culture_weight:
                        culture_weight[culture] = 0
                    culture_integration = faction_campaign_state["culture"][culture]["integration"]
                    if culture_integration > 0:
                        culture_weight[culture] += self.building_list[building_id]["Influence"] * culture_integration

    total_diversity_weight = sum([weight for weight in culture_weight.values()])

    # if any([key for key in culture_weight not in self.current_campaign_state[faction]["culture"]]):
    # culture is removed from faction because it no longer exist in the game

    for culture in faction_campaign_state["culture"].values():
        culture["influence"] = culture["weight"] / total_diversity_weight
