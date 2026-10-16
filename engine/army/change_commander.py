def change_commander(self, new_commander_char_id):
    self.commander_id = new_commander_char_id

    # change commander actor
    self.commander_actor.change_team_state()
    self.grand.current_campaign_state["faction"][self.faction]["Character"][new_commander_char_id] = (self, "commander")
