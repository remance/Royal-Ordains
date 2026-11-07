def remove_army_from_active(self, destroyed=False):
    """remove army and put it in reserved instead"""

    grand = self.grand
    current_campaign_state = grand.current_campaign_state
    faction_state = current_campaign_state[self.faction]
    if destroyed:
        if self.belong_to_player_faction:
            grand = self.grand
            grand.event_notification_ui.add_new_event((
                "event_bad", self.grab_text(("character", self.commander_id, "Name")) +
                self.grab_text(("ui", "army_destroyed")) + self.grab_text(("region", self.current_region, "Name")),
                str(current_campaign_state["turn"]) + "." + str(current_campaign_state["phase"]), ()))

    elif not destroyed and self.current_region:  # return supply to reserve
        faction_state["supply"] += self.supply
        self.supply = 0

    self.current_region = None

    faction_state["army"].remove(self)
    faction_state["reserve"].add(self)
    grand.dots_army_occupation[self.base_pos].remove(self)
    grand.sort_dot_army_occupation(self.base_pos)

    # remove actor and actor circle from updater
    grand.grand_object_updater.remove(self.commander_actor)
    grand.grand_camera_object_drawer.remove(self.commander_actor)

    self.commander_actor.clean_object()

    if self.belong_to_player_faction:  # reset ui
        grand.grand_army_list_ui.reset()

    grand.cal_faction_income_recruit()
