from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand


def cal_region_income_recruit(self: Grand, faction_id: str, region_id: str):
    """Calculate region income from each active building based on faction culture influence"""
    total_gold_income = 0
    total_supply_income = 0
    total_happiness = 0
    income_mod = {"gold": 1.0, "supply": 1.0, "happiness": 1.0}
    campaign_region_state = self.current_campaign_state["region"]
    owner = campaign_region_state[region_id]["control"]
    faction_culture_state = self.current_campaign_state["faction"][owner]["culture"]
    recruit_list = {"leader": [], "troop": [], "air": []}
    garrison_list = {"leader": [], "troop": [], "air": [], "strategy": []}

    for building_state in campaign_region_state[region_id]["building"]:
        if building_state:
            # building is active if it is not damaged, in progress, all requirement buildings are active
            if building_state[1] is True and not building_state[2] and building_state[3]:
                # building is in active state and not destroyed/constructing/repairing
                building_id = building_state[0]
                building_stat = self.building_list[building_id]
                integration_state = 1
                culture_prohibit = False
                if building_stat["Culture"] != "all":
                    culture_state = faction_culture_state[building_stat["Culture"]]
                    integration_state = culture_state["integration"]
                    if culture_state["policy"] == "reject":
                        culture_prohibit = True
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

                if not culture_prohibit:
                    if building_stat["Leader Recruit"]:
                        recruit_list["leader"] += [item for item in building_stat["Leader Recruit"] if
                                                   item not in recruit_list["leader"]]
                    if building_stat["Troop Recruit"]:
                        recruit_list["troop"] += [item for item in building_stat["Troop Recruit"] if
                                                  item not in recruit_list["troop"]]
                    if building_stat["Air Recruit"]:
                        recruit_list["air"] += [item for item in building_stat["Air Recruit"] if
                                                item not in recruit_list["air"]]

                    if building_stat["Leader Reinforcement"]:
                        garrison_list["leader"] += building_stat["Leader Reinforcement"]
                    if building_stat["Troop Reinforcement"]:
                        garrison_list["troop"] += building_stat["Troop Reinforcement"]
                    if building_stat["Air Reinforcement"]:
                        garrison_list["air"] += building_stat["Air Reinforcement"]
                    if building_stat["Garrison Strategy"]:
                        garrison_list["strategy"].append(building_stat["Garrison Strategy"])

    region_income_state = campaign_region_state[region_id]["income"]

    region_income_state["gold_income"] = total_gold_income * income_mod["gold"]
    region_income_state["supply_income"] = total_supply_income * income_mod["supply"]
    region_income_state["happiness"] = total_happiness * income_mod["happiness"]

    campaign_region_state[region_id]["garrison"] = garrison_list
    campaign_region_state[region_id]["recruit"] = recruit_list

    if owner == self.grand.player_faction:
        self.dots_settlement_info_banners[campaign_region_state[region_id]["dot"]].reset(owner)

    if faction_id == self.player_faction and region_id == self.region_management_ui.player_selected_region:
        self.region_management_ui.change_selected_region(region_id)
