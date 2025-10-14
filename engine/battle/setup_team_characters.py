from random import uniform

from pygame import Vector2
from engine.character.character import Character, BattleCharacter, CommanderBattleCharacter, AirBattleCharacter
from engine.constants import Default_Ground_Pos

team_start_x_distance = (600, 1200, 1800, 2400, 3000, 3600)
team_start_middle_x_distance = (600, -600, 1200, -1200, 1800, -1800, 2400, -2400)


def setup_team_characters(self, unit_list, in_battle=True):
    """Setup all characters at the start of battle, not used for character spawn afterward"""
    if in_battle:
        for team, team_unit in unit_list.items():
            if team_unit:
                for key_type, key_data in team_unit.items():
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
                                else:
                                    add_battle_char = BattleCharacter(self.last_char_game_id,
                                                                      data | self.character_data.character_list[character],
                                                                      None, is_general=True, is_controllable=control)

                                self.last_char_game_id += 1
                                general_count += 1
                                for value in data["Followers"]:
                                    for leader, follower in value.items():
                                        random_pos = Vector2(uniform(add_battle_char.base_pos[0] - 300,
                                                                     add_battle_char.base_pos[0] + 300),
                                                             add_battle_char.base_pos[1])
                                        if random_pos[0] < 0:
                                            random_pos[0] = 1
                                        elif random_pos[0] > self.base_stage_end:
                                            random_pos[0] = self.base_stage_end - 1
                                        leader_char = BattleCharacter(self.last_char_game_id, self.character_data.character_list[leader] |
                                                        {"ID": leader, "Team": add_battle_char.team,
                                                         "Start Health": data["Start Health"],
                                                         "Start Resource": data["Start Resource"],
                                                         "POS": random_pos,
                                                         "Arrive Condition": ()}, leader=add_battle_char)
                                        self.last_char_game_id += 1
                                        for key, number in follower.items():
                                            for _ in range(int(number)):
                                                random_pos = Vector2(uniform(leader_char.base_pos[0] - 300,
                                                                     leader_char.base_pos[0] + 300), leader_char.base_pos[1])
                                                if random_pos[0] < 0:
                                                    random_pos[0] = 1
                                                elif random_pos[0] > self.base_stage_end:
                                                    random_pos[0] = self.base_stage_end - 1
                                                BattleCharacter(self.last_char_game_id, self.character_data.character_list[key] |
                                                                {"ID": key, "Team": add_battle_char.team,
                                                                 "Start Health": data["Start Health"], "Start Resource": data["Start Resource"],
                                                                 "POS": random_pos,
                                                                 "Arrive Condition": ()}, leader=leader_char)
                                                self.last_char_game_id += 1
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
                                                            "POS": (-10000, 0), "Arrive Condition": ()},
                                                           leader=commander_char))
                                    self.last_char_game_id += 1
                            self.team_stat[team]["air_group"].append(this_group)
    else:
        for data in unit_list:
            Character(data["Object ID"], data | self.character_data.character_list[data["ID"]])
