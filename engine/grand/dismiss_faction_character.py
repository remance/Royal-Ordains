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
        for index, slot in enumerate(army.army_followers[character_state[1]]):
            if character_id in slot:
                army.change_follower(character_state[1], index, None)
                break

    faction_state["character"].pop(character_id)

    self.current_campaign_state["free_character"].append(character_id)
