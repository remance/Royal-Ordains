from random import uniform

from pygame import Vector2
from engine.character.character import BattleCharacter, AirBattleCharacter
from engine.constants import Default_Ground_Pos
from engine.battle.setup_team_characters import add_followers, add_neutral_character


def check_reinforcement(self):
    if len(self.all_characters) < 900:  # prevent too many characters in battle
        for condition_type in tuple(self.later_reinforcement.keys()):
            condition_data = self.later_reinforcement[condition_type]
            for condition in tuple(condition_data.keys()):
                reinforcement = condition_data[condition]
                if condition_type != "team":
                    if condition_check[condition_type](self, condition):
                        for key_data in reinforcement.copy():
                            add_neutral_character(self, key_data)
                            reinforcement.remove(key_data)  # remove added reinforcement from list
                else:
                    if self.team_commander[condition] and self.team_commander[condition].alive:
                        # team reinforcement allow only if commander exist and alive
                        for reinforcement_type in tuple(reinforcement.keys()):
                            reinforcement_list = reinforcement[reinforcement_type]
                            if reinforcement_type == "controllable":
                                for unit_dict_data in reinforcement_list.copy():
                                    if len([general for general in self.all_team_general[condition] if
                                            general.is_controllable]) >= 5:
                                        # No more than 5 controllable generals can be active in battle
                                        break
                                    for character, data in unit_dict_data.items():
                                        if "Team" not in data:
                                            data["Team"] = condition
                                        data["ID"] = character
                                        if "POS" not in data:
                                            data["POS"] = (self.team_stat[condition]["start_pos"], Default_Ground_Pos)

                                        add_battle_char = BattleCharacter(self.last_char_game_id,
                                                                          data | self.character_data.character_list[character],
                                                                          None, additional_layer=50,
                                                                          is_general=True, is_controllable=True)

                                        self.last_char_game_id += 1
                                        for value in data["Followers"]:
                                            add_followers(self, add_battle_char, value, data)
                                        add_battle_char.reset_general_variables()
                                        # auto order command to move from edge of battle when arrive
                                        if not self.team_stat[condition]["start_pos"]:
                                            add_battle_char.issue_commander_order(("attack", 300))
                                        elif self.team_stat[condition]["start_pos"] == self.base_stage_end:
                                            add_battle_char.issue_commander_order(("attack", self.base_stage_end - 300))
                                    reinforcement_list.remove(unit_dict_data)  # remove reinforcement from list

                            elif reinforcement_type == "air":
                                for squad in reinforcement_list.copy():
                                    if len(self.team_stat[condition]["air_group"]) >= 5:
                                        # No more than 5 controllable air groups can be available in battle
                                        break

                                    this_group = []
                                    for key, number in squad.items():
                                        for _ in range(int(number)):
                                            # leader of air units are commander
                                            this_group.append(
                                                AirBattleCharacter(self.last_char_game_id,
                                                                   self.character_data.character_list[key] |
                                                                   {"ID": key, "Team": condition,
                                                                    "Start Health": 1, "Start Resource": 1,
                                                                    "POS": (-10000, 0)},
                                                                   leader=self.team_commander[condition]))
                                            self.last_char_game_id += 1
                                    self.team_stat[condition]["air_group"].append(this_group)
                                    reinforcement_list.remove(squad)
                            if not reinforcement_list:
                                reinforcement.pop(reinforcement_type)
                    else:  # dead/not exist commander remove reinforcement
                        reinforcement = {}
                if not reinforcement:
                    condition_data.pop(condition)

            if not condition_data:
                self.later_reinforcement.pop(condition_type)


def weather_condition_check(self, weather):
    if self.current_weather.weather_type == weather:
        return True


def time_condition_check(self, time):
    if self.battle_time >= time:
        return True


condition_check = {"weather": weather_condition_check, "time": time_condition_check,}
