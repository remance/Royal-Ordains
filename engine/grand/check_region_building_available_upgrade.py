from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand


def check_region_building_available_upgrade(self: Grand, faction_id: str, region_id: str, building_id_to_check: str):
    building_list = self.building_list
    region_buildings = self.current_campaign_state["region"][region_id]["building"]

    # building is active if it is not damaged, in progress, all requirement buildings are active
    region_active_building = [item[0] for item in region_buildings if item[1] and not item[2] and item[3]]

    exist_building_upgrade = self.building_upgrade_list[building_id_to_check]
    faction_cultures_state = self.current_campaign_state["faction"][faction_id]["culture"]

    available_building_upgrade_by_type = {}
    all_available_building_upgrade = []
    for building, requirement in exist_building_upgrade.items():
        this_building_stat = building_list[building]
        building_type = this_building_stat["Type"]
        if (this_building_stat["Culture"] in faction_cultures_state and
                faction_cultures_state[this_building_stat["Culture"]]["policy"] != "reject"):
            can_build = True
            for require_buildings in requirement:
                if all([require_building not in region_active_building for require_building in require_buildings]):
                    # required building condition not met
                    can_build = False
                    break
            if can_build:
                if building_type not in available_building_upgrade_by_type:
                    available_building_upgrade_by_type[building_type] = {}

                available_building_upgrade_by_type[building_type][building] = True
                all_available_building_upgrade.append(building)

    return available_building_upgrade_by_type, all_available_building_upgrade
