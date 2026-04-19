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
    for region in self.current_campaign_state["region"]["control"][faction]:
        for building in self.current_campaign_state["region"][region]["buildings"]:
            culture = self.building_list[building]["Culture"]
            if culture not in culture_weight and culture != "all":
                culture_weight[culture] = 0
            culture_integration = self.current_campaign_state[faction]["culture"][culture][1]
            if culture_integration > 0:
                culture_weight[culture] += self.building_list[building]["Influence"] * culture_integration

    total_diversity_weight = sum([weight for weight in culture_weight.values()])

    # if any([key for key in culture_weight not in self.current_campaign_state[faction]["culture"]]):
    # culture is removed from faction because it no longer exist in the game

    for culture in self.current_campaign_state[faction]["culture"].values():
        culture["influence"] = culture["weight"] * culture["integration"] / total_diversity_weight


def change_faction_culture_state(self):
    pass
