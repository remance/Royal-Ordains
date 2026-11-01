from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle.battle import Battle


def end_cutscene_event(self: Battle, child_event: dict):
    """End cutscene from interact or selection input"""
    # for char in self.all_battle_characters:
    #     if char.game_id == child_event["Object"] or \
    #             (child_event["Object"] == "pm" and char == self.main_player_object):
    #         if char.cutscene_event in self.cutscene_playing:
    #             # end any player_interact events currently awaiting
    #             self.cutscene_playing.remove(char.cutscene_event)
    #         if "repeat after" in char.current_action:
    #             char.current_action["repeat"] = True
    #         char.cutscene_event = None
    #         break

    for box in self.speech_boxes:
        if box.cutscene_event == child_event:  # end speech box related to the event
            box.timer = 0
