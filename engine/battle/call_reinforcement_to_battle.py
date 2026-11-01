from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle.battle import Battle


def call_reinforcement_to_battle(self: Battle, team: int, call_type: str, character_index: int):
    """Call unit to battle, add to reinforcement list"""
    team_state = self.team_state[team]
    if call_type == "leader":
        call_pool = team_state["leader_call_list"]
        if team == 1:
            cooldown_check = self.team1_call_leader_cooldown_reinforcement
        else:
            cooldown_check = self.team2_call_leader_cooldown_reinforcement
    else:
        call_pool = team_state["troop_call_list"]
        if team == 1:
            cooldown_check = self.team1_call_troop_cooldown_reinforcement
        else:
            cooldown_check = self.team2_call_troop_cooldown_reinforcement

    if (self.team_commander[team] and self.team_commander[team].alive and
            character_index not in cooldown_check and character_index < len(call_pool) and
            call_pool[character_index] and call_pool[character_index][2] <= team_state["supply_resource"]):

        later_reinforcement = team_state["later_reinforcement"]
        character_to_call = call_pool[character_index]
        if "team" not in later_reinforcement:
            later_reinforcement["team"] = {}
        if "ground" not in later_reinforcement["team"]:
            later_reinforcement["team"]["ground"] = []
        character_stat = self.character_list[character_to_call[0]]
        later_reinforcement["team"]["ground"].append(
            [character_to_call[0], character_stat["Respond Time"], 0, character_stat["Arrive Per Call"]])
        character_to_call[1] -= 1
        team_state["supply_resource"] -= call_pool[character_index][2]
        if character_to_call[1] <= 0:
            call_pool.remove(character_to_call)
        else:
            cooldown_check[character_index] = character_stat["Reinforce Time"]
