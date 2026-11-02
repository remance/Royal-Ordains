from random import uniform, choice
from engine.constants import Culture_Policy_Integration


def change_turn(self, turn_change=True):
    """
    Update campaign state when turn change
    @param self: Grand object
    @param turn_change: turn actually change or not, function can be used for campaign setup when False
    @return:
    """
    # TODO check for culture extinction
    current_campaign_state = self.current_campaign_state
    campaign_faction_state = current_campaign_state["faction"]
    campaign_region_state = current_campaign_state["region"]
    campaign_battle_state = current_campaign_state["battle"]
    for faction, faction_state in campaign_faction_state.items():
        if faction != "free":
            # update diplomacy relation  # TODO add cultural policy difference
            for diplomacy_value in faction_state["diplomacy"].values():
                diplomacy_value["value"] = 0
                for index, history in enumerate(tuple(diplomacy_value["history"])):
                    if diplomacy_value["history"][index][2] > 1:
                        diplomacy_value["history"][index][2] -= 1
                        diplomacy_value["value"] += diplomacy_value["history"][index][1]
                    else:
                        diplomacy_value["history"].pop(index)
            self.cal_faction_culture(faction)

            for region in faction_state["region"]:
                self.cal_region_income_recruit(faction, region)

            for army in faction_state["army"]:
                army.reset_stat(reset_player_army_card=True)

            self.cal_faction_income_recruit(faction)

            if turn_change:
                # event duration is based on turn rather than phase
                faction_state["event"] = [[event[0], event[1] - 1] for event in faction_state["event"] if event[1] > 1]

                # faction_region_control = self.campaign_region_state["control"][faction]
                for faction_culture in faction_state["culture"].values():
                    # increase or decrease integration every turn
                    policy_integration_cap = Culture_Policy_Integration[faction_culture["policy"]]
                    if faction_culture["integration"] < policy_integration_cap:
                        faction_culture["integration"] += 0.01
                    elif faction_culture["integration"] > policy_integration_cap:
                        faction_culture["integration"] -= 0.01

                faction_state["gold"] += faction_state["gold_income"]
                faction_state["supply"] += faction_state["supply_income"]

                if faction_state["gold"] < 0:  # last 10 turns each
                    faction_state["event"].append([{"ID": "bankrupt", "happiness": faction_state["gold"] / 1000}, 10])
                if faction_state["supply"] < 0:
                    faction_state["event"].append([{"ID": "famine", "happiness": faction_state["supply"] / 1000}, 10])

                if faction_state["happiness"] < 0:
                    # check for rebel among unhappy region
                    for region in faction_state["region"]:
                        region_state = campaign_region_state[region]
                        if (region_state["dot"] not in campaign_battle_state["dot"] or
                                "free" in campaign_battle_state["factions"][region_state["dot"]]):
                            # can only spawn rebel in region with no battle or free faction already fighting in it
                            happiness = region_state["income"]["happiness"]
                            if happiness < 0:
                                spawn_chance = -400
                            else:
                                spawn_chance = -1000
                            # check for random rebel
                            if uniform(spawn_chance, 0) > faction_state["happiness"]:
                                # rebel!
                                self.create_rebel_army(region, faction_state, int(uniform(20, 20 + (-happiness * 2))))
    self.change_phase(phase_change=turn_change)
