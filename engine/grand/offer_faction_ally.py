def offer_faction_ally(self, offer_faction, receive_faction, offer: bool):
    offer_faction_state = self.current_campaign_state["faction"][offer_faction]
    offer_faction_diplomacy_state = offer_faction_state["diplomacy"]
    receive_faction_state = self.current_campaign_state["faction"][receive_faction]
    receive_faction_diplomacy_state = receive_faction_state["diplomacy"]
    offer_faction_diplomacy_state[receive_faction]["offer"] = offer
    if offer and receive_faction_diplomacy_state[receive_faction]["offer"]:
        # both factions agree to alliance
        offer_faction_state["alliance"].append(receive_faction)
        receive_faction_state["alliance"].append(offer_faction)

    elif not offer and receive_faction_diplomacy_state[receive_faction]["offer"]:
        # quit alliance
        offer_faction_state["alliance"].remove(receive_faction)
        receive_faction_state["alliance"].remove(offer_faction)

    if offer_faction == self.player_faction or receive_faction == self.player_faction:
        ai_faction = offer_faction
        if receive_faction == self.player_faction:
            ai_faction = receive_faction
        diplomacy_management_ui = self.diplomacy_management_ui
        diplomacy_management_ui.update_card(ai_faction,
                                            change_ally_status=True)