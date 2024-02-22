import copy
import os
import sys
import time
from math import sin, cos, radians
from random import uniform, randint

import pygame
from pygame import Vector2, display, mouse
from pygame.locals import *

from engine.battle.setup.make_battle_ui import make_battle_ui
from engine.battle.setup.make_esc_menu import make_esc_menu
from engine.camera.camera import Camera
from engine.character.character import Character
from engine.drama.drama import TextDrama
from engine.effect.effect import Effect
from engine.stage.stage import Stage
from engine.stageobject.stageobject import StageObject
from engine.uibattle.uibattle import FPSCount, BattleCursor, YesNo, CharacterSpeechBox, CharacterInteractPrompt, CityMap
from engine.utils.common import clean_object, clean_group_object
from engine.utils.data_loading import load_image, load_images
from engine.utils.text_making import number_to_minus_or_plus
from engine.weather.weather import Weather

script_dir = os.path.split(os.path.abspath(__file__))[0] + "/"

infinity = float("inf")

decision_route = {"yes": "a", "no": "b"}


def set_start_load(self, what):  # For output asset loading time in terminal
    globals()['load_timer'] = time.time()
    self.game.loading_screen("Loading " + what)  # change loading screen to display progress
    return "Loading {0}... ".format(what)


def set_done_load():
    duration = time.time() - globals()['load_timer']
    return " DONE ({0}s)\n".format(duration)


