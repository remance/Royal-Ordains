from random import choice, randint

from engine.character.character import AICharacter


def event_process(self):
    for event_index, child_event in enumerate(self.cutscene_playing.copy()):
        # play child events until found one that need waiting
        event_property = child_event["Property"]
        if "story choice" in event_property:
            mission_choice_appear = event_property["story choice"].split("_")[0]
        if "story choice" not in event_property or event_property["story choice"] == mission_choice_appear + "_" + self.main_story_profile["story choice"][mission_choice_appear]:
            # skip event that not in story path
            if child_event["Object"] == "camera":
                if child_event["Type"] == "move" and "POS" in event_property:
                    camera_pos_target = self.stage_end_list[event_property["POS"]]
                    camera_speed = 400
                    if "speed" in event_property:
                        camera_speed = event_property["speed"]
                    if self.camera_pos[0] != camera_pos_target:
                        if self.camera_pos[0] < camera_pos_target:
                            self.camera_pos[0] += camera_speed * self.dt
                            if self.camera_pos[0] > camera_pos_target:
                                self.camera_pos[0] = camera_pos_target
                        else:
                            self.camera_pos[0] -= camera_speed * self.dt
                            if self.camera_pos[0] < camera_pos_target:
                                self.camera_pos[0] = camera_pos_target
                    else:  # reach target
                        self.cutscene_playing.remove(child_event)
                elif child_event["Type"] == "cutscene":
                    if child_event["Animation"] == "blackout":
                        if not self.cutscene_timer:
                            self.cutscene_timer = 1
                            text = None
                            if child_event["Text ID"]:
                                text = self.localisation.grab_text(
                                    ("event", child_event["Text ID"], "Text"))
                            self.screen_fade.reset(1, text=text)
                            self.realtime_ui_updater.add(self.screen_fade)
                            if "timer" in event_property:
                                self.cutscene_timer = event_property["timer"]
                        else:
                            if self.cutscene_timer and self.screen_fade.alpha == 255:
                                # count down timer after finish fading
                                self.cutscene_timer -= self.true_dt
                                if self.cutscene_timer < 0:
                                    self.screen_fade.reset(1)
                                    self.realtime_ui_updater.remove(self.screen_fade)
                                    self.cutscene_timer = 0
                                    self.cutscene_playing.remove(child_event)
            else:
                event_character = None
                if child_event["Type"] == "create":  # add character for cutscene
                    AICharacter(child_event["Object"], event_index,
                                event_property | self.character_data.character_list[
                                    child_event["Object"]] |
                                {"ID": child_event["Object"],
                                 "Ground Y POS": event_property["POS"][1],
                                 "Scene": 1, "Team": 1, "Arrive Condition": {}, "Sprite Ver": self.chapter})
                    self.cutscene_playing.remove(child_event)
                elif child_event["Type"] == "music":  # play new music
                    self.current_music = self.stage_music_pool[str(child_event["Object"])]
                    self.music_left.play(self.current_music, fade_ms=100)
                    self.music_left.set_volume(self.play_music_volume, 0)
                    self.music_right.play(self.current_music, fade_ms=100)
                    self.music_right.set_volume(0, self.play_music_volume)
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
                                                  weather_strength,
                                                  self.weather_data)
                    self.cutscene_playing.remove(child_event)

                else:
                    if child_event["Object"] == "pm":  # main player
                        event_character = self.main_player_object
                    else:
                        for character in self.all_chars:
                            if character.game_id == child_event["Object"]:
                                event_character = character
                                break
                    if event_character:
                        event_character.character_event_process(child_event, event_property)
                    else:  # no character to play for this cutscene, no need to loop this child event further
                        self.cutscene_playing.remove(child_event)
            if "select" in event_property:
                if event_property["select"] == "yesno":
                    self.realtime_ui_updater.add(self.decision_select)

            elif "shop" in event_property:  # open shop interface
                self.change_game_state("shop")
                shop_npc = None
                for char in self.all_chars:
                    if char.game_id == child_event["Object"] or \
                            (child_event["Object"] == "pm" and char == self.main_player_object):
                        shop_npc = char
                        break

                for player in self.player_objects:
                    self.player_char_interfaces[player].shop_list = \
                        [key for key, value in self.character_data.shop_list.items() if
                         value["Shop"] == shop_npc.char_id and
                         (int(self.main_story_profile["chapter"]) > value["Chapter"] or
                          (int(self.main_story_profile["chapter"]) == value["Chapter"] and
                           int(self.main_story_profile["mission"]) >= value["Mission"]))]
                    self.player_char_interfaces[player].purchase_list = {}
                    self.player_char_interfaces[player].change_mode("shop")
                    self.player_char_interfaces[player].input_delay = 0.1
                    self.add_ui_updater(self.player_char_base_interfaces[player],
                                        self.player_char_interfaces[player])
                self.end_cutscene_event(child_event)

            elif "enchant" in event_property:  # open shop interface
                self.change_game_state("enchant")

                for player in self.player_objects:
                    self.player_char_interfaces[player].all_custom_item = \
                        [item for item in self.player_char_interfaces[player].profile["storage"] if
                         type(item) is tuple]
                    self.player_char_interfaces[player].change_mode("enchant")
                    self.player_char_interfaces[player].input_delay = 0.1
                    self.add_ui_updater(self.player_char_base_interfaces[player],
                                        self.player_char_interfaces[player])
                self.end_cutscene_event(child_event)

            if "wait" in event_property or "interact" in event_property or \
                    "select" in event_property:
                break
        elif "story choice" in event_property:  # remove child event that is not in story path
            self.cutscene_playing.remove(child_event)

    end_battle_specific_mission = self.cutscene_player_input()
    return end_battle_specific_mission
