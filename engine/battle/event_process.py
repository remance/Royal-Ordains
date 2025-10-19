import sys
from random import choice, randint

import pygame
from pygame.mixer import Sound

from engine.character.character import Character
from engine.stageobject.stageobject import StageObject


def event_process(self):
    for event_index, child_event in enumerate(self.cutscene_playing.copy()):
        # play child events until found one that need waiting
        event_property = child_event["Property"]
        if "story choice" in event_property:
            mission_choice_appear = event_property["story choice"].split("_")[0]
        if "story choice" not in event_property or event_property["story choice"] == mission_choice_appear + "_" + \
                self.main_story_profile["story choice"][mission_choice_appear]:
            # skip event that not in story path
            if child_event["Object"] == "camera":
                if child_event["Type"] == "move" and "POS" in event_property:
                    camera_pos_target = event_property["POS"]
                    camera_speed = 400
                    if "speed" in event_property:
                        camera_speed = event_property["speed"]
                    if self.camera_pos[0] != camera_pos_target:
                        if self.camera_pos[0] < camera_pos_target:
                            self.camera_pos[0] += camera_speed * self.true_dt
                            if self.camera_pos[0] > camera_pos_target:
                                self.camera_pos[0] = camera_pos_target
                        else:
                            self.camera_pos[0] -= camera_speed * self.true_dt
                            if self.camera_pos[0] < camera_pos_target:
                                self.camera_pos[0] = camera_pos_target
                    else:  # reach target
                        self.cutscene_playing.remove(child_event)
                elif child_event["Type"] == "cutscene":
                    if child_event["Animation"] == "blackout":
                        if not self.cutscene_in_progress:
                            self.cutscene_in_progress = True
                            text = None
                            if child_event["Text ID"]:
                                text = self.localisation.grab_text(
                                    ("event", child_event["Text ID"], "Text"))
                            use_font_texture = None
                            if "font texture" in child_event["Property"]:
                                use_font_texture = child_event["Property"]["font texture"]
                            instant_fade = False
                            if "instant fade" in child_event["Property"]:
                                instant_fade = child_event["Property"]["instant fade"]
                            text_delay = False
                            if "timer" in child_event["Property"]:
                                text_delay = child_event["Property"]["timer"]
                            text_fade_in = False
                            if "text fade in" in child_event["Property"]:
                                text_fade_in = child_event["Property"]["text fade in"]
                            fade_out = True
                            if "no auto fade out" in event_property:
                                fade_out = False
                            speed = 1
                            if "speed" in event_property:
                                speed = child_event["Property"]["speed"]
                            self.screen_fade.reset(text=text, font_texture=use_font_texture,
                                                   instant_fade=instant_fade, text_fade_in=text_fade_in,
                                                   text_delay=text_delay, fade_speed=speed, fade_out=fade_out)
                            self.battle_outer_ui_updater.add(self.screen_fade)
                        else:
                            if self.screen_fade.done:
                                if "no auto fade out" not in event_property:
                                    self.screen_fade.reset()
                                    self.battle_outer_ui_updater.remove(self.screen_fade)
                                self.cutscene_in_progress = False
                                self.cutscene_playing.remove(child_event)
                    elif child_event["Animation"] == "wait":
                        if self.cutscene_in_progress is False:
                            self.cutscene_in_progress = event_property["timer"]  # must have timer property
                        else:
                            self.cutscene_in_progress -= self.true_dt
                            if self.cutscene_in_progress < 0:
                                self.cutscene_in_progress = False
                                self.cutscene_playing.remove(child_event)

            elif child_event["Object"] == "battle":
                if child_event["Type"] == "end":  # end battle, go to menu
                    return False

            elif child_event["Object"] == "game":
                if child_event["Type"] == "end":  # end game entirely
                    pygame.quit()
                    sys.exit()

            elif "bgchange" in child_event["Type"]:
                pos = 1
                if "POS" in event_property:
                    pos = event_property["POS"]
                if child_event["Object"] != "remove":
                    self.scene.data[pos] = child_event["Object"]
                else:
                    self.scene.data[pos] = self.empty_scene_image
                x = (pos - 1) * self.scene.data[pos].get_width()
                rect = self.scene.data[pos].get_rect(topleft=(x, 0))
                self.scene.full_scene_image.blit(self.scene.data[pos], rect)
                self.cutscene_playing.remove(child_event)

            elif "bgfade" in child_event["Type"]:
                self.scene.fade_start = True
                self.scene.fade_in = False
                self.scene.fade_out = False
                if "fadein" in child_event["Type"]:
                    self.scene.alpha = 0
                    self.scene.fade_in = True
                elif "fadeout" in child_event["Type"]:
                    self.scene.alpha = 255
                    self.scene.fade_out = True

                self.scene.fade_speed = 1
                self.scene.fade_delay = 0
                if "speed" in event_property:
                    self.scene.fade_speed = event_property["speed"]
                if "timer" in event_property:
                    self.scene.fade_delay = event_property["timer"]
                self.cutscene_playing.remove(child_event)

            elif child_event["Type"] == "music":  # play new music
                if str(child_event["Object"]).lower() == "none":
                    self.current_music = None
                    self.music_left.stop()
                    self.music_right.stop()
                elif str(child_event["Object"]).lower() == "pause":
                    self.current_music = None  # remove current music so when game unpause it not replace event
                    self.music_left.pause()
                    self.music_right.pause()
                elif str(child_event["Object"]).lower() == "resume":
                    self.current_music = 1
                    self.music_left.unpause()
                    self.music_right.unpause()
                else:
                    self.current_music = self.stage_music_pool[str(child_event["Object"])]
                    self.music_left.play(self.current_music, loops=-1, fade_ms=100)
                    self.music_right.play(self.current_music, loops=-1, fade_ms=100)
                    self.music_left.set_volume(self.play_music_volume, 0)
                    self.music_right.set_volume(0, self.play_music_volume)
                self.cutscene_playing.remove(child_event)

            elif child_event["Type"] == "ambient":  # play new ambient
                if str(child_event["Object"]).lower() == "none":
                    self.current_ambient = None
                    self.ambient.stop()
                elif str(child_event["Object"]).lower() == "pause":
                    self.current_ambient = None  # remove current ambient so when game unpause it not replace event
                    self.ambient.pause()
                elif str(child_event["Object"]).lower() == "resume":
                    self.current_ambient = 1
                    self.ambient.unpause()
                else:
                    self.current_ambient = Sound(self.ambient_pool[str(child_event["Object"])])
                    self.ambient.play(self.current_ambient, loops=-1, fade_ms=100)
                    self.ambient.set_volume(self.play_effect_volume)
                self.cutscene_playing.remove(child_event)

            elif child_event["Type"] == "sound":  # play sound
                self.add_sound_effect_queue(choice(self.sound_effect_pool[str(child_event["Object"])]),
                                            self.camera_pos, child_event["Property"]["sound distance"],
                                            child_event["Property"]["shake value"])
                self.cutscene_playing.remove(child_event)

            elif child_event["Type"] == "weather":  # play weather
                # change weather
                weather_strength = 0
                if "strength" in child_event["Property"]:
                    weather_strength = child_event["Property"]["strength"]
                self.current_weather.__init__(child_event["Object"], randint(0, 359),
                                              weather_strength)
                self.cutscene_playing.remove(child_event)

            else:
                if child_event["Type"] == "create":  # add character for cutscene
                    game_id = child_event["Object"]
                    layer_id = event_index
                    if "Game ID" in event_property:
                        game_id = event_property["Game ID"]
                    if "Layer ID" in event_property:
                        layer_id = event_property["Layer ID"]
                    Character(game_id, layer_id,
                              event_property | self.character_data.character_list[
                                  child_event["Object"]] |
                              {"ID": child_event["Object"],
                               "Ground Y POS": event_property["POS"][1],
                               "Scene": 1, "Team": 1, "Arrive Condition": {}})
                    self.cutscene_playing.remove(child_event)
                elif child_event["Type"] == "place":  # place scene object
                    angle = None
                    if "angle" in event_property:
                        angle = event_property["angle"]
                    animation_speed = 0.1
                    if "speed" in event_property:
                        animation_speed = event_property["speed"]
                    flip = 0
                    if "flip" in event_property:
                        flip = 1
                    StageObject(child_event["Object"], event_property["POS"], child_event["Object"],
                                angle, flip, animation_speed=animation_speed)
                    self.cutscene_playing.remove(child_event)
                elif child_event["Type"] == "delete":  # delete specified scene object
                    for item in self.stage_objects:
                        if item.game_id == child_event["Object"]:
                            item.kill()
                    self.cutscene_playing.remove(child_event)
                else:
                    event_character = None
                    if child_event["Object"] == "pm":  # main player
                        event_character = self.main_player_object
                    else:
                        for character in self.all_characters:
                            if character.game_id == child_event["Object"]:
                                event_character = character
                                break
                    if event_character:
                        event_character.character_event_process(child_event, event_property)
                    else:  # no character to play for this cutscene, no need to loop this child event further
                        self.cutscene_playing.remove(child_event)

            if "select" in event_property:
                if event_property["select"] == "yesno":
                    if self.decision_select not in self.battle_outer_ui_updater:
                        self.battle_outer_ui_updater.add(self.decision_select)

            if "wait" in event_property or "interact" in event_property or \
                    "select" in event_property:
                break
        elif "story choice" in event_property:  # remove child event that is not in story path
            self.cutscene_playing.remove(child_event)

    end_battle_specific_mission = self.player_input_cutscene()
    return end_battle_specific_mission
