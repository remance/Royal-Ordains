from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand


def change_region_control(self: Grand, region_id, new_faction_id):
    current_campaign_state = self.current_campaign_state
    campaign_region_state = current_campaign_state["region"]
    this_region_state = campaign_region_state[region_id]

    if new_faction_id == self.player_faction:
        self.event_notification_ui.add_new_event((
            "event_good", self.grab_text(("ui", "info_text_gain_region")) + self.grab_text(("region", region_id, "Name")),
            str(current_campaign_state["turn"]) + "." + str(current_campaign_state["phase"]),
            self.region_list[region_id]["Settlement POS"]))
    elif this_region_state["control"] == self.player_faction:
        self.event_notification_ui.add_new_event((
            "event_bad", self.grab_text(("ui", "info_text_lose_region")) + self.grab_text(("region", region_id, "Name")),
            str(current_campaign_state["turn"]) + "." + str(current_campaign_state["phase"]),
            self.region_list[region_id]["Settlement POS"]))

    new_faction_owner_campaign_state = current_campaign_state["faction"][new_faction_id]
    # remove region control from old faction
    current_campaign_state["faction"][this_region_state["control"]]["region"].remove(region_id)
    # add region to new owner
    new_faction_owner_campaign_state["region"].append(region_id)
    this_region_state["control"] = new_faction_id

    # change settlement banner info
    for key, value in self.settlement_dots.items():
        if value == region_id:
            self.dots_settlement_info_banners[key].reset(new_faction_id)
            break

    if region_id == self.region_management_ui.change_selected_region:
        # collapse region management ui if player lose control while opening it
        self.region_management_ui.change_selected_region(None)
    self.mini_map.change_grand_faction(campaign_region_state)
    self.region_object_list[region_id].change_owner_state(new_faction_id, play_animation=True)
