from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from random import uniform
from engine.constants import Culture_Policy_Integration, Culture_Policy_Difference_Relation, Culture_Policy_Key


def change_turn(self: Grand, turn_change: bool = True):
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
            # update diplomacy relation
            for diplomacy_value in faction_state["diplomacy"].values():
                diplomacy_value["value"] = 0
                for index, history in enumerate(tuple(diplomacy_value["history"])):
                    if diplomacy_value["history"][index][2] > 1:
                        diplomacy_value["history"][index][2] -= 1
                        diplomacy_value["value"] += diplomacy_value["history"][index][1]
                    else:
                        diplomacy_value["history"].pop(index)
            if faction != self.player_faction:  # no need to add diplomacy difference for player
                for culture, culture_state in faction_state["culture"].items():
                    culture_policy_index = Culture_Policy_Key.index(culture_state["policy"])
                    for faction2, faction_state2 in campaign_faction_state.items():
                        if faction2 != faction:
                            if culture in faction_state2["culture"]:
                                # difference event last 1 turn but added every turn
                                self.add_diplomacy_history_event(faction2, faction, "culture_difference",
                                                                 Culture_Policy_Difference_Relation[
                                                                     abs(culture_policy_index - Culture_Policy_Key.index(
                                                                         culture_state["policy"]))], 1)

            self.cal_faction_culture(faction)

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
                        settlement_dot = region_state["dot"]
                        if (settlement_dot not in campaign_battle_state["dot"] or
                                "free" in campaign_battle_state["factions"][settlement_dot]):
                            # can only spawn rebel in region with no battle or free faction already fighting in it
                            happiness = region_state["income"]["happiness"]
                            if happiness < 0:
                                spawn_chance = -400
                            else:
                                spawn_chance = -1000
                            # check for random rebel
                            if (uniform(spawn_chance, 0) > faction_state["happiness"] and
                                    len(self.dots_army_occupation[settlement_dot]) < 40):
                                # rebel!, hard limit rebel not showing up when there are more than 40 armies exist there
                                self.create_rebel_army(region, faction_state, int(uniform(20, 20 + (-happiness * 2))))
    self.change_phase(phase_change=turn_change)
