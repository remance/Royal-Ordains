def change_commander(self, new_commander_char_id):
    faction_character_state = self.grand.current_campaign_state["faction"][self.faction]["Character"]
    if self.commander_id in faction_character_state:
        faction_character_state[self.commander_id] = [None, "courtier"]
    self.commander_id = new_commander_char_id

    # change commander actor
    self.commander_actor.change_team_state()
    if new_commander_char_id in faction_character_state:
        faction_character_state[new_commander_char_id] = (self, "commander")
    self.reset_stat()
