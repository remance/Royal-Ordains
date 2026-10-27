def remove_army_from_active(self, destroyed=False):
    """remove army and put it in reserved instead"""
    self.current_region = None

    grand = self.grand
    if destroyed:  # destroyed army get supply removed
        self.supply = 0  # remove supply
        # grand.current_campaign_state["faction"][self.faction]# add destroy event

    grand.current_campaign_state[self.faction]["army"].remove(self)
    grand.current_campaign_state[self.faction]["reserve"].add(self)
    grand.dots_army_occupation[self.base_pos].remove(self)
    grand.sort_dot_army_occupation(self.base_pos)

    # remove actor and actor circle from updater
    grand.grand_object_updater.remove(self.commander_actor)
    grand.grand_camera_object_drawer.remove(self.commander_actor)

    self.commander_actor.clean_object()

    if self.faction == grand.player_faction:  # reset ui
        grand.player_army_list_ui.reset()

    grand.cal_faction_income_recruit()
