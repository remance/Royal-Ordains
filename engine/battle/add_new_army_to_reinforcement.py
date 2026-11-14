from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.army.army import Army
    from engine.battle.battle import Battle


def add_new_army_to_reinforcement(self: Battle, team_state: dict, army: Army):
    commander_id = army.commander_id
    character_list = self.character_list
    team_state["supply_reserve"] += army.supply
    team_state["total_supply"] += army.supply
    team_state["leader_call_list"].append([commander_id, 1, character_list[commander_id][
        "Supply"]])  # add reinforcement commander as leader
    team_state["leader_call_list"] += [
        [item[0], character_list[item[0]]["Capacity"], character_list[item[0]]["Supply"]] if not army.is_garrison else
        [item[0], character_list[item[0]]["Capacity"], 0] for item in army.army_followers["leader"] if item and item[1]]
    team_state["troop_call_list"] += [
        [item[0], character_list[item[0]]["Capacity"], character_list[item[0]]["Supply"]] if not army.is_garrison else
        [item[0], character_list[item[0]]["Capacity"], 0] for item in army.army_followers["troop"] if item and item[1]]

    if army.garrison_strategy:
        for strategy in army.garrison_strategy:
            self.add_strategy_to_team_state(team_state, strategy)

    air_reinforcement = [air_group[0] for air_group in army.army_followers["air"] if air_group and air_group[1]]
    if air_reinforcement:
        if "team" not in team_state["later_reinforcement"]:
            team_state["later_reinforcement"]["team"] = {}
        if "air" not in team_state["later_reinforcement"]["team"]:
            team_state["later_reinforcement"]["team"]["air"] = []
        team_state["later_reinforcement"]["team"]["air"] += air_reinforcement

