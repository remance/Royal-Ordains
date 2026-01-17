from engine.utils.data_loading import load_image


def load_grand_campaign(self, campaign):
    if self.campaign != campaign:
        self.campaign = campaign
        self.map_data.read_region_data(campaign)
        self.localisation.read_localisation("region", (campaign,))
        self.grand_mini_map.change_grand_setup(load_image(
            self.data_dir, (1, 1), "world_show.png", ("map", "world", campaign),
            no_alpha=True))
