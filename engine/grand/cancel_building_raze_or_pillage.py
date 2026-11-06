from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand


def cancel_building_raze_or_pillage(self: Grand, faction_id: str, region_id: str, slot: int):
    building_state = self.current_campaign_state["region"][region_id]["building"][slot]
    building_state[1] = True
    building_state[2] = 0

    if faction_id == self.player_faction and region_id == self.region_management_ui.player_selected_region:
        self.region_management_ui.change_selected_region(region_id)

    self.settlement_object_list[region_id].change_building_state(slot, building_state, also_change_state=True)
