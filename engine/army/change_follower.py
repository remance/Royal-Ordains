def change_follower(self, role, slot, new_character, assembled=True):
    if role == "leader":
        faction_character_state = self.grand.current_campaign_state["faction"][self.faction]["Character"]
        old_character = faction_character_state[role][slot]
        if old_character and old_character[0] in faction_character_state:
            faction_character_state[old_character[0]] = [None, "courtier"]

        if new_character in faction_character_state:
            faction_character_state[new_character] = (self, "leader")

    self.army_followers[role][slot] = [new_character, assembled]
    self.reset_stat()
