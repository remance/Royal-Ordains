from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand


def add_or_remove_technology(self: Grand, region_id: str, technology_id: str,
                             remove: bool = False):  # TODO add tech effect
    if remove:
        self.current_campaign_state["region"][region_id]["technology"].remove(technology_id)
    else:
        self.current_campaign_state["region"][region_id]["technology"].append(technology_id)
