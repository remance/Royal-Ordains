from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand


def add_diplomacy_history_event(self: Grand, main_faction_id: str, event_faction_id: str, event_type: str,
                                value: int, turn: int):
    faction_behaviour = self.faction_list[main_faction_id]  # TODO add ai behaviour modifier
    self.current_campaign_state["faction"][main_faction_id]["diplomacy"][event_faction_id]["history"].append(
        [event_type, value, turn])
