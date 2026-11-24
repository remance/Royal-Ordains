from engine.autounitgroup.autounitgroup import AutoUnitGroup


def add_auto_character(self, team, character_data, is_commander: bool = False, is_summon: bool = False):
    if is_commander:
        character = AutoUnitGroup(self, self.last_game_id, character_data, is_commander=True)
        self.team_state[team]["commander_character"] = character
        self.team_commander[team] = character
    else:
        if "no_battle" in character_data["Property"]:
            character = AutoUnitGroup(self, self.last_game_id, character_data, no_combat=True, is_summon=is_summon)
        else:
            character = AutoUnitGroup(self, self.last_game_id, character_data, is_summon=is_summon)
        self.team_state[team]["unit"].append(character)
    self.all_team_enemy[team].add(character)
    self.last_game_id += 1
