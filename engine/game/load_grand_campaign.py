def load_grand_campaign(self, campaign):
    if self.campaign != campaign:
        self.loading_screen("Loading Campaign Data")  # add loading screen for different campaign load
        self.campaign = campaign
        self.map_data.load_campaign_data(campaign)
        self.localisation.read_localisation("region", (campaign,))
        self.localisation.read_localisation("faction", (campaign,))
        self.grand_setup_mini_map.change_grand_setup(self.map_data.base_world_map)
        self.grand_faction_selector.__init__(self.grand_faction_selector.width_limit,
                                             self.grand_faction_selector.pos)  # reset selector to include loaded factions
