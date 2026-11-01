from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand

from engine.constants import Diplomacy_Speech_Priority


def add_diplomacy_talk_queue(self: Grand, character, speech_id):
    speech = (character, speech_id, Diplomacy_Speech_Priority[speech_id])
    if speech not in self.diplomacy_head_talk_queue:
        self.diplomacy_head_talk_queue.append(speech)

        self.diplomacy_head_talk_queue.sort(key=lambda x: x[2], reverse=True)  # sort by priority

        if len(self.diplomacy_head_talk_queue) > 10:  # keep only first 10 items
            self.diplomacy_head_talk_queue = self.diplomacy_head_talk_queue[10:]
