from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand


def offer_faction_ally(self: Grand, offer_faction_id: str, receiver_faction_id: str, offer: bool):
    player_faction = self.player_faction
    offer_faction_state = self.current_campaign_state["faction"][offer_faction_id]
    offer_faction_diplomacy_state = offer_faction_state["diplomacy"]
    receive_faction_state = self.current_campaign_state["faction"][receiver_faction_id]
    receive_faction_diplomacy_state = receive_faction_state["diplomacy"]
    offer_faction_diplomacy_state[receiver_faction_id]["offer"] = offer
    if offer:
        if receive_faction_diplomacy_state[offer_faction_id]["offer"]:  # receiver already offer before
            # both factions agree to alliance
            if offer_faction_id == player_faction:  # player agree to alliance offer
                self.add_diplomacy_talk_queue(tuple(receive_faction_state["character"].keys())[0], "accept_ally_you")
            elif receiver_faction_id == player_faction:  # ai agree to player alliance offer
                self.add_diplomacy_talk_queue(tuple(offer_faction_state["character"].keys())[0], "accept_ally")
            offer_faction_state["alliance"].append(receiver_faction_id)
            receive_faction_state["alliance"].append(offer_faction_id)
        else:
            if receiver_faction_id == player_faction:  # player got offer alliance from ai
                self.add_diplomacy_talk_queue(tuple(offer_faction_state["character"].keys())[0], "offer_ally")

    else:
        if receive_faction_diplomacy_state[offer_faction_id]["offer"]:
            # quit alliance
            if offer_faction_id == player_faction:  # player quit alliance
                self.add_diplomacy_talk_queue(tuple(receive_faction_state["character"].keys())[0], "war_you")
            else:  # ai quit alliance
                self.add_diplomacy_talk_queue(tuple(offer_faction_state["character"].keys())[0], "war")

            offer_faction_state["alliance"].remove(receiver_faction_id)
            receive_faction_state["alliance"].remove(offer_faction_id)

    if offer_faction_id == player_faction or receiver_faction_id == player_faction:
        # update player diplomacy ui
        ai_faction = offer_faction_id
        if offer_faction_id == player_faction:
            ai_faction = receiver_faction_id
        diplomacy_management_ui = self.diplomacy_management_ui
        diplomacy_management_ui.update_card(ai_faction, change_ally_status=True)
