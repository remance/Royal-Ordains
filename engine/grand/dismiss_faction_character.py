from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand


def dismiss_faction_character(self: Grand, faction_id: str, character_id: str):
    faction_state = self.current_campaign_state["faction"][faction_id]
    character_state = faction_state["character"][character_id]

    if character_state[0]:
        # in army, cannot dismiss commander
        army = character_state[0]
        army.remove_follower(character_state[1], character_state[0])

    faction_state["character"].pop(character_id)

    self.current_campaign_state["free_character"].append(character_id)
