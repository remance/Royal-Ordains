from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle.battle import Battle

from engine.battle.setup_team_characters import add_neutral_stage_character
from engine.character.character import BattleCharacter
from engine.constants import Default_Battle_Ground_Pos


def check_reinforcement(self: Battle):
    """Check for reinforcement and add them to battle"""
    for team, team_state in self.team_state.items():
        later_reinforcement = team_state["later_reinforcement"]
        for condition_type in tuple(later_reinforcement.keys()):
            condition_data = later_reinforcement[condition_type]
            for condition in tuple(condition_data.keys()):
                reinforcement = condition_data[condition]
                if condition_type != "team":
                    if condition_check[condition_type](self, condition):
                        for key_data in reinforcement.copy():
                            add_neutral_stage_character(self, key_data)
                            reinforcement.remove(key_data)  # remove added reinforcement from list
                else:
                    if self.team_commander[team] and self.team_commander[team].alive and \
                            len(self.all_team_ally[team]) < 500:  # prevent too many characters per team in battle:
                        # team reinforcement allow only if commander exist and alive
                        if condition == "ground":
                            if reinforcement:
                                for this_reinforcement in reinforcement:
                                    character = this_reinforcement[0]
                                    this_reinforcement[2] += self.dt
                                    if this_reinforcement[2] >= this_reinforcement[1]:
                                        this_reinforcement[2] -= this_reinforcement[1]
                                        data = {"Team": team, "ID": character}
                                        if "POS" not in data:
                                            data["POS"] = (team_state["start_pos"], Default_Battle_Ground_Pos)

                                        add_battle_character = BattleCharacter(self.last_char_game_id,
                                                                               data | self.character_list[character],
                                                                               self.team_commander[team])
                                        add_battle_character.enter_stage()
                                        self.team_deployed[team] += 1
                                        self.last_char_game_id += 1

                                        this_reinforcement[3] -= 1
                                        if this_reinforcement[3] <= 0:
                                            # remove reinforcement from list when all arrive
                                            reinforcement.remove(this_reinforcement)

                        if condition == "air":
                            if reinforcement and len(team_state["air_group"]) < 5:
                                # No more than 5 controllable air groups can be available in battle
                                self.create_air_group(reinforcement[0], team,
                                                      self.team_commander[team])
                                reinforcement.pop(0)

                    else:  # dead/not exist commander remove reinforcement
                        reinforcement = {}
                if not reinforcement:  # no more reinforcement left
                    condition_data.pop(condition)

            if not condition_data:  # no more reinforcement left for this type
                later_reinforcement.pop(condition_type)


def weather_condition_check(self, weather):
    if self.current_weather.weather_type == weather:
        return True


def time_condition_check(self, time):
    if self.battle_time >= time:
        return True


condition_check = {"weather": weather_condition_check, "time": time_condition_check, }
