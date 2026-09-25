def add_new_army_to_reinforcement(self, team, team_state, army):
    commander_id = army.commander_id
    team_state["supply_reserve"] += army.supply
    team_state["total_supply"] += army.supply
    team_state["leader_call_list"].append([commander_id, 1, self.character_list[commander_id][
        "Supply"]])  # add reinforcement commander as leader
    team_state["leader_call_list"] += [
        [item[0], self.character_list[item[0]]["Capacity"], self.character_list[item[0]]["Supply"]] for item in
        army.army_followers["leader"] if item[1]]
    team_state["troop_call_list"] += [
        [item[0], self.character_list[item[0]]["Capacity"], self.character_list[item[0]]["Supply"]] for item in
        army.army_followers["troop"] if item[1]]

    air_reinforcement = [air_group[0] for air_group in army.army_followers["air"] if air_group[1]]
    if air_reinforcement:
        if "team" not in self.later_reinforcement:
            self.later_reinforcement["team"] = {}
        if team not in self.later_reinforcement["team"]:
            self.later_reinforcement["team"][team] = {}
        if "air" not in self.later_reinforcement["team"][team]:
            self.later_reinforcement["team"][team]["air"] = []
        self.later_reinforcement["team"][team]["air"] += air_reinforcement
