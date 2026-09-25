def setup_new_army_arrive(self, army, team):
    battle_character_list = []
    team_state = self.team_state[team]

    # add retinue
    if len(team_state["active_retinue"]) < 3:
        if army.army_followers["retinue"]:
            for retinue in [item[0] for item in army.army_followers["retinue"] if item[1]]:
                strategy = self.character_data.character_list[retinue]["Strategy"]
                if self.strategy_list[strategy]["Summon"]:
                    battle_character_list += list(self.strategy_list[strategy]["Summon"].keys())

    battle_character_list.append(army.commander_id)
    for follower_group in (army.army_followers["leader"], army.army_followers["troop"], army.army_followers["air"]):
        for follower in follower_group:
            if follower[1] and follower[0] not in battle_character_list:
                battle_character_list.append(follower[0])

    battle_character_list = self.check_battle_character_to_load(battle_character_list)

    self.sprite_data.inner_load_character_animation(battle_character_list)
    if team not in self.awaiting_armies:
        self.awaiting_armies[team] = []
    self.awaiting_armies[team].append(army)
