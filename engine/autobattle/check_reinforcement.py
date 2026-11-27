from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.autobattle.autobattle import AutoBattle

from engine.battle.setup_team_characters import add_neutral_stage_character
from engine.battle.check_reinforcement import condition_check
from engine.constants import Default_Battle_Ground_Pos, Round_To_Battle_Time, Phase_To_Round

Round_to_Second = Round_To_Battle_Time / Phase_To_Round


def check_reinforcement(self: AutoBattle):
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
                    if self.team_commander[team] and self.team_commander[team].alive:
                        # team reinforcement allow only if commander exist and alive
                        if condition == "ground":
                            if reinforcement:
                                for this_reinforcement in reinforcement:
                                    # auto battle spawn unit in group to reduce computation
                                    character = this_reinforcement[0]

                                    data = self.character_list[character] | {"Team": team, "ID": character,
                                                                             "base_pos": (team_state["start_pos"],
                                                                                          Default_Battle_Ground_Pos)}

                                    self.add_auto_character(team, data)
                                    self.team_deployed[team] += this_reinforcement[3]

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
