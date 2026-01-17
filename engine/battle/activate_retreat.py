def activate_retreat(self, team):
    self.drama_text.queue.append((self.localisation.grab_text(("ui", "Team")) + str(team) +
                                  self.localisation.grab_text(("ui", "retreats")),
                                  None))
    for character in self.battle.all_team_ally[self.team]:
        character.broken = True
    for air_group in self.battle.team_stat[self.team]["air_group"]:
        for character in air_group:
            character.broken = True
