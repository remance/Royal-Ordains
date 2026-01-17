from engine.character.character import AirBattleCharacter


def create_air_group(self, squad, team, commander_char):
    this_group = []
    number = self.character_list[squad]["Arrive Per Call"]
    for _ in range(int(number)):
        this_group.append(
            AirBattleCharacter(self.last_char_game_id, self.character_list[squad] |
                               {"ID": squad, "Team": team, "POS": (-10000, 0)}, leader=commander_char))
        self.last_char_game_id += 1
    self.team_stat[team]["air_group"].append(this_group)
