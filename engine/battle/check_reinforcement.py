from engine.battle.setup_team_characters import add_neutral_stage_character
from engine.character.character import BattleCharacter
from engine.constants import Default_Battle_Ground_Pos


def check_reinforcement(self):
    for condition_type in tuple(self.later_reinforcement.keys()):
        condition_data = self.later_reinforcement[condition_type]
        for condition in tuple(condition_data.keys()):
            reinforcement = condition_data[condition]
            if condition_type != "team":
                if condition_check[condition_type](self, condition):
                    for key_data in reinforcement.copy():
                        add_neutral_stage_character(self, key_data)
                        reinforcement.remove(key_data)  # remove added reinforcement from list
            else:
                if self.team_commander[condition] and self.team_commander[condition].alive and \
                        len(self.all_team_ally[condition]) < 500:  # prevent too many characters per team in battle:
                    # team reinforcement allow only if commander exist and alive
                    if "ground" in reinforcement:
                        if reinforcement["ground"]:
                            for this_reinforcement in reinforcement["ground"]:
                                character = this_reinforcement[0]
                                this_reinforcement[2] += self.dt
                                if this_reinforcement[2] >= this_reinforcement[1]:
                                    this_reinforcement[2] -= this_reinforcement[1]
                                    data = {"Team": condition, "ID": character}
                                    if "POS" not in data:
                                        data["POS"] = (
                                            self.team_state[condition]["start_pos"], Default_Battle_Ground_Pos)

                                    add_battle_character = BattleCharacter(self.last_char_game_id,
                                                                      data | self.character_list[character],
                                                                      self.team_commander[condition])
                                    add_battle_character.enter_stage()
                                    self.team_deployed[condition] += 1
                                    self.last_char_game_id += 1

                                    this_reinforcement[3] -= 1
                                    if not this_reinforcement[3]:
                                        # remove reinforcement from list when all arrive
                                        reinforcement["ground"].remove(this_reinforcement)

                        if not reinforcement["ground"]:  # no more reinforcement left
                            reinforcement.pop("ground")

                    if "air" in reinforcement:
                        if reinforcement["air"] and len(self.team_state[condition]["air_group"]) < 5:
                            # No more than 5 controllable air groups can be available in battle
                            self.create_air_group(reinforcement["air"][0], condition,
                                                  self.team_commander[condition])
                            reinforcement["air"].pop(0)
                        if not reinforcement["air"]:
                            reinforcement.pop("air")
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


condition_check = {"weather": weather_condition_check, "time": time_condition_check, }
