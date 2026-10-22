from math import ceil

from engine.constants import Diplomacy_Turn_Event_Gift


def give_faction_gift(self, give_faction, receive_faction, which: str):
    give_faction_state = self.current_campaign_state["faction"][give_faction]
    receive_faction_state = self.current_campaign_state["faction"][receive_faction]
    if which == "gold":
        give_value = ceil(give_faction_state["gold"] * 0.1)
        receiver_diff = give_value / (receive_faction_state["gold"] + receive_faction_state["gold_income"])
        receive_faction_state["gold"] += give_value
        give_faction_state["gold"] -= give_value
    else:
        give_value = ceil(give_faction_state["supply"] * 0.1)
        receiver_diff = give_value / (receive_faction_state["supply"] + receive_faction_state["supply_income"])
        receive_faction_state["supply"] += give_value
        give_faction_state["supply"] -= give_value

    if receiver_diff > 0.1:
        diplomacy_value = ceil(receiver_diff * 10)
        if diplomacy_value > 20:  # maximum diplomacy benefit from gift is twice the reserve+income of receiver
            diplomacy_value = 20
    else:
        diplomacy_value = 1

    self.add_diplomacy_history_event(receive_faction, give_faction, "gift", diplomacy_value,
                                     Diplomacy_Turn_Event_Gift)
