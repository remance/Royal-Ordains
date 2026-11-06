from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.grand.grand import Grand


def sort_dot_army_occupation(self: Grand, base_pos: tuple):
    self.dots_army_occupation[base_pos].sort(key=lambda x: x.power, reverse=True)
