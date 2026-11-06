from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from math import ceil


def cancel_building_construction_or_repair(self: Grand, faction_id: str, region_id: str, slot: int, building_id: str):
    building_state = self.current_campaign_state["region"][region_id]["building"][slot]
    building_state[2] = 0
    if not building_state[1]:  # cancel repair
        self.current_campaign_state["faction"][faction_id]["gold"] += ceil(self.building_list[building_id]["Cost"] / 2)
    else:  # cancel construct new building
        building_state[0] = self.building_list[building_state[0]]["Precede"]  # return to precede
        self.current_campaign_state["faction"][faction_id]["gold"] += self.building_list[building_id]["Cost"]

    if faction_id == self.player_faction:
        # self.region_dots
        if region_id == self.region_management_ui.player_selected_region:
            self.region_management_ui.change_selected_region(region_id)

    self.settlement_object_list[region_id].change_building_state(slot, building_state, also_change_state=True)
