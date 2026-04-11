def dismiss_faction_character(self, faction, character):
    faction_state = self.current_campaign_state["faction"][faction]
    character_state = faction_state["character"][character]

    if character_state[0]:
        # in army, cannot dismiss commander
        army = character_state[0]
        army.remove_follower(character_state[1], character_state[0])

    faction_state["character"].pop(character)

    self.current_campaign_state["free_character"].append(character)
