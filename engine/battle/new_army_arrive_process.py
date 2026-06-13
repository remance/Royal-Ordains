def new_army_arrive_process(self, army, team):
    battle_character_list = []
    team_state = self.team_state[team]

    # add retinue
    if len(team_state["active_retinue"]) < 3:
        if army.retinue:
            for retinue in army.retinue:
                strategy = self.character_data.character_list[retinue]["Strategy"]
                if self.strategy_list[strategy]["Summon"]:
                    battle_character_list += list(self.strategy_list[strategy]["Summon"].keys())

    battle_character_list.append(army.commander_id)
    for air_group in army.air_group:
        battle_character_list.append(air_group)
    for character in army.ground_group:
        battle_character_list.append(character)
    for character in army.leader_group:
        battle_character_list.append(character)

    battle_character_list = self.check_battle_character_to_load(battle_character_list)

    self.sprite_data.inner_load_character_animation(battle_character_list)
    if team not in self.awaiting_armies:
        self.awaiting_armies[team] = []
    self.awaiting_armies[team].append(army)
