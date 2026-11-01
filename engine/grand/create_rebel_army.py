from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from uuid import uuid4
from random import choice, uniform


def create_rebel_army(self: Grand, region_id: str, faction_state: dict, max_spawn_power: float):
    """Create and deploy a random rebel army"""
    current_campaign_state = self.current_campaign_state
    campaign_faction_state = current_campaign_state["faction"]
    campaign_region_state = current_campaign_state["region"]
    region_state = campaign_region_state[region_id]
    character_list = self.character_list

    culture = tuple(faction_state["culture"].keys())[0]
    region_culture = region_state["culture"]

    if region_culture:
        culture = choice(tuple(region_culture.keys()))
    culture_character_list = self.custom_character_setup[culture]
    # create rebel army preset
    rebel_army = {"ID": str(uuid4()), "Faction": "free", "Region": region_id, "Commander": None,
                  "Leader 1": None, "Leader 2": None, "Leader 3": None, "Troop 1": None,
                  "Troop 2": None, "Troop 3": None, "Troop 4": None, "Troop 5": None,
                  "Air 1": None, "Air 2": None, "Air 3": None, "Air 4": None, "Air 5": None,
                  "Supply": 0, "Max Supply": 0}

    if current_campaign_state["free_character"] and uniform(0, 100) < 10:
        # 10% chance to use free hero as commander
        picked_character = choice(current_campaign_state["free_character"])
        if not character_list[picked_character]["No Commander"]:
            rebel_army["Commander"] = choice(current_campaign_state["free_character"])
    if not rebel_army["Commander"]:
        rebel_army["Commander"] = choice(culture_character_list["leader"]["generic"])

    cache_available_list = {}
    for header in ("Leader 1", "Leader 2", "Leader 3", "Troop 1", "Troop 2", "Troop 3",
                   "Troop 4", "Troop 5", "Air 1", "Air 2", "Air 3", "Air 4", "Air 5"):
        header_split = header.split(" ")
        if uniform(0, 100) < 100 / (int(header_split[-1]) + 1):
            header_type = header_split[0].lower()
            if header_type == "leader":
                rebel_army[header] = choice(culture_character_list["leader"]["generic"])
            else:
                if header_type not in cache_available_list:
                    cache_available_list[header_type] = [item for item in culture_character_list[header_type] if
                                                         character_list[item]["Power Score"] <= max_spawn_power]
                available_culture_character_list = cache_available_list[header_type]
                if available_culture_character_list:
                    rebel_army[header] = choice(available_culture_character_list)

            if rebel_army[header]:
                character_data = self.character_list[rebel_army[header]]
                rebel_army["Supply"] += character_data["Supply"] * character_data["Capacity"]

    rebel_army["Max Supply"] = rebel_army["Supply"]
    self.create_new_army(campaign_faction_state["free"], rebel_army, no_assemble=True, no_enemy_check=False)

    if self.player_faction == region_state["control"]:
        self.event_notification_ui.add_new_event((
            "event_bad", self.grab_text(("ui", "info_text_rebel_appear")) + self.grab_text(("region", region_id, "Name")),
            str(current_campaign_state["turn"]) + "." + str(current_campaign_state["phase"]), ()))
