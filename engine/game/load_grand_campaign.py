def load_grand_campaign(self, campaign):
    if self.campaign != campaign:
        self.loading_screen("Loading Campaign Data")  # add loading screen for different campaign load
        self.campaign = campaign
        self.map_data.load_campaign_data(campaign)
        self.localisation.read_localisation("region", (campaign,))
        self.grand_mini_map.change_grand_setup(self.map_data.world_map)
