def sort_player_army_list(self):
    how = self.player_army_list_sort_option_ui.option
    reverse = True
    if how[1] == "descend":
        reverse = False
    if how[0] == "supply":
        self.current_campaign_state["faction"][self.player_faction]["army"].sort(key=lambda x: x.supply,
                                                                                 reverse=reverse)
    elif how[0] == "number":
        self.current_campaign_state["faction"][self.player_faction]["army"].sort(key=lambda x: x.total_number,
                                                                                 reverse=reverse)
    elif how[0] == "commander":
        self.current_campaign_state["faction"][self.player_faction]["army"].sort(
            key=lambda x: self.localisation.grab_text(("character", x.commander_id, "Name")), reverse=reverse)
    elif how[0] == "region":
        self.current_campaign_state["faction"][self.player_faction]["army"].sort(
            key=lambda x: self.localisation.grab_text(("region", x.current_region, "Name")), reverse=reverse)

    self.player_army_list_ui.reset_list()
