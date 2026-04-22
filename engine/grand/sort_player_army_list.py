def sort_player_army_list(self):
    how = self.player_army_list_sort_option_ui.option
    if how == "supply":
        self.current_campaign_state["faction"][self.player_faction]["army"].sort(key=lambda x: x.supply)
    elif how == "number":
        self.current_campaign_state["faction"][self.player_faction]["army"].sort(key=lambda x: x.total_number)
    elif how == "commander":
        self.current_campaign_state["faction"][self.player_faction]["army"].sort(
            key=lambda x: self.localisation.grab_text(("character", x.commander_id, "Name")))
    elif how == "region":
        self.current_campaign_state["faction"][self.player_faction]["army"].sort(
            key=lambda x: self.localisation.grab_text(("region", x.current_region, "Name")))

    self.player_army_list_ui.reset_list()