class Battle:
    from engine.game.activate_input_popup import activate_input_popup
    activate_input_popup = activate_input_popup

    from engine.battle.add_sound_effect_queue import add_sound_effect_queue
    add_sound_effect_queue = add_sound_effect_queue

    from engine.battle.cal_shake_value import cal_shake_value
    cal_shake_value = cal_shake_value

    from engine.battle.camera_process import camera_process
    camera_process = camera_process

    from engine.game.change_pause_update import change_pause_update
    change_pause_update = change_pause_update

    from engine.battle.cutscene_player_input import cutscene_player_input
    cutscene_player_input = cutscene_player_input

    from engine.battle.fix_camera import fix_camera
    fix_camera = fix_camera

    from engine.battle.increase_player_score import increase_player_score
    increase_player_score = increase_player_score

    from engine.battle.play_sound_effect import play_sound_effect
    play_sound_effect = play_sound_effect

    from engine.battle.setup_battle_character import setup_battle_character
    setup_battle_character = setup_battle_character

    from engine.battle.shake_camera import shake_camera
    shake_camera = shake_camera

    from engine.battle.spawn_weather_matter import spawn_weather_matter
    spawn_weather_matter = spawn_weather_matter

    from engine.battle.escmenu_process import escmenu_process
    escmenu_process = escmenu_process

    from engine.lorebook.lorebook import lorebook_process
    lorebook_process = lorebook_process

    battle = None
    camera = None
    ui_updater = None
    ui_drawer = None
    screen = None
    battle_camera_size = None
    battle_camera_min = None
    battle_camera_max = None
    start_camera_mode = "Follow"

    base_fall_gravity = 900

    def __init__(self, game):
        self.game = game
        Battle.battle = self

        # TODO LIST for full chapter 1
        # finish city stage
        # add skill/moveset unlockable for enemy (charisma)
        # add enemy trap with delay and cycle
        # add one more playable char
        # add online/lan multiplayer?
        # add shop,
        # add quest system?
        # add ranking record system
        # add save/profile system (add story event finish check to save)
        # finish main menu
        # add choice story check
        # add dialogue log in save and esc
        # add victory scene in throne room that show reward from finished mission

        self.clock = pygame.time.Clock()  # Game clock to keep track of realtime pass

        self.config = game.config
        self.master_volume = game.master_volume
        self.music_volume = game.music_volume
        self.effect_volume = game.effect_volume
        self.voice_volume = game.voice_volume
        self.play_music_volume = game.play_music_volume
        self.play_effect_volume = game.play_effect_volume
        self.play_voice_volume = game.play_voice_volume
        self.joystick_bind_name = game.joystick_bind_name
        self.player_key_control = {player: self.config["USER"]["control player " + str(player)] for player in
                                   game.player_list}
        self.player_key_bind = {player: self.game.player_key_bind_list[player][self.player_key_control[player]] for
                                player in game.player_list}
        self.player_key_bind_name = {player: {value: key for key, value in self.player_key_bind[player].items()} for
                                     player in game.player_list}
        self.player_key_press = {player: {key: False for key in self.player_key_bind[player]} for player in
                                 game.player_list}
        self.player_key_hold = {player: {key: False for key in self.player_key_bind[player]} for player in
                                game.player_list}
        self.player_joystick = self.game.player_joystick
        self.joystick_player = self.game.joystick_player
        self.screen_rect = game.screen_rect
        self.corner_screen_width = game.corner_screen_width
        self.corner_screen_height = game.corner_screen_height

        Battle.battle_camera_size = (self.screen_rect.width, self.screen_rect.height)
        Battle.battle_camera_min = (self.screen_rect.width, 0)
        Battle.battle_camera_max = (self.screen_rect.width - 1, self.screen_rect.height - 1)
        self.battle_camera_center = (self.battle_camera_size[0] / 2, self.battle_camera_size[1] / 2)

        self.main_dir = game.main_dir
        self.data_dir = game.data_dir
        self.screen_scale = game.screen_scale
        self.battle_camera = game.battle_camera
        Battle.ui_updater = game.battle_ui_updater
        Battle.ui_drawer = game.battle_ui_drawer
        Battle.cursor_drawer = game.battle_cursor_drawer

        self.character_updater = game.character_updater
        self.all_chars = game.all_chars
        self.speech_boxes = game.speech_boxes
        self.all_damage_effects = game.all_damage_effects
        self.effect_updater = game.effect_updater
        self.realtime_ui_updater = game.realtime_ui_updater

        self.cursor = game.cursor
        self.joysticks = game.joysticks
        self.joystick_name = game.joystick_name

        self.button_ui = game.button_ui

        self.stage_translation_text_popup = game.stage_translation_text_popup

        self.input_box = game.input_box
        self.input_ui = game.input_ui
        self.input_ok_button = game.input_ok_button
        self.input_cancel_button = game.input_cancel_button
        self.input_ui_popup = game.input_ui_popup
        self.confirm_ui_popup = game.confirm_ui_popup
        self.all_input_ui_popup = game.all_input_ui_popup

        self.weather_matters = game.weather_matters
        self.weather_effect = game.weather_effect

        self.lorebook = game.lorebook
        self.lore_name_list = game.lore_name_list
        self.filter_tag_list = game.filter_tag_list
        self.lore_buttons = game.lore_buttons
        self.subsection_name = game.subsection_name
        self.tag_filter_name = game.tag_filter_name

        self.lorebook_stuff = game.lorebook_stuff

        self.music_pool = game.music_pool
        self.sound_effect_pool = game.sound_effect_pool
        self.sound_effect_queue = {}

        self.weather_screen_adjust = self.screen_rect.width / self.screen_rect.height  # for weather sprite spawn position
        self.right_corner = self.screen_rect.width - (5 * self.screen_scale[0])
        self.bottom_corner = self.screen_rect.height - (5 * self.screen_scale[1])

        self.character_data = self.game.character_data
        self.battle_map_data = self.game.battle_map_data
        self.weather_data = self.battle_map_data.weather_data
        self.weather_matter_images = self.battle_map_data.weather_matter_images
        self.weather_list = self.battle_map_data.weather_list
        self.character_animation_data = self.game.character_animation_data
        self.body_sprite_pool = self.game.body_sprite_pool
        self.effect_animation_pool = self.game.effect_animation_pool
        self.language = self.game.language
        self.localisation = self.game.localisation
        self.save_data = game.save_data
        self.main_story_profile = {}
        self.all_story_profiles = {1: None, 2: None, 3: None, 4: None}
        self.player_char_interfaces = game.player_char_interfaces

        self.game_speed = 1
        self.all_team_character = {1: pygame.sprite.Group(), 2: pygame.sprite.Group(),
                                   3: pygame.sprite.Group(), 4: pygame.sprite.Group()}
        self.all_team_enemy = {1: pygame.sprite.Group(), 2: pygame.sprite.Group(),
                               3: pygame.sprite.Group(), 4: pygame.sprite.Group()}
        self.all_team_enemy_part = {1: pygame.sprite.Group(), 2: pygame.sprite.Group(),
                                    3: pygame.sprite.Group(), 4: pygame.sprite.Group()}
        self.all_team_drop = {1: pygame.sprite.Group(), 2: pygame.sprite.Group(),
                              3: pygame.sprite.Group(), 4: pygame.sprite.Group()}
        self.player_damage = {1: 0, 2: 0, 3: 0, 4: 0}
        self.player_kill = {1: 0, 2: 0, 3: 0, 4: 0}
        self.player_boss_kill = {1: 0, 2: 0, 3: 0, 4: 0}
        self.play_time = 0
        self.stage_gold = 0
        self.stage_score = 0
        self.last_resurrect_stage_score = 5000
        self.reserve_resurrect_stage_score = 0

        self.players = {}  # player
        self.player_objects = {}
        self.players_control_input = {1: None, 2: None, 3: None, 4: None}
        self.existing_playable_characters = []
        self.later_enemy = {}
        self.city_mode = False
        self.esc_menu_mode = "menu"

        self.helper = None  # helper character that can be moved via cursor
        self.score_board = None

        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, self.game.window_style,
                                                 32)  # Set the display mode
        Battle.screen = pygame.display.set_mode(self.screen_rect.size, self.game.window_style,
                                                self.best_depth)  # set up self screen

        # Assign battle variable to some classes
        Character.sound_effect_pool = self.sound_effect_pool
        Effect.sound_effect_pool = self.sound_effect_pool

        # Create battle ui
        cursor_images = load_images(self.data_dir, subfolder=("ui", "cursor_battle"))  # no need to scale cursor
        self.main_player_battle_cursor = BattleCursor(cursor_images, self.player_key_control[1])

        self.fps_count = FPSCount(self)  # FPS number counter
        if self.game.show_fps:
            self.realtime_ui_updater.add(self.fps_count)

        battle_ui_images = self.game.battle_ui_images
        CharacterSpeechBox.images = battle_ui_images

        self.speech_prompt = CharacterInteractPrompt(battle_ui_images["button_weak"])
        self.city_map = CityMap(load_images(self.data_dir, screen_scale=self.screen_scale,
                                            subfolder=("ui", "map_select_ui")))

        battle_ui_dict = make_battle_ui(battle_ui_images)

        self.decision_select = YesNo(battle_ui_images)

        self.player_1_portrait = battle_ui_dict["player_1_portrait"]
        self.player_2_portrait = battle_ui_dict["player_2_portrait"]
        self.player_3_portrait = battle_ui_dict["player_3_portrait"]
        self.player_4_portrait = battle_ui_dict["player_4_portrait"]
        self.player_portraits = {1: self.player_1_portrait, 2: self.player_2_portrait,
                                 3: self.player_3_portrait, 4: self.player_4_portrait}

        self.player_1_wheel_ui = battle_ui_dict["player_1_wheel_ui"]
        self.player_2_wheel_ui = battle_ui_dict["player_2_wheel_ui"]
        self.player_3_wheel_ui = battle_ui_dict["player_3_wheel_ui"]
        self.player_4_wheel_ui = battle_ui_dict["player_4_wheel_ui"]
        self.player_wheel_uis = {1: self.player_1_wheel_ui, 2: self.player_2_wheel_ui,
                                 3: self.player_3_wheel_ui, 4: self.player_4_wheel_ui}
        self.current_weather = Weather(1, 0, 0, None)

        TextDrama.images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                       subfolder=("ui", "popup_ui", "drama_text"))
        self.drama_text = TextDrama(
            self.battle_camera_size)  # message at the top of screen that show up for important event

        # Battle ESC menu
        esc_menu_dict = make_esc_menu(self.game.char_selector_images, self.game.button_image,
                                      self.game.option_menu_images,
                                      self.master_volume, self.music_volume, self.voice_volume, self.effect_volume)

        self.player_char_base_interfaces = esc_menu_dict["player_char_base_interfaces"]
        self.battle_menu_button = esc_menu_dict["battle_menu_button"]
        self.esc_option_menu_button = esc_menu_dict["esc_option_menu_button"]
        self.esc_slider_menu = esc_menu_dict["esc_slider_menu"]
        self.esc_value_boxes = esc_menu_dict["esc_value_boxes"]
        self.esc_option_text = esc_menu_dict["volume_texts"]

        # Create the game camera
        self.main_player = 1  # TODO need to add recheck later for when resurrect count run out
        self.main_player_object = None
        self.camera_mode = "Follow"  # mode of game camera, follow player character or free observation
        self.camera_pos = Vector2(500, 500)  # camera pos on stage
        self.base_camera_begin = (self.camera_pos[0] - self.battle_camera_center[0]) / self.screen_scale[0]
        self.base_camera_end = (self.camera_pos[0] + self.battle_camera_center[0]) / self.screen_scale[0]

        self.shown_camera_pos = self.camera_pos  # pos of camera shown to player, in case of screen shaking or other effects

        self.dt = 0  # Realtime used for time calculation
        self.ui_dt = 0  # Realtime used for ui timer
        self.screen_shake_value = 0  # count for how long to shake camera

        Battle.camera = Camera(self.screen, self.battle_camera_size)

        self.base_cursor_pos = [0, 0]  # mouse pos on the map based on camera position
        self.command_cursor_pos = [0, 0]  # with zoom and screen scale for character command

        self.show_cursor_timer = 0

        # music player
        self.current_music = None
        self.music_left = pygame.mixer.Channel(1)
        self.music_left.set_volume(self.play_music_volume, 0)
        self.music_right = pygame.mixer.Channel(2)
        self.music_right.set_volume(0, self.play_music_volume)

        # Battle map object
        Stage.image = pygame.Surface.subsurface(self.camera.image,
                                                (0, 0, self.camera.image.get_width(),
                                                 self.camera.image.get_height()))
        Stage.camera_center_y = self.battle_camera_center[1]
        self.battle_stage = Stage(1)
        self.frontground_stage = Stage(100000000000000000000000000000000000000000000000)

        Effect.battle_stage = self.battle_stage
        Character.battle_stage = self.battle_stage  # add battle map to character class
        self.base_stage_start = 0
        self.stage_start = 0
        self.base_stage_end = 0
        self.stage_end = 0
        self.execute_cutscene = None
        self.start_cutscene = []
        self.reach_scene_event_list = {}  # cutscene that play when camera reach scene
        self.player_interact_event_list = {}
        self.base_stage_end_list = {}
        self.stage_end_list = {}
        self.end_delay = 0  # delay until stage end and continue to next one
        self.spawn_delay_timer = {}
        self.survive_timer = 0
        self.stage_end_choice = False
        self.stage_scene_lock = {}
        self.lock_objective = None
        self.next_lock = None
        self.cutscene_playing = None

    def prepare_new_stage(self, chapter, mission, stage, players, scene):

        for message in self.inner_prepare_new_stage(chapter, mission, stage, players, scene):
            self.game.error_log.write("Start Stage:" + str(chapter) + "." + str(mission) + "." + str(stage))
            print(message, end="")

    def inner_prepare_new_stage(self, chapter, mission, stage, players, scene):
        """Setup stuff when start new stage"""
        self.chapter = chapter
        self.chapter_sprite_ver = str(chapter)
        self.mission = mission
        self.stage = stage

        self.players = players
        self.existing_playable_characters = [value["ID"] for value in self.players.values()]

        # Stop any current music
        self.current_music = None
        self.music_left.stop()
        self.music_right.stop()

        # try:
        #     self.music_event = csv_read(self.main_dir, "music_event.csv",
        #                                 ("data", "module", self.module_folder, "map", play_map_type,
        #                                  self.map_selected), output_type="list")
        #     self.music_event = self.music_event[1:]
        #     if self.music_event:
        #         utility.convert_str_time(self.music_event)
        #         self.music_schedule = list(dict.fromkeys([item[1] for item in self.music_event]))
        #         new_list = []
        #         for time in self.music_schedule:
        #             new_event_list = []
        #             for event in self.music_event:
        #                 if time == event[1]:
        #                     new_event_list.append(event[0])
        #             new_list.append(new_event_list)
        #         self.music_event = new_list
        #     else:
        #         self.music_schedule = [self.weather_playing]
        #         self.music_event = []
        # except:  # any reading error will play random custom music instead
        #     self.music_schedule = [self.weather_playing]
        #     self.music_event = []

        # map_event_text = self.localisation.grab_text(("map", str(chapter), str(mission), str(stage), "eventlog"))
        # map_event = self.game.preset_map_data[chapter][mission][stage]["eventlog"]

        print("Start loading", self.chapter, self.mission, self.stage, scene)
        yield set_start_load(self, "stage setup")
        self.current_weather.__init__(1, 0, 0,
                                      self.weather_data)

        stage_data = self.game.preset_map_data[chapter][mission][stage]
        self.city_mode = False
        if scene:  # city stage with only 1 scene
            stage_data = stage_data[scene]
            self.city_mode = True
        stage_object_data = stage_data["data"]
        stage_event_data = copy.deepcopy(stage_data["event"])
        loaded_item = []
        later_enemy = {}
        self.stage_scene_lock = {}
        self.lock_objective = None
        self.stage_end_choice = False
        self.next_lock = None
        self.cutscene_playing = None
        self.base_stage_end = 0  # for object pos
        self.base_stage_start = 0  # for camera pos
        self.stage_start = self.battle_camera_center[0]
        self.stage_end = -self.battle_camera_center[0]
        self.execute_cutscene = None
        self.decision_select.selected = None
        self.end_delay = 0
        self.start_cutscene = []
        self.reach_scene_event_list = {}
        self.player_interact_event_list = {}
        self.base_stage_end_list = {}
        self.stage_end_list = {}
        self.speech_prompt.clear()

        first_lock = None
        for value in stage_object_data.values():
            if value["Object"] not in loaded_item:  # load image
                if value["Type"] == "stage":  # type of object with image data to load
                    if value["Type"] == "stage":  # load background stage
                        image = load_image(self.data_dir, self.screen_scale, value["Object"] + ".png",
                                           ("map", "stage"))  # no scaling yet
                        if "front" in value["Type"]:
                            self.frontground_stage.images[value["Object"]] = image
                        else:
                            self.battle_stage.images[value["Object"]] = image

                        loaded_item.append(value["Object"])

            if "stage" in value["Type"]:  # assign stage data
                if "front" in value["Type"]:
                    self.frontground_stage.data[value["POS"]] = value["Object"]
                else:  # battle stage should have data for all scene
                    self.battle_stage.data[value["POS"]] = value["Object"]
                    later_enemy[value["POS"]] = []
            elif "endchoice" in value["Type"]:
                self.stage_end_choice = True
            elif "lock" in value["Type"]:
                first_lock_pos = value["POS"]
                lock_pos = value["POS"]
                if type(first_lock_pos) is str:
                    lock_pos = tuple(
                        [int(item) for item in value["POS"].split(",")])  # list of stage lock, get last one
                    first_lock_pos = lock_pos[-1]  # get last one
                else:
                    lock_pos = (lock_pos,)
                if not first_lock:  # change stage end to first lock
                    first_lock = True
                    self.base_stage_end = 1920 * first_lock_pos
                    self.stage_end = (1920 * self.screen_scale[0] * first_lock_pos) - self.battle_camera_center[0]
                    self.next_lock = lock_pos
                self.stage_scene_lock[lock_pos] = value["Object"]
            elif value["Type"] == "object":
                StageObject(value["Object"], value["POS"])

        base_stage_end = 0
        stage_end = -self.battle_camera_center[0]
        for key, value in self.battle_stage.data.items():
            base_stage_end += 1920  # 1 scene width size always 1920
            stage_end += self.battle_stage.images[value].get_width()
            self.base_stage_end_list[key] = base_stage_end
            self.stage_end_list[key] = stage_end
        if not self.base_stage_end:  # no stage end from lock, use last stage end value
            self.base_stage_end = base_stage_end
            self.stage_end = stage_end
        yield set_done_load()

        yield set_start_load(self, "common setup")
        self.camera_mode = self.start_camera_mode
        if not self.players:
            self.camera_mode = "Free"

        for this_group in self.all_team_character.values():
            this_group.empty()
        for this_group in self.all_team_enemy.values():
            this_group.empty()
        for this_group in self.all_team_enemy_part.values():
            this_group.empty()

        self.helper = None
        self.score_board = None

        self.spawn_delay_timer = {}
        start_enemy = [item for item in stage_data["character"] if "camera_scene" not in item["Arrive Condition"]]
        self.later_enemy = {scene: [item for item in stage_data["character"] if
                                    "camera_scene" in item["Arrive Condition"] and
                                    item["Scene"] == scene] for scene in later_enemy}
        for scene, value in self.later_enemy.items():  # rearrange arrival list based on delay
            new_value = {}
            self.spawn_delay_timer[scene] = 0
            for item in value:
                if "delay" in item["Arrive Condition"]:  # character has delay for arrival
                    timer = float(item["Arrive Condition"]["delay"])
                    if timer not in new_value:
                        new_value[timer] = []
                    new_value[timer].append(item)
                else:
                    if 0 not in new_value:
                        new_value[0] = []
                    new_value[0].append(item)
            self.later_enemy[scene] = new_value

        add_helper = True
        if self.stage == 0:  # city stage not add helper
            add_helper = False
        self.setup_battle_character(self.players, start_enemy, add_helper=add_helper)

        if not self.city_mode:
            for player in self.player_objects:
                self.realtime_ui_updater.add(self.player_portraits[player])
                self.player_portraits[player].add_char_portrait(self.player_objects[player])

        self.main_player_object = self.player_objects[self.main_player]
        for trigger, value in stage_event_data.items():
            if "char" in trigger:  # trigger depend on character
                for key, value2 in value.items():
                    for this_char in self.all_chars:
                        if this_char.game_id == key:
                            if "in_camera" in trigger:  # reach camera event
                                this_char.reach_camera_event = value2
                            break
            elif "start" in trigger:
                for key, value2 in value.items():
                    for key3, value3 in value2.items():
                        if value3[0]["Type"]:  # check only parent event type data
                            self.start_cutscene.append(value3)
            elif "interact" in trigger:
                for key, value2 in value.items():
                    char_found = None
                    for char in self.all_chars:
                        if char.game_id == key:
                            char_found = char
                            break
                    for key3, value3 in value2.items():
                        if "/Any/" in value3[0]["ID"] or "/" + self.main_player_object.sprite_id + "/" in value3[0][
                            "ID"]:
                            # only add event involving the character of first player
                            if value3[0]["Type"] == "char":
                                # must always have char id as second item in trigger
                                if char_found:
                                    if char_found not in self.player_interact_event_list:
                                        self.player_interact_event_list[char_found] = []
                                    self.player_interact_event_list[char_found].append(value3)
                            elif value3[0]["Type"] == "pos":  # interact with specific pos
                                if key not in self.player_interact_event_list:
                                    self.player_interact_event_list[key] = []
                                self.player_interact_event_list[key].append(value3)
            elif "camera" in trigger:  # trigger depend on camera reaching something
                if "reach_scene" in trigger:
                    for key, value2 in value.items():
                        for key3, value3 in value2.items():
                            if key not in self.reach_scene_event_list:
                                self.reach_scene_event_list[key] = {}
                            if value3[0]["Type"] == "cutscene":  # check only parent event type data
                                if "cutscene" not in self.reach_scene_event_list[key]:
                                    self.reach_scene_event_list[key]["cutscene"] = []
                                self.reach_scene_event_list[key]["cutscene"].append(value3)
                            elif value3[0]["Type"] == "weather":
                                weather_strength = 0
                                if "strength" in value3[0]["Property"]:
                                    weather_strength = value3[0]["Property"]["strength"]
                                self.reach_scene_event_list[key]["weather"] = (value3[0]["Object"], weather_strength)
                            elif value3[0]["Type"] == "music":
                                self.reach_scene_event_list[key]["music"] = self.music_pool[
                                    str(value3[0]["Object"])]
                            elif value3[0]["Type"] == "sound":
                                if "sound" not in self.reach_scene_event_list[key]:
                                    self.reach_scene_event_list[key]["sound"] = []
                                self.reach_scene_event_list[key]["sound"].append(
                                    self.sound_effect_pool[str(value3[0]["Object"])])

            elif "execute" in trigger:
                for key, value2 in value.items():
                    self.execute_cutscene = value2
        yield set_done_load()

    def run_game(self):
        # Create Starting Values
        self.game_state = "battle"  # battle mode
        self.input_popup = None  # no popup asking for user text input state
        self.drama_text.queue = []  # reset drama text popup queue

        self.camera_mode = self.start_camera_mode

        # portrait = transform.smoothscale(this_unit.portrait, (150 * self.screen_scale[0],
        #                                                       150 * self.screen_scale[1]))
        # self.portrait_rect = portrait.get_rect(center=(portrait.get_width() / 1.6,
        #                                                portrait.get_height() * 0.95))
        self.camera_pos = Vector2(500, self.battle_camera_center[1])
        self.fix_camera()

        self.shown_camera_pos = self.camera_pos

        self.screen_shake_value = 0
        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0  # This is timer for combat related function, use self time (realtime * game_speed)
        self.dt = 0  # Realtime used for time calculation
        self.ui_dt = 0  # Realtime used for ui timer
        self.weather_spawn_timer = 0
        self.show_cursor_timer = 0
        self.main_player_battle_cursor.shown = True
        self.player_damage = {1: 0, 2: 0, 3: 0, 4: 0}
        self.player_kill = {1: 0, 2: 0, 3: 0, 4: 0}
        self.player_boss_kill = {1: 0, 2: 0, 3: 0, 4: 0}
        self.play_time = 0
        self.stage_gold = 0
        self.stage_score = 0
        self.last_resurrect_stage_score = 5000  # start at 5000 to get next resurrect reserve
        self.reserve_resurrect_stage_score = 0

        self.base_cursor_pos = [0, 0]  # mouse pos on the map based on camera position
        self.command_cursor_pos = [0, 0]  # with zoom and screen scale for character command
        mouse.set_pos(Vector2(self.battle.camera_pos[0], 140 * self.screen_scale[1]))  # set cursor to midtop screen

        self.player_key_control = {player: self.config["USER"]["control player " + str(player)] for player in
                                   self.game.player_list}
        self.player_key_bind = {player: self.game.player_key_bind_list[player][self.player_key_control[player]] for
                                player in self.game.player_list}
        self.player_key_bind_name = {player: {value: key for key, value in self.player_key_bind[player].items()} for
                                     player in self.game.player_list}
        self.player_key_press = {player: {key: False for key in self.player_key_bind[player]} for player in
                                 self.game.player_list}
        self.player_key_hold = {player: {key: False for key in self.player_key_bind[player]} for player in
                                self.game.player_list}
        self.player_joystick = self.game.player_joystick
        self.joystick_player = self.game.joystick_player

        self.screen.fill((0, 0, 0))
        self.realtime_ui_updater.add(self.main_player_battle_cursor)
        self.remove_ui_updater(self.cursor)
        # self.map_def_array = []
        # self.mapunitarray = [[x[random.randint(0, 1)] if i != j else 0 for i in range(1000)] for j in range(1000)]
        # pygame.mixer.music.set_endevent(self.SONG_END)  # End current music before battle start

        frame = 0
        while True:  # self running
            frame += 1

            if frame % 30 == 0 and hasattr(self.game, "profiler"):  # Remove for stable release, along with dev key
                self.game.profiler.refresh()
                frame = 0

            key_state = pygame.key.get_pressed()
            esc_press = False

            self.player_key_press = {key: dict.fromkeys(self.player_key_press[key], False) for key in
                                     self.player_key_press}
            self.player_key_hold = {key: dict.fromkeys(self.player_key_hold[key], False) for key in
                                    self.player_key_hold}

            self.true_dt = self.clock.get_time() / 1000  # dt before game_speed
            self.play_time += self.true_dt

            for player, key_set in self.player_key_press.items():
                if self.player_key_control[player] == "keyboard":
                    for key in key_set:  # check for key holding
                        if type(self.player_key_bind[player][key]) == int and key_state[
                            self.player_key_bind[player][key]]:
                            self.player_key_hold[player][key] = True
                else:
                    player_key_bind_name = self.player_key_bind_name[player]
                    for joystick_id, joystick in self.joysticks.items():
                        if self.player_joystick[player] == joystick_id:
                            for i in range(joystick.get_numbuttons()):
                                if joystick.get_button(i) and i in player_key_bind_name:
                                    self.player_key_hold[player][player_key_bind_name[i]] = True

                            for i in range(joystick.get_numhats()):
                                if joystick.get_hat(i)[0] > 0.1 or joystick.get_hat(i)[0] < -0.1:
                                    hat_name = "hat" + number_to_minus_or_plus(joystick.get_hat(i)[0]) + str(0)
                                    if hat_name in self.player_key_bind_name:
                                        self.player_key_hold[player][player_key_bind_name[hat_name]] = True
                                if joystick.get_hat(i)[1] > 0.1 or joystick.get_hat(i)[1] < -0.1:
                                    hat_name = "hat" + number_to_minus_or_plus(joystick.get_hat(i)[1]) + str(1)
                                    if hat_name in self.player_key_bind_name:
                                        self.player_key_hold[player][player_key_bind_name[hat_name]] = True

                            for i in range(joystick.get_numaxes()):
                                if joystick.get_axis(i) > 0.5 or joystick.get_axis(i) < -0.5:
                                    if i in (2, 3) and player == 1:  # right axis only for cursor (player 1 only)
                                        vec = pygame.math.Vector2(joystick.get_axis(2), joystick.get_axis(3))
                                        radius, angle = vec.as_polar()
                                        adjusted_angle = (angle + 90) % 360
                                        if self.game_state == "battle":
                                            new_pos = pygame.Vector2(
                                                self.main_player_battle_cursor.pos[0] + (
                                                        self.true_dt * 1000 * sin(radians(adjusted_angle))),
                                                self.main_player_battle_cursor.pos[1] - (
                                                        self.true_dt * 1000 * cos(radians(adjusted_angle))))
                                        else:
                                            new_pos = pygame.Vector2(
                                                self.cursor.pos[0] + (
                                                        self.true_dt * 1000 * sin(radians(adjusted_angle))),
                                                self.cursor.pos[1] - (
                                                        self.true_dt * 1000 * cos(radians(adjusted_angle))))
                                        if new_pos[0] < 0:
                                            new_pos[0] = 0
                                        elif new_pos[0] > self.corner_screen_width:
                                            new_pos[0] = self.corner_screen_width
                                        if new_pos[1] < 0:
                                            new_pos[1] = 0
                                        elif new_pos[1] > self.corner_screen_height:
                                            new_pos[1] = self.corner_screen_height
                                        pygame.mouse.set_pos(new_pos)
                                    else:
                                        axis_name = "axis" + number_to_minus_or_plus(joystick.get_axis(i)) + str(i)
                                        if axis_name in player_key_bind_name:
                                            # axis pressing require different way to check than other buttons
                                            if (joystick.get_axis(i) > 0.9 or joystick.get_axis(i) < -0.9) and \
                                                    player_key_bind_name[axis_name] in self.player_objects[
                                                player].player_key_hold_timer:
                                                self.player_key_hold[player][player_key_bind_name[axis_name]] = True
                                            else:
                                                self.player_key_hold[player][player_key_bind_name[axis_name]] = True
                                                self.player_key_press[player][player_key_bind_name[axis_name]] = True

            self.base_cursor_pos = Vector2(
                (self.main_player_battle_cursor.pos[0] - self.battle_camera_center[0] + self.camera_pos[0]),
                (self.main_player_battle_cursor.pos[1] - self.battle_camera_center[1] + self.camera_pos[
                    1]))  # mouse pos on the map based on camera position
            self.command_cursor_pos = Vector2(self.base_cursor_pos[0] / self.screen_scale[0],
                                              self.base_cursor_pos[1] / self.screen_scale[1])  # with screen scale

            for event in pygame.event.get():  # get event that happen
                if event.type == QUIT:  # quit game
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.JOYBUTTONUP:
                    joystick = event.instance_id
                    if joystick in self.joystick_player:
                        player = self.joystick_player[joystick]
                        if self.player_key_control[player] == "joystick" and \
                                event.button in self.player_key_bind_name[player]:  # check for key press
                            self.player_key_press[player][self.player_key_bind_name[player][event.button]] = True

                elif event.type == pygame.KEYDOWN:
                    event_key_press = event.key
                    if event_key_press == K_ESCAPE:  # accept esc button always
                        esc_press = True
                    for player in self.player_key_control:
                        if self.player_key_control[player] == "keyboard" and \
                                event_key_press in self.player_key_bind_name[player]:  # check for key press
                            self.player_key_press[player][self.player_key_bind_name[player][event_key_press]] = True

                    # FOR DEVELOPMENT
                    if event.key == K_F1:
                        self.drama_text.queue.append("Hello and welcome to showcase video")
                    elif event.key == K_F2:
                        CharacterSpeechBox(self.main_player_object, "Hello and welcome to showcase video.")
                    # elif event.key == K_F3:
                    #     self.drama_text.queue.append("New Medieval art style as shown in previous videos")
                    # elif event.key == K_F4:
                    #     self.drama_text.queue.append("Few more updates until demo release")
                    # elif event.key == K_F5:
                    #     self.drama_text.queue.append("Rushed to the English line, he fought valiantly alone")
                    elif event.key == K_F6:
                        for enemy in self.all_team_enemy[1]:
                            if not enemy.invincible and int(enemy.base_pos[0] / 1920) in \
                                    (self.battle_stage.spawn_check_scene - 1, self.battle_stage.spawn_check_scene):
                                enemy.health = 0
                    elif event.key == K_F7:  # clear profiler
                        if hasattr(self.game, "profiler"):
                            self.game.profiler.clear()
                    elif event.key == K_F8:  # show/hide profiler
                        if not hasattr(self.game, "profiler"):
                            self.game.setup_profiler()
                        self.game.profiler.switch_show_hide()
                    elif event.key == pygame.K_1:
                        for character in self.player_objects.values():
                            character.cal_loss(None, 0, (50, -200), character.angle, (0, 0), False)
                    # elif event_key_press == pygame.K_k:
                    #     if self.players:
                    #         for unit in self.players.alive_leader_follower:
                    #             unit.health -= unit.health
                    # self.players.health = 0

                elif event.type == pygame.JOYDEVICEADDED:
                    # Player add new joystick by plug in
                    joy = pygame.joystick.Joystick(event.device_index)
                    self.joysticks[joy.get_instance_id()] = joy
                    joy_name = joy.get_name()
                    for name in self.joystick_bind_name:
                        if name in joy_name:  # find common name
                            self.joystick_name[joy.get_instance_id()] = name
                    if joy.get_instance_id() not in self.joystick_name:
                        self.joystick_name[joy.get_instance_id()] = "Other"

                    for player in self.player_key_control:  # check for player with joystick control but no assigned yet
                        if self.player_key_control[player] == "joystick" and player not in self.player_joystick:
                            # assign new joystick to player with joystick control setting
                            self.player_joystick[player] = joy.get_instance_id()
                            self.joystick_player[joy.get_instance_id()] = player
                            break  # only one player get assigned

                elif event.type == pygame.JOYDEVICEREMOVED:
                    # Player unplug joystick
                    del self.joysticks[event.instance_id]
                    del self.joystick_name[event.instance_id]
                    for key, value in self.player_joystick.copy().items():
                        if value == event.instance_id:
                            self.player_joystick.pop(key)
                            self.joystick_player.pop(value)

            if not self.music_left.get_busy() and self.current_music:  # change if music finish playing
                self.music_left.play(self.current_music, fade_ms=100)
                self.music_left.set_volume(self.play_music_volume, 0)
                self.music_right.play(self.current_music, fade_ms=100)
                self.music_right.set_volume(0, self.play_music_volume)

            if self.player_key_press[self.main_player]["Menu/Cancel"]:
                # open/close menu
                esc_press = True

            self.ui_updater.update()  # update ui before more specific update

            if self.game_state == "battle":  # game in battle state
                if esc_press:  # open/close menu
                    if self.city_mode:  # add character setup UI for city mode when pause game
                        for player in self.player_objects:
                            self.add_ui_updater(self.player_char_base_interfaces[player],
                                                self.player_char_interfaces[player])
                    self.game_state = "menu"  # open menu
                    self.stage_translation_text_popup.popup(
                        (self.screen_rect.midleft[0], self.screen_rect.height * 0.88),
                        self.game.localisation.grab_text(
                            ("map", self.chapter, self.mission, self.stage,
                             self.battle_stage.current_scene, "Text")),
                        width_text_wrapper=self.screen_rect.width)
                    self.add_ui_updater(self.cursor, self.battle_menu_button,
                                        self.stage_translation_text_popup)  # add menu and its buttons to drawer
                    self.realtime_ui_updater.remove(self.main_player_battle_cursor)
                elif self.city_mode and self.player_key_press[self.main_player]["Special"]:
                    if self.game_state != "map":  # open city map
                        self.add_ui_updater(self.cursor, self.city_map)
                        self.game_state = "map"

                self.camera_process()

                # Update game time
                self.dt = self.true_dt * self.game_speed  # apply dt with game_speed for calculation
                if self.dt > 0.1:  # one frame update should not be longer than 0.1 second for calculation
                    self.dt = 0.1  # make it so stutter and lag does not cause overtime issue

                self.ui_timer += self.dt  # ui update by real time instead of self time to reduce workload
                self.ui_dt = self.dt  # get ui timer before apply

                if self.main_player_battle_cursor.pos_change:  # display cursor when have movement
                    self.show_cursor_timer = 0.1
                    self.main_player_battle_cursor.shown = True

                if self.show_cursor_timer:
                    self.show_cursor_timer += self.dt
                    if self.show_cursor_timer > 3:
                        self.show_cursor_timer = 0
                        self.main_player_battle_cursor.shown = False
                        self.main_player_battle_cursor.rect.topleft = (-100, -100)

                # Drama text function
                if not self.drama_timer and self.drama_text.queue:  # Start timer and draw if there is event queue
                    self.realtime_ui_updater.add(self.drama_text)
                    self.drama_text.process_queue()
                    self.drama_timer = 0.1
                elif self.drama_timer:
                    self.drama_text.play_animation()
                    self.drama_timer += self.ui_dt
                    if self.drama_timer > 5:  # drama popup last for 5 seconds
                        self.drama_timer = 0
                        self.realtime_ui_updater.remove(self.drama_text)

                # Weather system
                if self.current_weather.spawn_rate:
                    self.weather_spawn_timer += self.dt
                    if self.weather_spawn_timer >= self.current_weather.spawn_rate:
                        self.weather_spawn_timer = 0
                        self.spawn_weather_matter()

                # Screen shaking
                self.shown_camera_pos = self.camera_pos.copy()  # reset camera pos first
                if self.screen_shake_value:
                    self.screen_shake_value -= (self.dt * 100)
                    self.shake_camera()
                    if self.screen_shake_value < 0:
                        self.screen_shake_value = 0

                # Battle related updater
                self.battle_stage.update(self.shown_camera_pos)  # update stage first
                if not self.cutscene_playing:
                    self.character_updater.update(self.dt)
                    self.effect_updater.update(self.dt)
                else:
                    self.character_updater.cutscene_update(self.dt)
                    self.effect_updater.cutscene_update(self.dt)
                self.realtime_ui_updater.update()  # update UI
                self.camera.update(self.shown_camera_pos, self.battle_camera, self.realtime_ui_updater)
                # self.frontground_stage.update(self.shown_camera_pos[0])  # update frontground stage last

                for key, value in self.sound_effect_queue.items():  # play each sound effect initiate in this loop
                    self.play_sound_effect(key, value)
                self.sound_effect_queue = {}

                if self.ui_timer >= 0.1 and not self.city_mode:
                    for key, value in self.player_objects.items():
                        self.player_portraits[key].value_input(value)

                    self.ui_drawer.draw(self.screen)  # draw the UI
                    self.ui_timer -= 0.1

                if not self.cutscene_playing:  # no current cutscene check for one
                    if self.next_lock:  # stage has lock, check if player reach next lock or unlock it
                        if self.lock_objective:  # player in locked stage, check if pass yet
                            pass_objective = False  # check for passing lock objective
                            if self.lock_objective == "clear":
                                if not len([enemy for enemy in self.all_team_enemy[1] if
                                            self.base_stage_start <= enemy.base_pos[0] <= self.base_stage_end]):
                                    pass_objective = True
                            elif self.lock_objective == "survive":
                                self.survive_timer -= self.dt
                                if self.survive_timer < 0:
                                    self.survive_timer = 0
                                    pass_objective = True

                            if pass_objective:  # can reach next scene, check for possible scene lock
                                self.lock_objective = None
                                if self.stage_scene_lock:
                                    self.next_lock = tuple(self.stage_scene_lock.keys())[0]
                                    self.base_stage_end = self.base_stage_end_list[self.next_lock[-1]]
                                    self.stage_end = self.stage_end_list[self.next_lock[-1]]
                                else:  # no more lock, make the stage_end the final stage position
                                    self.next_lock = None  # assign None so no need to do below code in later update
                                    self.base_stage_end = self.base_stage_end_list[
                                        tuple(self.base_stage_end_list.keys())[-1]]
                                    self.stage_end = self.stage_end_list[tuple(self.stage_end_list.keys())[-1]]

                        elif self.battle_stage.current_scene >= self.next_lock[0]:
                            # player (camera) reach next lock
                            self.base_stage_start = self.base_stage_end_list[self.next_lock[0]] - 1920
                            self.stage_start = self.stage_end_list[self.next_lock[0]]
                            self.base_stage_end = self.base_stage_end_list[self.next_lock[-1]]
                            self.stage_end = self.stage_end_list[self.next_lock[-1]]

                            self.lock_objective = self.stage_scene_lock[self.next_lock]
                            if "survive" in self.lock_objective:
                                self.survive_timer = float(self.lock_objective.split("_")[-1])
                                self.lock_objective = "survive"

                            self.stage_scene_lock.pop(self.next_lock)

                    if self.later_enemy[self.battle_stage.spawn_check_scene]:
                        # check for enemy arriving based on camera pos
                        self.spawn_delay_timer[self.battle_stage.spawn_check_scene] += self.dt
                        first_delay = tuple(self.later_enemy[self.battle_stage.spawn_check_scene].keys())[0]
                        if self.spawn_delay_timer[self.battle_stage.spawn_check_scene] >= first_delay:
                            # spawn based on delay timer
                            self.setup_battle_character((), self.later_enemy[self.battle_stage.spawn_check_scene][
                                first_delay],
                                                        add_helper=False)
                            self.later_enemy[self.battle_stage.spawn_check_scene].pop(first_delay)

                    for player_index, player_object in self.player_objects.items():
                        player_object.player_input(player_index, self.dt)

                    if self.reach_scene_event_list:
                        # check for event with camera reaching
                        if self.battle_stage.reach_scene in self.reach_scene_event_list:
                            if "weather" in self.reach_scene_event_list[self.battle_stage.reach_scene]:
                                # change weather
                                self.current_weather.__init__(
                                    self.reach_scene_event_list[self.battle_stage.reach_scene]["weather"][0],
                                    randint(0, 359),
                                    self.reach_scene_event_list[self.battle_stage.reach_scene]["weather"][1],
                                    self.weather_data)
                                self.reach_scene_event_list[self.battle_stage.reach_scene].pop("weather")
                            if "music" in self.reach_scene_event_list[self.battle_stage.reach_scene]:  # change weather
                                self.current_music = self.reach_scene_event_list[self.battle_stage.reach_scene]["music"]
                                self.reach_scene_event_list[self.battle_stage.reach_scene].pop("music")
                            if "sound" in self.reach_scene_event_list[self.battle_stage.reach_scene]:  # change weather
                                for sound_effect in self.reach_scene_event_list[self.battle_stage.reach_scene]:
                                    self.add_sound_effect_queue(self.sound_effect_pool[sound_effect[0]],
                                                                self.camera_pos, sound_effect[1], sound_effect[2])
                                self.reach_scene_event_list[self.battle_stage.reach_scene].pop("sound")
                            if "cutscene" in self.reach_scene_event_list[self.battle_stage.reach_scene]:  # cutscene
                                for parent_event in self.reach_scene_event_list[self.battle_stage.reach_scene][
                                    "cutscene"]:
                                    # play one parent at a time
                                    self.cutscene_playing = parent_event
                                    if "replayable" not in parent_event[0]["Property"]:
                                        self.reach_scene_event_list[self.battle_stage.reach_scene].pop("cutscene")
                            if not self.reach_scene_event_list[self.battle_stage.reach_scene]:  # no more event left
                                self.reach_scene_event_list.pop(self.battle_stage.reach_scene)

                    if self.player_interact_event_list:
                        event_list = sorted({key[0]: self.main_player_object.base_pos.distance_to(key[1]) for key in
                                             [(item2, item2) if type(item2) is tuple else (item2, item2.base_pos) for
                                              item2 in
                                              self.player_interact_event_list]}.items(), key=lambda item: item[1])
                        for item in event_list:
                            target_pos = item[0]
                            if type(item[0]) is not tuple:
                                target_pos = (item[0].base_pos[0], item[0].base_pos[1] - item[0].sprite_size * 4.5)
                            if 100 < abs(self.main_player_object.base_pos[0] - target_pos[0]) < 250:
                                # use player with the lowest number as interactor
                                self.speech_prompt.add_to_screen(self.main_player_object, target_pos)
                                if self.player_key_press[self.main_player]["Weak"]:  # player interact, start event
                                    self.speech_prompt.clear()  # remove prompt
                                    if (self.main_player_object.base_pos[0] - target_pos[0] < 0 and
                                        self.main_player_object.angle != -90) or \
                                            (self.main_player_object.base_pos[0] - target_pos[0] >= 0 and
                                             self.main_player_object.angle != 90):  # face target
                                        self.main_player_object.new_angle *= -1
                                        self.main_player_object.rotate_logic()
                                    if type(item[0]) is not tuple:
                                        if (item[0].base_pos[0] - self.main_player_object.base_pos[0] < 0 and
                                            item[0].angle != -90) or \
                                                (item[0].base_pos[0] - self.main_player_object.base_pos[0] >= 0 and
                                                 item[0].angle != 90):  # face player
                                            item[0].new_angle *= -1
                                            item[0].rotate_logic()

                                    if "replayable" not in self.player_interact_event_list[item[0]][0][0]["Property"]:
                                        self.cutscene_playing = self.player_interact_event_list[item[0]][0]
                                        self.player_interact_event_list[item[0]].remove(self.cutscene_playing)
                                        if not self.player_interact_event_list[item[0]]:
                                            self.player_interact_event_list.pop(item[0])
                                    else:  # event can be replayed, use copy instead of original to prevent delete
                                        self.cutscene_playing = copy.deepcopy(
                                            self.player_interact_event_list[item[0]][0])
                                break

                else:  # currently in cutscene mode
                    for child_event in self.cutscene_playing.copy():
                        # play child events until found one that need waiting
                        if child_event["Object"] == "camera":
                            if child_event["Type"] == "move" and "POS" in child_event["Property"]:
                                camera_pos_target = self.stage_end_list[child_event["Property"]["POS"]]
                                camera_speed = 400
                                if "speed" in child_event["Property"]:
                                    camera_speed = child_event["Property"]["speed"]
                                if self.camera_pos[0] != camera_pos_target:
                                    if self.camera_pos[0] < camera_pos_target:
                                        self.camera_pos[0] += camera_speed * self.dt
                                        if self.camera_pos[0] > camera_pos_target:
                                            self.camera_pos[0] = camera_pos_target
                                    else:
                                        self.camera_pos[0] -= camera_speed * self.dt
                                        if self.camera_pos[0] < camera_pos_target:
                                            self.camera_pos[0] = camera_pos_target
                                else:
                                    self.cutscene_playing.remove(child_event)
                        else:
                            event_character = None
                            if child_event["Object"] == "pm":  # main player
                                event_character = self.main_player_object
                            else:
                                for character in self.all_chars:
                                    if character.game_id == child_event["Object"]:
                                        event_character = character
                                        break
                            if event_character and (not event_character.cutscene_event or
                                                    (("hold" in event_character.current_action or
                                                      "repeat" in event_character.current_action) and
                                                     event_character.cutscene_event != child_event)):
                                # replace previous event on hold or repeat when there is new one to play next
                                if "hold" in event_character.current_action:
                                    # previous event done
                                    self.cutscene_playing.remove(event_character.cutscene_event)

                                event_character.cutscene_event = child_event
                                if "POS" in child_event["Property"]:
                                    if type(child_event["Property"]["POS"]) is str:
                                        target_scene = self.battle_stage.current_scene
                                        if "reach_" in child_event["Property"]["POS"]:
                                            target_scene = self.battle_stage.reach_scene

                                        if "start" in child_event["Property"]["POS"]:
                                            positioning = event_character.layer_id
                                            if event_character.layer_id > 4:
                                                positioning = uniform(1, 4)
                                            ground_pos = event_character.ground_pos
                                            if event_character.fly:  # flying character can just move with current y pos
                                                ground_pos = event_character.base_pos[1]
                                            event_character.cutscene_target_pos = Vector2(
                                                (1920 * target_scene) + (100 * positioning), ground_pos)
                                        elif "middle" in child_event["Property"]["POS"]:
                                            ground_pos = event_character.ground_pos
                                            if event_character.fly:  # flying character can just move with current y pos
                                                ground_pos = event_character.base_pos[1]
                                            event_character.cutscene_target_pos = Vector2(
                                                (1920 * target_scene) - (self.battle_camera_center[0] * 1.5),
                                                ground_pos)
                                        elif "center" in child_event["Property"]["POS"]:
                                            # true center, regardless of flying
                                            event_character.cutscene_target_pos = Vector2(
                                                (1920 * target_scene) - (self.battle_camera_center[0] * 1.5),
                                                self.battle_camera_center[1])
                                    else:
                                        event_character.cutscene_target_pos = Vector2(
                                            child_event["Property"]["POS"][0],
                                            child_event["Property"]["POS"][1])
                                elif "target" in child_event["Property"]:
                                    for character2 in self.all_chars:
                                        if character2.game_id == child_event["Property"]["target"]:  # go to target pos
                                            event_character.cutscene_target_pos = character2.base_pos
                                            break
                                if "angle" in child_event["Property"]:
                                    if child_event["Property"]["angle"] == "target":
                                        # facing target must have cutscene_target_pos
                                        if event_character.cutscene_target_pos[0] >= event_character.base_pos[0]:
                                            event_character.new_angle = -90
                                        else:
                                            event_character.new_angle = 90
                                    else:
                                        event_character.new_angle = int(child_event["Property"]["angle"])
                                    event_character.rotate_logic()
                                animation = child_event["Animation"]
                                animation_dict = {}
                                if animation:
                                    animation_dict = {"name": child_event["Animation"]} | child_event["Property"]
                                event_character.pick_cutscene_animation(animation_dict)
                                if child_event["Text ID"]:
                                    specific_timer = None
                                    player_input_indicator = None
                                    if "player_interact" in child_event["Property"]:
                                        specific_timer = infinity
                                        player_input_indicator = True
                                    elif "timer" in child_event["Property"]:
                                        specific_timer = child_event["Property"]
                                    elif "select" not in child_event["Property"]:
                                        # selecting event, also infinite timer but not add player input indication
                                        specific_timer = infinity
                                    CharacterSpeechBox(event_character,
                                                       self.localisation.grab_text(("event",
                                                                                    child_event["Text ID"],
                                                                                    "Text")),
                                                       specific_timer=specific_timer,
                                                       player_input_indicator=player_input_indicator,
                                                       cutscene_event=child_event)
                            elif not event_character:
                                # no character to play for this cutscene, no need to loop further
                                self.cutscene_playing.remove(child_event)
                        if "select" in child_event["Property"]:
                            if child_event["Property"]["select"] == "yesno":
                                self.realtime_ui_updater.add(self.decision_select)
                        if "wait_done" in child_event["Property"] or "player_interact" in child_event["Property"] or \
                                "select" in child_event["Property"]:
                            break
                    end_battle_specific_mission = self.cutscene_player_input()
                    if end_battle_specific_mission:  # event cause the end of mission, go to the output mission next
                        return end_battle_specific_mission

                if not self.city_mode and not self.all_team_enemy[1]:  # all enemies dead, end stage process
                    if not self.end_delay and not self.cutscene_playing:
                        mission_str = str(self.chapter) + "." + str(self.mission) + "." + str(self.stage)
                        # not ending stage yet, due to decision waiting or playing cutscene
                        if self.decision_select not in self.realtime_ui_updater and self.stage_end_choice:
                            if mission_str not in self.main_story_profile["story choice"]:
                                if "Victory" not in self.drama_text.queue:
                                    self.drama_text.queue.append("Victory")
                                self.realtime_ui_updater.add(self.decision_select)
                        elif not self.stage_end_choice:
                            if "Victory" not in self.drama_text.queue:
                                self.drama_text.queue.append("Victory")

                        if self.decision_select.selected or mission_str in self.main_story_profile["story choice"]:
                            self.end_delay = 0.1
                            choice = self.decision_select.selected
                            if mission_str in self.main_story_profile["story choice"]:
                                choice = self.main_story_profile["story choice"][mission_str]
                            if choice == "yes":
                                for character in self.character_updater:
                                    if character.is_boss and not character.leader:  # boss char that is not follower
                                        # start decision animation
                                        character.engage_combat()
                                        character.position = "Stand"  # enforce stand position
                                        character.current_action = character.submit_action
                                        character.show_frame = 0
                                        character.frame_timer = 0
                                        character.pick_animation()
                            else:  # start execution cutscene
                                self.cutscene_playing = self.execute_cutscene

                            self.realtime_ui_updater.remove(self.decision_select)

                    if not self.cutscene_playing and \
                            (self.decision_select.selected or self.decision_select not in self.realtime_ui_updater):
                        #  player select decision or mission has no decision, count end delay
                        self.end_delay += self.dt

                        if self.end_delay >= 5:  # end battle
                            self.end_delay = 0
                            if self.stage + 1 in self.game.preset_map_data[self.chapter][
                                self.mission]:  # has next stage
                                return True
                            else:
                                if self.mission + 1 in self.game.preset_map_data[self.chapter]:  # has next mission
                                    return True
                                else:
                                    return False

            elif self.game_state == "menu":  # Complete battle pause when open either esc menu or lorebook
                self.battle_stage.update(self.shown_camera_pos)  # update stage first
                # self.realtime_ui_updater.update()  # update UI
                self.camera.update(self.shown_camera_pos, self.battle_camera, self.realtime_ui_updater)
                # self.frontground_stage.update(self.shown_camera_pos)  # update frontground stage last
                self.ui_drawer.draw(self.screen)  # draw the UI

                if self.input_popup:  # currently, have input text pop up on screen, stop everything else until done
                    if self.input_ok_button.event_press:
                        if self.input_popup[1] == "quit":  # quit game
                            pygame.quit()
                            sys.exit()

                        self.input_box.text_start("")
                        self.input_popup = None
                        self.remove_ui_updater(self.input_ui_popup, self.confirm_ui_popup)
                        if self.game_state == "battle":
                            self.remove_ui_updater(self.cursor)

                    elif self.input_cancel_button.event_press or esc_press:
                        self.change_pause_update(False)
                        self.input_box.text_start("")
                        self.input_popup = None
                        self.remove_ui_updater(self.input_ui_popup, self.confirm_ui_popup)

                else:
                    command = self.escmenu_process(esc_press)
                    if command == "end_battle":  # return to city if not in city stage
                        return "throne"
                    elif command == "main_menu":  # return to main menu
                        return False

            elif self.game_state == "map":
                self.camera.update(self.shown_camera_pos, self.battle_camera, self.realtime_ui_updater)
                # self.frontground_stage.update(self.shown_camera_pos)  # update frontground stage last
                self.ui_drawer.draw(self.screen)  # draw the UI

                if self.city_map.selected_map:  # player select new map
                    selected_map = self.city_map.selected_map
                    self.city_map.selected_map = None
                    self.remove_ui_updater(self.cursor, self.city_map)
                    self.game_state = "battle"
                    return selected_map
                elif self.player_key_press[self.main_player]["Special"] or esc_press:
                    self.remove_ui_updater(self.cursor, self.city_map)
                    self.game_state = "battle"

            display.update()  # update game display, draw everything
            self.clock.tick(1000)  # clock update even if self pause

    def add_ui_updater(self, *args):
        self.ui_updater.add(*args)
        self.ui_drawer.add(*args)

    def remove_ui_updater(self, *args):
        self.ui_updater.remove(*args)
        self.ui_drawer.remove(*args)

    def exit_battle(self):
        # self.ui_updater.clear(self.screen)  # clear all sprite
        # self.battle_camera.clear(self.screen)  # clear all sprite

        # remove menu and ui
        self.remove_ui_updater(self.battle_menu_button, self.esc_slider_menu.values(),
                               self.esc_value_boxes.values(), self.esc_option_text.values(),
                               self.stage_translation_text_popup, self.player_char_base_interfaces.values(),
                               self.player_char_interfaces.values())

        for key, value in self.player_objects.items():
            self.player_portraits[key].reset_value()
        self.realtime_ui_updater.remove(self.player_portraits.values(), self.player_wheel_uis.values())

        self.music_left.stop()
        self.music_right.stop()

        # remove all reference from battle object
        self.players = {}
        self.player_objects = {}

        if self.score_board:
            clean_object(self.score_board)
        self.helper = None
        self.score_board = None
        self.main_player_object = None

        self.speech_prompt.clear()  # clear speech prompt from updater to avoid being deleted

        clean_group_object((self.all_chars, self.effect_updater, self.weather_matters))

        self.sound_effect_queue = {}

        self.battle_stage.clear_image()
        self.frontground_stage.clear_image()

        self.drama_timer = 0  # reset drama text popup
        self.realtime_ui_updater.remove(self.drama_text)

        for profile_num, profile in self.all_story_profiles.items():  # update each active player's profile stat
            if profile:
                profile["playtime"] += self.play_time
                profile["total scores"] += self.stage_score
                profile["total golds"] += self.stage_gold
                profile["total kills"] += self.player_kill[profile_num]
                profile["boss kills"] += self.player_boss_kill[profile_num]
