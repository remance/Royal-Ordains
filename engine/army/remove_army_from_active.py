def remove_army_from_active(self, destroyed=False):
    """remove army and put it in reserved instead"""
    grand = self.grand
    if destroyed:  # destroyed army get supply removed
        self.supply = 0  # remove supply
        # grand.current_campaign_state["faction"][self.faction]# add destroy event

    grand.current_campaign_state[self.faction]["army"].remove(self)
    grand.current_campaign_state[self.faction]["reserved"].add(self)
    grand.dots_army_occupation[self.base_pos].remove(self)

    # remove actor and actor circle from updater
    grand.grand_actor_updater.remove(self.commander_actor)
    grand.grand_camera_object_drawer.remove(self.commander_actor)

    grand.grand_actor_updater.remove(self.commander_actor.grand_faction_actor_circle)
    grand.grand_camera_object_drawer.remove(self.commander_actor.grand_faction_actor_circle)

    if self.faction == grand.player_faction:  # reset ui
        grand.player_army_list_ui.reset_list()

    grand.cal_faction_income()
