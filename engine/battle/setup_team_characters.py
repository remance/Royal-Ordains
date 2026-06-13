from engine.character.character import Character, BattleCharacter, CommanderBattleCharacter
from engine.constants import Default_Battle_Ground_Pos, Default_Battle_Float_Pos, Default_Battle_Air_Pos

team_start_x_distance = 600


def setup_team_characters(self, stage_data):
    """Setup all characters at the start of battle, not used for character spawn afterward"""
    for team, team_state in self.team_state.items():
        if "unit" in team_state:
            if team_state["commander_unit"]:
                data = {key: value for key, value in team_state["commander_unit"].items()}
                data["Team"] = team
                add_battle_char = CommanderBattleCharacter(self.last_char_game_id,
                                                           team_state["commander_unit"])
                commander_char = add_battle_char
                self.team_commander[team] = commander_char
                if team == self.player_team:
                    self.player_commander = commander_char
                    self.character_command_indicator.setup(add_battle_char)

                self.last_char_game_id += 1

            for unit in team_state["unit"]:
                # unit in team_state indicate this is battle that player control from auto
                data = {key: value for key, value in unit.items()}
                data["Team"] = team
                BattleCharacter(self.last_char_game_id, data | self.character_list[data["ID"]])
                self.last_char_game_id += 1

        elif team_state["main_army"]:
            data = {}
            if self.team_state[team]["start_pos"] == 0:
                start_x = team_start_x_distance
            else:
                start_x = self.base_stage_end - team_start_x_distance
            data["Team"] = team
            data["ID"] = team_state["main_army"].commander_id
            if "POS" not in data:
                data["POS"] = (start_x, Default_Battle_Ground_Pos)

            add_battle_char = CommanderBattleCharacter(self.last_char_game_id,
                                                       data | self.character_list[team_state["main_army"].commander_id])
            commander_char = add_battle_char
            self.team_commander[team] = commander_char
            if team == self.player_team:
                self.player_commander = commander_char
                self.character_command_indicator.setup(add_battle_char)

            self.last_char_game_id += 1
            for squad in team_state["main_army"].air_group:
                self.create_air_group(squad, team, commander_char)

    for data in stage_data["character"]:
        if not data["Arrive Condition"]:  # neutral character with arrive condition got added via check_reinforcement
            add_neutral_stage_character(self, data)


def add_neutral_stage_character(self, input_data):
    data = input_data.copy()
    character_data = self.character_list[data["ID"]]
    if "fly" in character_data["Property"]:
        data["POS"] = (data["POS"], Default_Battle_Air_Pos)
        data["Ground Y POS"] = Default_Battle_Air_Pos
    elif "float" in character_data["Property"]:
        data["POS"] = (data["POS"], Default_Battle_Float_Pos)
        data["Ground Y POS"] = Default_Battle_Float_Pos
    else:
        data["POS"] = (data["POS"], Default_Battle_Ground_Pos)
    if "no_battle" in data["Stage Property"] or "no_battle" in character_data["Property"]:
        add_battle_char = Character(self.last_char_game_id,
                                    data | self.character_list[data["ID"]])
        self.last_char_game_id += 1
    else:
        add_battle_char = BattleCharacter(self.last_char_game_id, data | self.character_list[data["ID"]])
        self.last_char_game_id += 1
