from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.autobattle.autobattle import AutoBattle

from random import randint, uniform

from engine.autounitgroup.autounitgroup import AutoUnitGroup
from engine.constants import Default_Battle_Ground_Pos


def activate_strategy(self: AutoBattle, team: int, strategy_id: str, base_pos_x: (int, float)):
    stat = self.strategy_list[strategy_id]
    range_check = stat["Range"]
    stat_property = stat["Property"]
    commander = self.team_commander[team]
    this_team_state = self.team_state[team]
    if (this_team_state["strategy_resource"] > stat["Resource Cost"] and (
            not commander or not stat["Activate Range"] or
            abs(commander.base_pos[0] - base_pos_x) < stat["Activate Range"])):
        this_team_state["strategy_resource"] -= stat["Resource Cost"]

        # if :
        # self.grand.tactical_map_ui.warn_strategy(base_pos_x)

        this_strategy_cooldown = this_team_state["strategy_cooldown"][strategy_id]
        for index, value in enumerate(this_strategy_cooldown):
            if not value:  # replace cooldown 0 with strategy cooldown
                this_strategy_cooldown[index] = stat["Cooldown"]
                break
        if stat_property:
            if "weather" in stat_property:  # strategy that change weather
                self.current_weather.__init__(self, stat_property["weather"], randint(120, 250),
                                              randint(0, 2))

        if stat["Summon"]:
            if "chaos_summon" in stat_property:  # chaos summon enemy with neutral team
                team = 0
            for spawn_name, spawn_num in stat["Summon"].items():
                for _ in range(spawn_num):
                    start_x = base_pos_x
                    if "random_summon_pos" in stat_property:
                        # put summon to random pos
                        start_x = base_pos_x + uniform(-range_check, range_check)
                    if start_x < 0:
                        start_x = 0
                    elif start_x > self.base_stage_end:
                        start_x = self.base_stage_end
                    start_pos = (start_x, Default_Battle_Ground_Pos)

                    self.add_auto_character(team, self.character_list[spawn_name] |
                                            {"ID": spawn_name, "Team": team, "POS": start_pos}, is_summon=True,
                                            specific_number=spawn_num)

        if stat["Damage Effects"]:
            if "air" not in stat["AI Condition"]:
                for enemy in self.all_team_ground_enemy_collision_grids[team][0]:
                    if abs(enemy.base_pos[0] - base_pos_x) < range_check:
                        for effect_stat in stat["Damage Effects"]:
                            commander.cal_damage_and_loss(enemy, stat, stat["Offence"], stat["Offence"] * 0.5)
            else:
                for enemy in self.all_team_air_enemy_collision_grids[team][0]:
                    if abs(enemy.base_pos[0] - base_pos_x) < range_check:
                        for effect_stat in stat["Damage Effects"]:
                            commander.cal_damage_and_loss(enemy, stat, stat["Offence"], stat["Offence"] * 0.5)
            for effect_stat in stat["Damage Effects"]:
                if "summon" in self.effect_list[effect_stat]["Property"]:
                    start_x = base_pos_x
                    if start_x < 0:
                        start_x = 0
                    elif start_x > self.base_stage_end:
                        start_x = self.base_stage_end
                    start_pos = (start_x, Default_Battle_Ground_Pos)

                    self.add_auto_character(team, self.character_list[self.effect_list[effect_stat]["Property"]["summon"]] |
                                            {"ID": spawn_name, "Team": team, "POS": start_pos}, is_summon=True,
                                            specific_number=1)

        if stat["Enemy Status"]:
            for enemy in self.all_team_ground_enemy_collision_grids[team][0]:
                if abs(enemy.base_pos[0] - base_pos_x) < range_check:
                    for effect in stat["Enemy Status"]:
                        enemy.apply_status(effect)
            for enemy in self.all_team_air_enemy_collision_grids[team][0]:
                if abs(enemy.base_pos[0] - base_pos_x) < range_check:
                    for effect in stat["Enemy Status"]:
                        enemy.apply_status(effect)

        if stat["Status"]:
            for ally in [key for key in self.all_team_ally[team] if abs(key.base_pos[0] - base_pos_x) < range_check]:
                for effect in stat["Status"]:
                    ally.apply_status(effect)
        return True
