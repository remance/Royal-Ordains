def add_strategy_to_team_state(self, team_state, strategy):
    if strategy not in team_state["strategy_cooldown"]:
        team_state["strategy_cooldown"][strategy] = [0]
    else:
        team_state["strategy_cooldown"][strategy].append(0)
