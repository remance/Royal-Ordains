def change_active_commander_actor(self, new_commander_char_id):
    self.commander_id = new_commander_char_id

    # change commander actor
    self.commander_actor.change_team_state()
