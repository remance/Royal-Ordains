def change_follower(self, follower_type, slot, new_character_id, reset_stat=True):
    faction_character_state = self.grand.current_campaign_state["faction"][self.faction]["character"]

    if follower_type == "commander":
        old_character_id = self.commander_id
        self.commander_id = new_character_id
    else:
        old_character_id = self.army_followers[follower_type][slot]
        if old_character_id:
            old_character_id = old_character_id[0]
        else:  # empty slot with no character
            old_character_id = None

        if new_character_id:
            self.army_followers[follower_type][slot] = [new_character_id, False]
        else:  # remove follower
            self.army_followers[follower_type][slot] = []

    if old_character_id in faction_character_state:  # replaced old hero reassign to courtier
        faction_character_state[old_character_id] = (None, "courtier")

    if new_character_id in faction_character_state:  # assign new hero to this army
        faction_character_state[new_character_id] = (self, follower_type)

    if reset_stat:
        self.reset_stat(reset_player_army_card=True)
