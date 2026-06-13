from engine.constants import Phase_To_Battle_Time


def auto_battle_process(self, battle_state):
    # update supply, strategy
    full_team_state = battle_state["team"]
    for team, team_state in full_team_state.items():
        team_state["strategy_cooldown"] = {key: value - Phase_To_Battle_Time if value > Phase_To_Battle_Time else 0 for
                                           key, value in team_state["strategy_cooldown"].items()}
        team_commander = self.team_commander[team]
        if team_commander and team_commander.alive and team_state["strategy_resource"] < 200:
            team_state["strategy_resource"] += Phase_To_Battle_Time * team_state["strategy_regen"]
            if team_state["strategy_resource"] > 100:
                team_state["strategy_resource"] = 100

        if team_state["supply_reserve"]:
            if team_state["supply_reserve"] > 0:
                supply_transfer = team_state["supply_reserve"] * 0.004 * Phase_To_Battle_Time
            else:
                supply_transfer = team_state["supply_reserve"]
            team_state["supply_resource"] += supply_transfer
            team_state["supply_reserve"] -= supply_transfer

        if team_state["supply_reserve"]:
            team_state["commander"]

    # call troop

    pass


def add_reinforcement(self, army):
    pass


def end_battle(self):
    pass
    # if army.faction == self.player_faction:
    # reset_card
