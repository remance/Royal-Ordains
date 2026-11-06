from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game.game import Game


def convert_custom_army_to_deployable(self: Game, army_dict: dict, culture_id: str):
    deployable_army_dict = {"culture": culture_id, "commander": army_dict["Commander"],
                            "followers": {"leader": [], "troop": [], "air": []},
                            "cost": 0, "supply": 0, "leadership": 0}
    for header in ("Leader 1", "Leader 2", "Leader 3", "Troop 1", "Troop 2", "Troop 3", "Troop 4", "Troop 5",
                   "Air 1", "Air 2", "Air 3", "Air 4", "Air 5"):
        character = army_dict[header]
        if character:
            if type(character) is list:
                deployable_army_dict["followers"][header.split(" ")[0].lower()].append(character)
            else:
                deployable_army_dict["followers"][header.split(" ")[0].lower()].append([character, True])
    return deployable_army_dict
