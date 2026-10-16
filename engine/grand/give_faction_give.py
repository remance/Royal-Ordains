def give_faction_gift(self, give_faction, receive, which):
    give_faction_state = self.current_campaign_state["faction"][give_faction]
    give_faction_diplomacy_state = give_faction_state["diplomacy"]
    receive_faction_state = self.current_campaign_state["faction"][receive]
    receive_faction_diplomacy_state = receive_faction_state["diplomacy"]

