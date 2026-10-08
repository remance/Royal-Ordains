from copy import deepcopy

from pygame.mixer import Sound


def check_event(self):
    if self.event_list:
        event_list = self.event_list
        # check for event with camera reaching
        for key in event_list:
            if self.battle_time >= key:
                if "weather" in event_list[key]:
                    # change weather
                    self.current_weather.__init__(
                        event_list[key]["weather"][0],
                        event_list[key]["weather"][1],
                        event_list[key]["weather"][2])
                    event_list[key].pop("weather")
                if "music" in event_list[key]:  # change music
                    self.current_music = None
                    if event_list[key]["music"] != "none":
                        self.current_music = Sound(self.stage_music_pool[
                                                       event_list[key]["music"]])
                        self.music_channel.set_volume(self.play_music_volume)
                        self.music_channel.play(self.current_music, loops=-1, fade_ms=100)
                    else:  # stop music
                        self.music_channel.set_volume(0)
                        self.music_channel.stop()
                    event_list[key].pop("music")
                if "ambient" in event_list[key]:  # change ambient
                    self.current_ambient = None
                    if event_list[key]["ambient"] != "none":
                        self.current_ambient = Sound(self.ambient_pool[
                                                         event_list[key][
                                                             "ambient"]])
                    if self.current_ambient:
                        self.ambient_channel.set_volume(self.play_effect_volume)
                        self.ambient_channel.play(self.current_ambient, loops=-1, fade_ms=100)
                    else:  # stop ambient
                        self.ambient_channel.set_volume(0)
                        self.ambient_channel.stop()
                    event_list[key].pop("ambient")
                if "sound" in event_list[key]:  # play sound
                    for sound_effect in event_list[key]["sound"]:
                        self.add_sound_effect_queue(sound_effect[0],
                                                    self.base_camera_center_pos, sound_effect[1], sound_effect[2])
                    event_list[key].pop("sound")
                if "cutscene" in event_list[key]:  # cutscene
                    self.cutscene_finish_camera_delay = 1
                    for parent_event in event_list[key]["cutscene"]:
                        # play one parent at a time
                        self.cutscene_playing = parent_event
                        self.cutscene_playing_data = deepcopy(parent_event)
                        if "replayable" not in parent_event[0]["Property"]:
                            event_list[key].pop("cutscene")
                if not event_list[key]:  # no more event left
                    event_list.pop(key)

                break

    if self.player_interact_event_list:  # event that require player interaction (talk)
        event_list = self.player_interact_event_list
        for item in event_list:
            if self.player_key_press[self.main_player]["Confirm"]:  # player interact, start event
                self.speech_prompt.clear()  # remove prompt

                self.cutscene_playing = deepcopy(self.player_interact_event_list[item[0]][0])
                self.cutscene_playing_data = self.player_interact_event_list[item[0]][0]
                break
