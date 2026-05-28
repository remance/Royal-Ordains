def start_battle_engagement(self, armies, base_pos, team1_alliance):
    current_campaign_state = self.current_campaign_state
    campaign_battle_dot = current_campaign_state["battle"]["dot"]
    campaign_battle_armies = current_campaign_state["battle"]["armies"]
    campaign_battle_state = current_campaign_state["battle"]["state"]
    current_campaign_state["battle"]["auto"].append(base_pos)

    campaign_battle_dot[base_pos] = armies
    campaign_battle_state[base_pos] = {"team": [], "armies": [], "battle_character": {},
                                       "supply": {}, "strategy": {}}
    team_1_army = None  # attacker
    team_2_army = None  # defender
    team_1_sub_armies = []
    team_2_sub_armies = []
    for army in armies:
        if not team_1_army and army.faction in team1_alliance:
            team_1_army = army
        if not team_2_army and army.faction not in team1_alliance:
            team_2_army = army
        army.assembling = {}  # cancel assembling
        if army not in campaign_battle_armies:
            campaign_battle_armies.append(army)

        if army.faction == self.player_faction:
            self.player_army_list_ui.reset_card(army)

    team_stat = {
        0: {"faction": "free", "culture": "free", "strategy_resource": 0, "start_pos": 0.5, "air_group": [],
            "active_retinue": (), "retinue": (),
            "strategy": [], "strategy_cooldown": {},
            "main_army": None,
            "reinforcement_army": []},
        1: {"faction": team_1_army.faction,
            "culture": team_1_army.culture,
            "strategy_resource": 0, "start_pos": 0, "air_group": [], "active_retinue": (), "retinue": (),
            "strategy": [], "strategy_cooldown": {},
            "main_army": team_1_army,
            "reinforcement_army": team_1_sub_armies},
        2: {"faction": team_2_army.faction,
            "culture": team_2_army.culture,
            "strategy_resource": 0, "start_pos": 1, "air_group": [],
            "active_retinue": (), "retinue": (), "strategy": [], "strategy_cooldown": {},
            "main_army": team_2_army,
            "reinforcement_army": team_2_sub_armies}}

    campaign_battle_state[base_pos]["team"].append(team_1_army.faction)
    campaign_battle_state[base_pos]["team"].append(team_2_army.faction)
