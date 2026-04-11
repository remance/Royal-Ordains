def add_or_remove_technology(self, region, technology, remove=False):  # TODO add tech effect
    if remove:
        self.current_campaign_state["region"][region]["technology"].remove(technology)
    else:
        self.current_campaign_state["region"][region]["technology"].append(technology)
