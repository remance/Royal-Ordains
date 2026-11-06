from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.battle.battle import Battle
    from pygame import Sound

from pygame.mixer import find_channel


def play_sound_effect(self: Battle, sound: Sound, effect_volume: (tuple, list)):
    sound_effect_channel = find_channel()
    if sound_effect_channel:
        sound_effect_channel.set_volume(effect_volume[0], effect_volume[1])
        sound_effect_channel.play(sound)
