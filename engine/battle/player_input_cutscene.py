from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle.battle import Battle


def player_input_cutscene(self: Battle):
    # cutscene that need main player to press button to continue
    for key, pressed in self.player_key_press.items():
        if key == "Confirm" and pressed:
            for child_event in self.cutscene_playing.copy():
                if "wait" in child_event["Property"]:  # has event that still requires finishing before events after
                    break

                elif "interact" in child_event["Property"]:
                    self.end_cutscene_event(child_event)
                    break  # only one player interact event can be played at a time
