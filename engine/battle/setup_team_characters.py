from random import uniform

from pygame import Vector2
from engine.character.character import Character, BattleCharacter, CommanderBattleCharacter, AirBattleCharacter
from engine.constants import Default_Ground_Pos, Default_Float_Pos, Default_Air_Pos

team_start_x_distance = (600, 1200, 1800, 2400, 3000, 3600)
team_start_middle_x_distance = (600, -600, 1200, -1200, 1800, -1800, 2400, -2400)


def setup_team_characters(self, stage_data):
    """Setup all characters at the start of battle, not used for character spawn afterward"""
    for team, team_unit in self.team_stat.items():
        for key_type, key_data in team_unit["unit"].items():
            if key_data:
                commander_char = None
                if key_type in ("controllable", "uncontrollable"):
                    general_count = 0
                    control = False
                    if key_type == "controllable":
                        control = True
                    for value2 in key_data:
                        for character, data in value2.items():
                            is_commander = False
                            if not general_count and control:  # first controllable general is commander
                                is_commander = True
                            if self.team_stat[team]["start_pos"] == 0:
                                start_x = team_start_x_distance[general_count]
                            elif self.team_stat[team]["start_pos"] == self.base_stage_end:
                                start_x = self.base_stage_end - team_start_x_distance[general_count]
                            else:
                                start_x = self.team_stat[team]["start_pos"] + team_start_middle_x_distance[general_count]
                            data["Team"] = team
                            data["ID"] = character
                            if "POS" not in data:
                                data["POS"] = (start_x, Default_Ground_Pos)
                            if is_commander:
                                add_battle_char = CommanderBattleCharacter(self.last_char_game_id,
                                                                  data | self.character_data.character_list[character])
                                commander_char = add_battle_char
                                self.team_commander[team] = commander_char
                            else:
                                add_layer = 0
                                if control:
                                    add_layer = 1000000
                                add_battle_char = BattleCharacter(self.last_char_game_id,
                                                                  data | self.character_data.character_list[character],
                                                                  None, additional_layer=add_layer,
                                                                  is_general=True, is_controllable=control)
                            if team == 1 and control:
                                self.character_command_indicator[general_count].setup(add_battle_char)
                            self.last_char_game_id += 1
                            general_count += 1
                            for value in data["Followers"]:
                                add_followers(self, add_battle_char, value, data)
                            add_battle_char.reset_general_variables()
                if key_type == "air":
                    for squad in key_data:
                        this_group = []
                        for key, number in squad.items():
                            for _ in range(int(number)):
                                # leader of air units are commander
                                this_group.append(
                                    AirBattleCharacter(self.last_char_game_id, self.character_data.character_list[key] |
                                                       {"ID": key, "Team": team,
                                                        "Start Health": 1, "Start Resource": 1,
                                                        "POS": (-10000, 0)},
                                                       leader=commander_char))
                                self.last_char_game_id += 1
                        self.team_stat[team]["air_group"].append(this_group)

    for data in stage_data["character"]:
        if not data["Arrive Condition"]:  # neutral character with arrive condition got added via check_reinforcement
            add_neutral_character(self, data)


def add_neutral_character(self, input_data):
    data = input_data.copy()
    character_data = self.character_data.character_list[data["ID"]]
    if "fly" in character_data["Property"]:
        data["POS"] = (data["POS"], Default_Air_Pos)
        data["Ground Y POS"] = Default_Air_Pos
    elif "float" in character_data["Property"]:
        data["POS"] = (data["POS"], Default_Float_Pos)
        data["Ground Y POS"] = Default_Float_Pos
    else:
        data["POS"] = (data["POS"], Default_Ground_Pos)
    if "no_battle" in data["Stage Property"] or "no_battle" in character_data["Property"]:
        add_battle_char = Character(self.last_char_game_id,
                                    data | self.character_data.character_list[data["ID"]])
        self.last_char_game_id += 1
    else:
        add_battle_char = BattleCharacter(self.last_char_game_id, data | self.character_data.character_list[data["ID"]])
        self.last_char_game_id += 1


def add_followers(self, general, value, data, battle_char=True):
    char_class = Character
    if battle_char:
        char_class = BattleCharacter
    for key, number in value.items():
        for _ in range(int(number)):
            random_pos = Vector2(uniform(general.base_pos[0] - 300,
                                         general.base_pos[0] + 300), general.base_pos[1])
            if random_pos[0] < 0:
                random_pos[0] = 1
            elif random_pos[0] > self.base_stage_end:
                random_pos[0] = self.base_stage_end - 1
            char_class(self.last_char_game_id, self.character_data.character_list[key] |
                       {"ID": key, "Team": general.team,
                        "Start Health": data["Start Health"], "Start Resource": data["Start Resource"],
                        "POS": random_pos}, leader=general)
            self.last_char_game_id += 1
