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
    if offer and receive_faction_diplomacy_state[offer_faction_id]["offer"]:
        # both factions agree to alliance
        offer_faction_state["alliance"].append(receiver_faction_id)
        receive_faction_state["alliance"].append(offer_faction_id)

    elif not offer and receive_faction_diplomacy_state[offer_faction_id]["offer"]:
        # quit alliance
        offer_faction_state["alliance"].remove(receiver_faction_id)
        receive_faction_state["alliance"].remove(offer_faction_id)

    if offer_faction_id == player_faction or receiver_faction_id == player_faction:
        ai_faction = offer_faction_id
        if offer_faction_id == player_faction:
            ai_faction = receiver_faction_id
        diplomacy_management_ui = self.diplomacy_management_ui
        diplomacy_management_ui.update_card(ai_faction, change_ally_status=True)
