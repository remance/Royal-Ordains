def deploy_from_reserve(self, region):
    """deploy army from reserve"""
    self.base_pos = self.grand.region_list[region]["Settlement POS"]
    self.grand.current_campaign_state[self.faction]["reserved"].remove(self)
    self.grand.current_campaign_state[self.faction]["army"].add(self)
    self.grand.dots_army_occupation[self.base_pos].add(self)

    # add actor and actor circle from updater
    self.grand.grand_actor_updater.add(self.commander_actor)
    self.grand.grand_camera_object_drawer.add(self.commander_actor)

    self.grand.grand_actor_updater.add(self.commander_actor.grand_faction_actor_circle)
    self.grand.grand_camera_object_drawer.add(self.commander_actor.grand_faction_actor_circle)