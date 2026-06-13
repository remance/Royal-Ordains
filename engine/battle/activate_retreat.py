def activate_retreat(self, team):
    bad_drama = False
    if team == self.player_team:
        bad_drama = True
    self.drama_text.queue.append((bad_drama,
                                  self.localisation.grab_text(("ui", "Team")) + str(team) +
                                  self.localisation.grab_text(("ui", "retreats")),
                                  None))
    for character in self.battle.all_team_ally[self.team]:
        character.broken = True
    for air_group in self.battle.team_state[self.team]["air_group"]:
        for character in air_group:
            character.broken = True
