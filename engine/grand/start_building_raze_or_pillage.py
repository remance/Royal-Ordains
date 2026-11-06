from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from math import ceil


def start_building_raze_or_pillage(self: Grand, faction_id: str, region_id: str, slot: int, building_id: str,
                                   pillage: bool = False):
    building_state = self.current_campaign_state["region"][region_id]["building"][slot]
    if pillage:  # pillage, take half time
        building_state[1] = "pillage"
        building_state[2] = ceil(self.building_list[building_id]["Real Build Time"] / 2)
    else:  # raze, take a quater time
        building_state[1] = "raze"
        building_state[2] = ceil(self.building_list[building_id]["Real Build Time"] / 4)

    if faction_id == self.player_faction:
        self.settlement_object_list[region_id].change_building_state(slot, building_state, also_change_state=True)

        if region_id == self.region_management_ui.player_selected_region:
            self.region_management_ui.change_selected_region(region_id)
