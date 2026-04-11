def remove_follower(self, follower_type, character):
    faction_character_state = self.grand.current_campaign_state["faction"][self.faction]["character"]
    if follower_type == "commander":
        self.commander_id = ""
    else:
        for index, follower_state in enumerate(self.army_followers[follower_type]):
            if character in follower_state:
                self.army_followers[follower_type][index] = []  # remove to empty
                break
    if character in faction_character_state:
        faction_character_state[character] = [None, "courtier"]
    self.reset_stat(reset_player_army_card=True)
