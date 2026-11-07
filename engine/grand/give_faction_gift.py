from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from math import ceil

from engine.constants import Diplomacy_Turn_Event_Gift


def give_faction_gift(self: Grand, giver_faction_id: str, receiver_faction_id: str, which: str):
    give_faction_state = self.current_campaign_state["faction"][giver_faction_id]
    receive_faction_state = self.current_campaign_state["faction"][receiver_faction_id]

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
        if receive_faction_state == self.player_faction:
            self.add_diplomacy_talk_queue(tuple(give_faction_state["character"].keys())[0], "offer_gift")
        elif giver_faction_id == self.player_faction:
            self.add_diplomacy_talk_queue(tuple(receive_faction_state["character"].keys())[0], "accept_gift")

        diplomacy_value = ceil(receiver_diff * 10)
        if diplomacy_value > 20:  # maximum diplomacy benefit from gift is twice the reserve+income of receiver
            diplomacy_value = 20
    else:
        diplomacy_value = 1

    self.add_diplomacy_history_event(receiver_faction_id, giver_faction_id, "gift", diplomacy_value,
                                     Diplomacy_Turn_Event_Gift)
