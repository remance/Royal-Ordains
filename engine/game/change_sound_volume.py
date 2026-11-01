from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game.game import Game

from pygame.mixer import music


def change_sound_volume(self: Game):
    config = self.config
    self.master_volume = float(config["USER"]["master_volume"])

    self.music_volume = float(config["USER"]["music_volume"])
    self.play_music_volume = self.master_volume * self.music_volume / 10000
    self.effect_volume = float(config["USER"]["effect_volume"])
    self.play_effect_volume = self.master_volume * self.effect_volume / 10000
    self.voice_volume = float(config["USER"]["voice_volume"])
    self.play_voice_volume = self.master_volume * self.voice_volume / 10000

    music.set_volume(self.play_music_volume)  # set new music player volume

    volume_stat = {"master": self.master_volume, "music": self.music_volume,
                   "effect": self.effect_volume, "voice": self.voice_volume}

    for main_process in (self.battle, self.grand):
        main_process.music_channel.set_volume(self.play_music_volume)
        main_process.button_sound_channel.set_volume(self.play_effect_volume)
        main_process.ambient_channel.set_volume(self.play_effect_volume)
        main_process.weather_ambient_channel.set_volume(self.play_effect_volume)

        main_process.master_volume = self.master_volume
        main_process.play_music_volume = self.play_music_volume
        main_process.play_effect_volume = self.play_effect_volume
        main_process.play_voice_volume = self.play_voice_volume

        for key, value in self.option_menu_sliders.items():  # re-update volume slider
            value.player_input(forced_value=volume_stat[key])
            main_process.esc_slider_menu[key].player_input(forced_value=volume_stat[key])
