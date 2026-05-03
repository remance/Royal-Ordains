def change_phase(self):
    self.current_campaign_state

    # process respective faction ai assigned to the phase

    for faction_data in self.current_campaign_state["faction"].values():
        for army in faction_data["army"]:
            army.change_phase()

    for battle in self.current_campaign_state["battle"]["auto"]:  # process all auto battle
        pass
