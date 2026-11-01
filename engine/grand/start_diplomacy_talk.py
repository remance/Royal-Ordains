from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand


def start_diplomacy_talk(self: Grand):
    speech = self.diplomacy_head_talk_queue[0]
    self.diplomacy_head_ui.start_speak(speech[0], speech[1])
    self.diplomacy_head_talk_queue = self.diplomacy_head_talk_queue[1:]
