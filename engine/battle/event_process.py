from types import MethodType
from random import uniform

from pygame import Vector2

from engine.character.character import Character, AICharacter
from engine.uibattle.uibattle import CharacterSpeechBox

infinity = float("inf")


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
                else:
                    if child_event["Object"] == "pm":  # main player
                        event_character = self.main_player_object
                    else:
                        for character in self.all_chars:
                            if character.game_id == child_event["Object"]:
                                event_character = character
                                break
                    if event_character:
                        if child_event["Type"] == "hide":
                            self.battle_camera.remove(event_character.body_parts.values())
                            if event_character.indicator:  # also hide indicator
                                self.battle_camera.remove(event_character.indicator)
                            event_character.cutscene_update = MethodType(Character.inactive_update, event_character)
                            self.cutscene_playing.remove(child_event)
                        elif child_event["Type"] == "remove":
                            event_character.die(delete=True)
                            self.cutscene_playing.remove(child_event)
                        elif (not event_character.cutscene_event or
                              (("hold" in event_character.current_action or
                                "repeat" in event_character.current_action) and
                               event_character.cutscene_event != child_event)):
                            # replace previous event on hold or repeat when there is new one to play next
                            if "hold" in event_character.current_action and \
                                    event_character.cutscene_event in self.cutscene_playing:
                                # previous event done
                                self.cutscene_playing.remove(event_character.cutscene_event)

                            event_character.cutscene_event = child_event
                            if "POS" in event_property:
                                if type(event_property["POS"]) is str:
                                    target_scene = self.battle_stage.current_scene
                                    if "reach_" in event_property["POS"]:
                                        target_scene = self.battle_stage.reach_scene

                                    if "start" in event_property["POS"]:
                                        positioning = event_character.layer_id
                                        if event_character.layer_id > 4:
                                            positioning = uniform(1, 4)
                                        ground_pos = event_character.ground_pos
                                        if event_character.fly:  # flying character can just move with current y pos
                                            ground_pos = event_character.base_pos[1]
                                        event_character.cutscene_target_pos = Vector2(
                                            (1920 * target_scene) + (100 * positioning), ground_pos)
                                    elif "middle" in event_property["POS"]:
                                        ground_pos = event_character.ground_pos
                                        if event_character.fly:  # flying character can just move with current y pos
                                            ground_pos = event_character.base_pos[1]
                                        event_character.cutscene_target_pos = Vector2(
                                            (1920 * target_scene) - (self.battle_camera_center[0] * 1.5),
                                            ground_pos)
                                    elif "center" in event_property["POS"]:
                                        # true center, regardless of flying
                                        event_character.cutscene_target_pos = Vector2(
                                            (1920 * target_scene) - (self.battle_camera_center[0] * 1.5),
                                            self.battle_camera_center[1])
                                else:
                                    event_character.cutscene_target_pos = Vector2(
                                        event_property["POS"][0],
                                        event_property["POS"][1])
                            elif "target" in event_property:
                                for character2 in self.all_chars:
                                    if character2.game_id == event_property[
                                        "target"]:  # go to target pos
                                        event_character.cutscene_target_pos = character2.base_pos
                                        break
                            if "angle" in event_property:
                                if event_property["angle"] == "target":
                                    # facing target must have cutscene_target_pos
                                    if event_character.cutscene_target_pos[0] >= event_character.base_pos[
                                        0]:
                                        event_character.new_angle = -90
                                    else:
                                        event_character.new_angle = 90
                                else:
                                    event_character.new_angle = int(event_property["angle"])
                                event_character.rotate_logic()
                            animation = child_event["Animation"]
                            action_dict = {}
                            if animation:
                                action_dict = {"name": child_event["Animation"]} | event_property
                            if action_dict and action_dict != event_character.current_action:  # start new action
                                event_character.pick_cutscene_animation(action_dict)
                            if child_event["Text ID"]:
                                specific_timer = None
                                player_input_indicator = None
                                if "interact" in event_property:
                                    specific_timer = infinity
                                    player_input_indicator = True
                                elif "timer" in event_property:
                                    specific_timer = event_property
                                elif "select" in event_property or \
                                        "hold" in event_property:
                                    # selecting event, also infinite timer but not add player input indication
                                    specific_timer = infinity

                                if "angle" in event_property:
                                    if event_character.angle != event_property["angle"]:  # player face target
                                        event_character.new_angle *= -1
                                        event_character.rotate_logic()

                                CharacterSpeechBox(event_character,
                                                   self.localisation.grab_text(("event",
                                                                                child_event["Text ID"],
                                                                                "Text")),
                                                   specific_timer=specific_timer,
                                                   player_input_indicator=player_input_indicator,
                                                   cutscene_event=child_event)
                    else:
                        # no character to play for this cutscene, no need to loop this child event further
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
