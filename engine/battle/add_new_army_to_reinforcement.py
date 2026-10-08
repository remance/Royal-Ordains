def add_new_army_to_reinforcement(self, team, team_state, army):
    commander_id = army.commander_id
    character_list = self.character_list
    team_state["supply_reserve"] += army.supply
    team_state["total_supply"] += army.supply
    team_state["leader_call_list"].append([commander_id, 1, character_list[commander_id][
        "Supply"]])  # add reinforcement commander as leader
    team_state["leader_call_list"] += [
        [item[0], character_list[item[0]]["Capacity"], character_list[item[0]]["Supply"]] for item in
        army.army_followers["leader"] if item[1]]
    team_state["troop_call_list"] += [
        [item[0], character_list[item[0]]["Capacity"], character_list[item[0]]["Supply"]] for item in
        army.army_followers["troop"] if item[1]]

    air_reinforcement = [air_group[0] for air_group in army.army_followers["air"] if air_group[1]]
    if air_reinforcement:
        later_reinforcement = self.later_reinforcement
        if "team" not in later_reinforcement:
            later_reinforcement["team"] = {}
        if team not in later_reinforcement["team"]:
            later_reinforcement["team"][team] = {}
        if "air" not in later_reinforcement["team"][team]:
            later_reinforcement["team"][team]["air"] = []
        later_reinforcement["team"][team]["air"] += air_reinforcement
