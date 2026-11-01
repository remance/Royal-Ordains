def remove_army_from_reserve(self):
    grand = self.grand
    campaign_faction_state = grand.current_campaign_state["faction"][self.faction]
    faction_character_state = campaign_faction_state["character"]

    # remove hero to courtier
    if self.commander_id in faction_character_state:
        faction_character_state[self.commander_id] = (None, "courtier")
    for leader in self.army_followers["leader"]:
        if leader and leader[0] in faction_character_state:
            faction_character_state[leader[0]] = (None, "courtier")

    campaign_faction_state["reserve"].remove(self)
