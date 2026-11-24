def change_round(self):
    current_campaign_state = self.current_campaign_state
    for battle in current_campaign_state["battle"]["battles"].values():  # process all auto battle
        battle.change_round()