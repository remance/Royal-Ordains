from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from math import ceil


def start_building_construction_or_repair(self: Grand, faction_id: str, region_id: str, slot: int, building_id: str):
    building_state = self.current_campaign_state["region"][region_id]["building"][slot]
    if not building_state[1]:  # repair
        building_state[2] = ceil(self.building_list[building_id]["Real Build Time"] / 2)
        self.current_campaign_state["faction"][faction_id]["gold"] -= ceil(self.building_list[building_id]["Cost"] / 2)
    else:  # construct new building
        building_state[0] = building_id
        building_state[2] = self.building_list[building_id]["Real Build Time"]
        self.current_campaign_state["faction"][faction_id]["gold"] -= self.building_list[building_id]["Cost"]

    if faction_id == self.player_faction:
        self.settlement_object_list[region_id].change_building_state(slot, building_state, also_change_state=True)

        if region_id == self.region_management_ui.player_selected_region:
            self.region_management_ui.change_selected_region(region_id)
