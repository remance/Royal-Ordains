from types import MethodType
from random import uniform

from pygame import Vector2

from engine.uibattle.uibattle import CharacterSpeechBox

infinity = float("inf")


def character_event_process(self, event, event_property):
    from engine.character.character import Character

    if event["Type"] == "hide":
        self.battle.battle_camera.remove(self.body_parts.values())
        if self.indicator:  # also hide indicator
            self.battle.battle_camera.remove(self.indicator)
        self.cutscene_update = MethodType(Character.inactive_update, self)
        self.battle.cutscene_playing.remove(event)
    if event["Type"] == "speak":  # speak something
        CharacterSpeechBox(self, self.battle.localisation.grab_text(("event",
                                                                     event["Text ID"],
                                                                     "Text")))
    elif event["Type"] == "animation":  # play specific animation
        self.command_action = event_property
    elif event["Type"] == "remove":
        self.die(delete=True)
        self.battle.cutscene_playing.remove(event)
    elif event["Type"] == "unlock":  # unlock AI via event
        self.ai_lock = False
        self.event_ai_lock = False
        self.battle.cutscene_playing.remove(event)
    elif event["Type"] == "lock":  # lock AI via event
        self.event_ai_lock = True
        self.ai_lock = True
        self.battle.cutscene_playing.remove(event)
    elif (not self.cutscene_event or (("hold" in self.current_action or "repeat" in self.current_action) and
                                      self.cutscene_event != event)):
        # replace previous event on hold or repeat when there is new one to play next
        if "hold" in self.current_action and self.cutscene_event in self.battle.cutscene_playing:
            # previous event done
            self.battle.cutscene_playing.remove(self.cutscene_event)

        self.cutscene_event = event
        if "POS" in event_property:
            if type(event_property["POS"]) is str:
                target_scene = self.battle.battle_stage.current_scene
                if "reach_" in event_property["POS"]:
                    target_scene = self.battle.battle_stage.reach_scene

                if "start" in event_property["POS"]:
                    positioning = self.layer_id
                    if self.layer_id > 4:
                        positioning = uniform(1, 4)
                    ground_pos = self.ground_pos
                    if self.fly:  # flying character can just move with current y pos
                        ground_pos = self.base_pos[1]
                    self.cutscene_target_pos = Vector2(
                        (1920 * target_scene) + (100 * positioning), ground_pos)
                elif "middle" in event_property["POS"]:
                    ground_pos = self.ground_pos
                    if self.fly:  # flying character can just move with current y pos
                        ground_pos = self.base_pos[1]
                    self.cutscene_target_pos = Vector2(
                        (1920 * target_scene) - (self.battle.battle_camera_center[0] * 1.5),
                        ground_pos)
                elif "center" in event_property["POS"]:
                    # true center, regardless of flying
                    self.cutscene_target_pos = Vector2(
                        (1920 * target_scene) - (self.battle.battle_camera_center[0] * 1.5),
                        self.battle.battle_camera_center[1])
            else:
                self.cutscene_target_pos = Vector2(
                    event_property["POS"][0],
                    event_property["POS"][1])
        elif "target" in event_property:
            for character2 in self.battle.all_chars:
                if character2.game_id == event_property["target"]:  # go to target pos
                    self.cutscene_target_pos = character2.base_pos
                    break
        if "angle" in event_property:
            if event_property["angle"] == "target":
                # facing target must have cutscene_target_pos
                if self.cutscene_target_pos[0] >= self.base_pos[0]:
                    self.new_angle = -90
                else:
                    self.new_angle = 90
            else:
                self.new_angle = int(event_property["angle"])
            self.rotate_logic()
        animation = event["Animation"]
        action_dict = {}
        if animation:
            action_dict = {"name": event["Animation"]} | event_property
        if action_dict and action_dict != self.current_action:  # start new action
            self.pick_cutscene_animation(action_dict)
        if event["Text ID"]:
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
                if self.angle != event_property["angle"]:  # player face target
                    self.new_angle *= -1
                    self.rotate_logic()

            CharacterSpeechBox(self,
                               self.battle.localisation.grab_text(("event", event["Text ID"], "Text")),
                               specific_timer=specific_timer,
                               player_input_indicator=player_input_indicator,
                               cutscene_event=event)
