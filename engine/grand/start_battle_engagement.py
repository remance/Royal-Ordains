def start_battle_engagement(self, armies):
    campaign_battle_state = self.current_campaign_state["battle"]
    for army in armies:
        campaign_battle_state["armies"].append(army)
        if army.faction == self.player_faction:
            self.grand.player_army_list_ui.reset_card(army)
