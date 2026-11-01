def convert_battle_state_for_game(self, battle_state):
    """For converting saved data to game"""
    for team, team_value in battle_state.items():
        team_value["main_army"] = [army for army in self.current_campaign_state["faction"][team_value["main_army"][1]]["army"]
                                   if army.game_id == team_value["main_army"]][0]
        team_value["reinforcement_army"] = [army for army in self.current_campaign_state["faction"][faction]["army"] for army_id, faction in team_value["reinforcement_army"]
                                            if army.game_id == army_id]
        # team_value["commander_character"] =
        # team_value["commander_character"]["unit"] = []
        # team_value["commander_character"]["air_unit"] = []


def convert_battle_state_for_save(self, battle_state):
    """For converting game data to save"""
    for team_value in battle_state:
        team_value["main_army"] = (team_value["main_army"].game_id, team_value["main_army"].faction)
        team_value["reinforcement_army"] = [(army.game_id, army.faction) for army in team_value["reinforcement_army"]]
        team_value["commander_character"]
        team_value["commander_character"]["unit"]
        team_value["commander_character"]["air_unit"]