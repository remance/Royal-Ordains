from engine.constants import Round_To_Game_Time


def change_round(self):
    current_campaign_state = self.current_campaign_state
    for battle in current_campaign_state["battle"]["battles"].values():  # process all auto battle
        battle.change_round()

    if self.tactical_map_ui in self.outer_ui_updater:
        self.tactical_map_ui.update_timer = Round_To_Game_Time
        self.tactical_map_ui.update(0)
