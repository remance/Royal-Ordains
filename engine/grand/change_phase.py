from engine.constants import Turn_To_Phase

time_per_phase = 1 / Turn_To_Phase  # 1 cosmic time is 1 turn


def change_phase(self):
    self.cosmic_ui.phase_change()
    self.current_campaign_state["cosmic_time"] += time_per_phase

    # process respective faction ai assigned to the phase
    for faction_data in self.current_campaign_state["faction"].values():
        for army in faction_data["army"]:
            army.change_phase()

    for battle in self.current_campaign_state["battle"]["auto"]:  # process all auto battle
        pass
