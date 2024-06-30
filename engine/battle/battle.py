import sys
import time
from random import choice, randint
from copy import deepcopy
from os import path
from math import sin, cos, radians

import pygame
from pygame import Vector2, display, mouse, sprite, Surface, JOYDEVICEADDED, JOYDEVICEREMOVED
from pygame.locals import *
from pygame.mixer import Sound, Channel

from engine.camera.camera import Camera
from engine.character.character import Character
from engine.drama.drama import TextDrama
from engine.effect.effect import Effect
from engine.stage.stage import Stage
from engine.stageobject.stageobject import StageObject
from engine.uibattle.uibattle import FPSCount, BattleCursor, YesNo, CharacterSpeechBox, CharacterInteractPrompt, \
    CourtBook, CityMap, CityMission, ScreenFade
from engine.uimenu.uimenu import TextPopup
from engine.utils.common import clean_object, clean_group_object
from engine.utils.data_loading import load_image, load_images
from engine.utils.text_making import number_to_minus_or_plus
from engine.weather.weather import Weather

script_dir = path.split(path.abspath(__file__))[0] + "/"

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

    from engine.battle.check_event import check_event
    check_event = check_event

    from engine.battle.cal_civil_war import cal_civil_war
    cal_civil_war = cal_civil_war

    from engine.battle.cal_shake_value import cal_shake_value
    cal_shake_value = cal_shake_value

    from engine.battle.camera_process import camera_process
    camera_process = camera_process

    from engine.battle.change_game_state import change_game_state
    change_game_state = change_game_state

    from engine.game.change_pause_update import change_pause_update
    change_pause_update = change_pause_update

    from engine.battle.common_process import common_process
    common_process = common_process

    from engine.battle.cutscene_player_input import cutscene_player_input
    cutscene_player_input = cutscene_player_input

    from engine.battle.drama_process import drama_process
    drama_process = drama_process

    from engine.battle.end_cutscene_event import end_cutscene_event
    end_cutscene_event = end_cutscene_event

    from engine.battle.escmenu_process import escmenu_process, back_to_battle_state
    back_to_battle_state = back_to_battle_state
    escmenu_process = escmenu_process

    from engine.battle.fix_camera import fix_camera
    fix_camera = fix_camera

    from engine.battle.increase_team_score import increase_team_score
    increase_team_score = increase_team_score

    from engine.battle.make_battle_ui import make_battle_ui
    make_battle_ui = make_battle_ui

    from engine.battle.make_esc_menu import make_esc_menu
    make_esc_menu = make_esc_menu

    from engine.battle.play_sound_effect import play_sound_effect
    play_sound_effect = play_sound_effect

    from engine.battle.spawn_character import spawn_character
    spawn_character = spawn_character

    from engine.battle.spawn_weather_matter import spawn_weather_matter
    spawn_weather_matter = spawn_weather_matter

    from engine.battle.state_battle_process import state_battle_process
    state_battle_process = state_battle_process
    state_process = state_battle_process

    from engine.battle.state_court_process import state_court_process
    state_court_process = state_court_process

    from engine.battle.state_map_process import state_map_process
    state_map_process = state_map_process

    from engine.battle.state_menu_process import state_menu_process
    state_menu_process = state_menu_process

    from engine.battle.state_reward_process import state_reward_process
    state_reward_process = state_reward_process

    from engine.battle.state_shop_process import state_shop_process
    state_shop_process = state_shop_process

    from engine.battle.shake_camera import shake_camera
    shake_camera = shake_camera

    from engine.battle.event_process import event_process
    event_process = event_process

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

    process_list = {"battle": state_battle_process, "menu": state_menu_process, "map": state_map_process,
                    "court": state_court_process,
                    "reward": state_reward_process, "shop": state_shop_process, "enchant": state_shop_process}

    def __init__(self, game):
        self.game = game
        Battle.battle = self

        # TODO LIST for full chapter 1
        # add skill/moveset unlockable for enemy (charisma)
        # add enemy trap with delay and cycle
        # add one more playable char
        # add online/lan multiplayer?
        # court structure interface, mission select, side mission, feast system
        # add ranking record system
        # add pvp mode, follower recruit unlock with all save story progress
        # mission 2: 4 scenes, 4 enemies (hound master, hound, bandit ranger, rabbit killer appear with 1b)
        # add sound type to skill/move for collide and damage sound check
        # move loading sprite to when start character based on chapter
        # find way to increase speech text size
        # finish main menu

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
        self.screen_width = self.screen_rect.width
        self.screen_height = self.screen_rect.height
        self.corner_screen_width = game.corner_screen_width
        self.corner_screen_height = game.corner_screen_height

        Battle.battle_camera_size = (self.screen_width, self.screen_height)
        Battle.battle_camera_min = (self.screen_width, 0)
        Battle.battle_camera_max = (self.screen_width - 1, self.screen_height - 1)
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

        # Text popup
        self.text_popup = TextPopup()
        self.stage_translation_text_popup = TextPopup()  # popup box for text that translate background script

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
        self.stage_music_pool = {}  # pool for music already converted to pygame Sound

        self.weather_screen_adjust = self.screen_width / self.screen_height  # for weather sprite spawn position
        self.right_corner = self.screen_width - (5 * self.screen_scale[0])
        self.bottom_corner = self.screen_height - (5 * self.screen_scale[1])

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
        self.all_team_character = {0: sprite.Group(), 1: sprite.Group(), 2: sprite.Group(),
                                   3: sprite.Group(), 4: sprite.Group()}
        self.all_team_enemy = {0: sprite.Group(), 1: sprite.Group(), 2: sprite.Group(),
                               3: sprite.Group(), 4: sprite.Group()}  # for AI combo check
        self.all_team_enemy_check = {0: sprite.Group(), 1: sprite.Group(), 2: sprite.Group(),
                                     3: sprite.Group(), 4: sprite.Group()}  # for victory check
        self.all_team_enemy_part = {0: sprite.Group(), 1: sprite.Group(), 2: sprite.Group(),
                                    3: sprite.Group(), 4: sprite.Group()}
        self.all_team_drop = {0: sprite.Group(), 1: sprite.Group(), 2: sprite.Group(),
                              3: sprite.Group(), 4: sprite.Group()}
        self.player_damage = {1: 0, 2: 0, 3: 0, 4: 0}
        self.player_kill = {1: 0, 2: 0, 3: 0, 4: 0}
        self.player_boss_kill = {1: 0, 2: 0, 3: 0, 4: 0}
        self.play_time = 0
        self.stage_gold = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        self.stage_score = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        self.last_resurrect_stage_score = {1: 5000, 2: 5000, 3: 5000, 4: 5000, 5: 5000}
        self.reserve_resurrect_stage_score = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        self.players = {}  # player
        self.player_objects = {}
        self.player_team = {}
        self.players_control_input = {1: None, 2: None, 3: None, 4: None}
        self.existing_playable_characters = []
        self.later_enemy = {}
        self.city_mode = False
        self.game_state = "battle"
        self.esc_menu_mode = "menu"

        self.helper = None  # helper character that can be moved via cursor
        self.score_board = None

        self.best_depth = display.mode_ok(self.screen_rect.size, self.game.window_style,
                                          32)  # Set the display mode
        Battle.screen = display.set_mode(self.screen_rect.size, self.game.window_style,
                                         self.best_depth)  # set up self screen

        # Assign battle variable to some classes
        Character.sound_effect_pool = self.sound_effect_pool
        Effect.sound_effect_pool = self.sound_effect_pool

        # Create battle ui
        cursor_images = load_images(self.data_dir, subfolder=("ui", "cursor_battle"))  # no need to scale cursor
        self.main_player_battle_cursor = BattleCursor(cursor_images, self.player_key_control[1])
        self.current_cursor = self.main_player_battle_cursor

        self.fps_count = FPSCount(self)  # FPS number counter
        if self.game.show_fps:
            self.realtime_ui_updater.add(self.fps_count)

        battle_ui_images = self.game.battle_ui_images
        CharacterSpeechBox.images = battle_ui_images

        self.screen_fade = ScreenFade()
        self.speech_prompt = CharacterInteractPrompt(battle_ui_images["button_weak"])
        self.court_book = CourtBook(load_images(self.data_dir, screen_scale=self.screen_scale,
                                                subfolder=("ui", "court_ui"), key_file_name_readable=True))
        self.city_map = CityMap(load_images(self.data_dir, screen_scale=self.screen_scale,
                                            subfolder=("ui", "map_select_ui")))
        self.city_mission = CityMission(load_images(self.data_dir, screen_scale=self.screen_scale,
                                                    subfolder=("ui", "mission_select_ui")))

        battle_ui_dict = self.make_battle_ui(battle_ui_images)

        self.decision_select = YesNo(battle_ui_images)

        self.player_portraits = battle_ui_dict["player_portraits"]
        self.player_wheel_uis = battle_ui_dict["player_wheel_uis"]
        self.player_trainings = battle_ui_dict["player_trainings"]

        self.current_weather = Weather(1, 0, 0, None)

        TextDrama.images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                       subfolder=("ui", "popup_ui", "drama_text"))
        self.drama_text = TextDrama(self)  # message at the top of screen that show up for important event

        # Battle ESC menu
        esc_menu_dict = self.make_esc_menu()

        self.player_char_base_interfaces = esc_menu_dict["player_char_base_interfaces"]
        self.battle_menu_button = esc_menu_dict["battle_menu_button"]
        self.esc_option_menu_button = esc_menu_dict["esc_option_menu_button"]
        self.esc_slider_menu = esc_menu_dict["esc_slider_menu"]
        self.esc_value_boxes = esc_menu_dict["esc_value_boxes"]
        self.esc_option_text = esc_menu_dict["volume_texts"]
        self.dialogue_box = esc_menu_dict["dialogue_box"]
        self.esc_dialogue_button = esc_menu_dict["esc_dialogue_button"]

        # Create the game camera
        self.main_player = 1  # TODO need to add recheck later for when resurrect count run out
        self.main_player_object = None
        self.camera_mode = "Follow"  # mode of game camera, follow player character or free observation
        self.camera_pos = Vector2(500, 500)  # camera pos on stage
        self.base_camera_begin = (self.camera_pos[0] - self.battle_camera_center[0]) / self.screen_scale[0]
        self.base_camera_end = (self.camera_pos[0] + self.battle_camera_center[0]) / self.screen_scale[0]

        self.shown_camera_pos = self.camera_pos  # pos of camera shown to player, in case of screen shaking or other effects

        self.clock_time = 0
        self.true_dt = 0
        self.dt = 0  # Realtime used for time calculation
        self.ui_dt = 0  # Realtime used for ui timer
        self.screen_shake_value = 0  # count for how long to shake camera

        Battle.camera = Camera(self.screen, self.battle_camera_size)

        self.base_cursor_pos = [0, 0]  # mouse pos on the map based on camera position

        self.show_cursor_timer = 0

        # music player
        self.current_music = None
        self.music_left = Channel(1)
        self.music_left.set_volume(self.play_music_volume, 0)
        self.music_right = Channel(2)
        self.music_right.set_volume(0, self.play_music_volume)

        # Battle map object
        Stage.image = Surface.subsurface(self.camera.image, (0, 0, self.camera.image.get_width(),
                                                             self.camera.image.get_height()))
        Stage.camera_center_y = self.battle_camera_center[1]
        self.battle_stage = Stage(1)
        self.frontground_stage = Stage(100000000000000000000000000000000000000000000000)
        self.empty_stage_image = load_image(self.data_dir, self.screen_scale, "empty.png",
                                            ("map", "stage"))  # no scaling yet

        Effect.battle_stage = self.battle_stage
        Character.battle_stage = self.battle_stage  # add battle map to character class
        self.base_stage_start = 0
        self.stage_start = 0
        self.base_stage_end = 0
        self.stage_end = 0
        self.execute_cutscene = None
        self.submit_cutscene = None
        self.start_cutscene = []
        self.reach_scene_event_list = {}  # cutscene that play when camera reach scene
        self.player_interact_event_list = {}
        self.base_stage_end_list = {}
        self.stage_end_list = {}
        self.end_delay = 0  # delay until stage end and continue to next one
        self.spawn_delay_timer = {}
        self.cutscene_timer = 0
        self.cutscene_finish_camera_delay = 0  # delay before camera can move again after cutscene
        self.survive_timer = 0
        self.stage_end_choice = False
        self.stage_scene_lock = {}
        self.lock_objective = None
        self.next_lock = None
        self.cutscene_playing = None
        self.cutscene_playing_data = None

    def prepare_new_stage(self, chapter, mission, stage, players, scene):
        for message in self.inner_prepare_new_stage(chapter, mission, stage, players, scene):
            self.game.error_log.write("Start Stage:" + str(chapter) + "." + str(mission) + "." + str(stage))
            print(message, end="")

    def inner_prepare_new_stage(self, chapter, mission, stage, players, scene):
        """Setup stuff when start new stage"""
        self.chapter = chapter
        self.mission = mission
        self.stage = stage
        self.scene = scene

        self.players = players
        self.existing_playable_characters = [value["ID"] for value in self.players.values()]

        # Stop any current music
        self.current_music = None
        self.music_left.stop()
        self.music_right.stop()

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
        stage_event_data = deepcopy(stage_data["event"])
        loaded_item = []
        later_enemy = {}
        self.stage_scene_lock = {}
        self.lock_objective = None
        self.stage_end_choice = False
        self.next_lock = None
        self.cutscene_playing = None
        self.cutscene_playing_data = None
        self.base_stage_end = 0  # for object pos
        self.base_stage_start = 0  # for camera pos
        self.stage_start = self.battle_camera_center[0]
        self.stage_end = -self.battle_camera_center[0]
        self.execute_cutscene = None
        self.submit_cutscene = None
        self.decision_select.selected = None
        self.end_delay = 0
        self.start_cutscene = []
        self.reach_scene_event_list = {}
        self.player_interact_event_list = {}
        self.base_stage_end_list = {}
        self.stage_end_list = {}
        self.stage_music_pool = {}
        self.speech_prompt.clear()

        first_lock = None
        for value in stage_object_data.values():
            if value["Object"] not in loaded_item:  # load image
                if value["Type"] == "stage":  # type of object with image data to load
                    if value["Type"] == "stage":  # load background stage
                        image = self.empty_stage_image

                        if path.exists(path.join(self.data_dir, "map", "stage", value["Object"] + ".png")):
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
        for this_group in self.all_team_enemy_check.values():
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
        if self.stage == "0":  # city stage not add helper
            add_helper = False
        self.last_char_id = 0
        self.spawn_character(self.players, start_enemy, add_helper=add_helper)

        for player in self.player_objects:
            self.realtime_ui_updater.add(self.player_portraits[player])
            self.player_portraits[player].add_char_portrait(self.player_objects[player])
            if self.stage == "training":
                self.realtime_ui_updater.add(self.player_trainings[player])

        self.main_player_object = self.player_objects[self.main_player]
        if stage_event_data:
            self.stage_music_pool = {key: Sound(self.music_pool[key]) for
                                     key in stage_event_data["music"]}
            for trigger, value in stage_event_data.items():
                if ("once" not in value or tuple(value["once"].keys())[0] + self.chapter + self.mission + self.stage
                    not in self.main_story_profile["story event"]) and \
                        ("story choice" not in value or
                         (value["story choice"] == value["story choice"].split("_")[0] + "_" + self.main_story_profile["story choice"][value["story choice"].split("_")[0]])):
                    # event with once condition will not be played again if already play once for the save profile
                    # also check parent event that depend on story choice
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
                                    self.start_cutscene = value3
                    elif "interact" in trigger:
                        for key, value2 in value.items():
                            char_found = None
                            for char in self.all_chars:
                                if char.game_id == key:
                                    char_found = char
                                    break
                            for key3, value3 in value2.items():
                                if "/Any/" in value3[0]["ID"] or "/" + self.main_player_object.char_id + "/" in \
                                        value3[0][
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
                                        wind_direction = randint(0, 359)
                                        if "strength" in value3[0]["Property"]:
                                            weather_strength = value3[0]["Property"]["strength"]
                                        if "wind direction" in value3[0]["Property"]:
                                            wind_direction = value3[0]["Property"]["wind direction"]
                                        self.reach_scene_event_list[key]["weather"] = (
                                        value3[0]["Object"], wind_direction, weather_strength)
                                    elif value3[0]["Type"] == "music":
                                        if value3[0]["Object"] != "stop":
                                            self.reach_scene_event_list[key]["music"] = str(value3[0]["Object"])
                                        else:
                                            self.reach_scene_event_list[key]["music"] = None
                                    elif value3[0]["Type"] == "sound":
                                        if "sound" not in self.reach_scene_event_list[key]:
                                            self.reach_scene_event_list[key]["sound"] = []
                                        # sound effect must have sound distance and shake value in property
                                        self.reach_scene_event_list[key]["sound"].append(
                                            (choice(self.sound_effect_pool[str(value3[0]["Object"])]),
                                             value3[0]["Property"]["sound distance"],
                                             value3[0]["Property"]["shake value"]))

                    elif "execute" in trigger:
                        for key, value2 in value.items():
                            self.execute_cutscene = value2
                    elif "submit" in trigger:
                        for key, value2 in value.items():
                            self.submit_cutscene = value2
        yield set_done_load()

    def run_game(self):
        # Create Starting Values
        self.input_popup = None  # no popup asking for user text input state
        self.drama_text.queue = []  # reset drama text popup queue

        if self.main_story_profile["interface event queue"]["inform"]:
            for item in self.main_story_profile["interface event queue"]["inform"].copy():
                self.drama_text.queue.append(item)
                self.main_story_profile["interface event queue"]["inform"].remove(item)

        self.camera_mode = self.start_camera_mode

        self.camera_pos = Vector2(500, self.battle_camera_center[1])
        self.fix_camera()

        self.shown_camera_pos = self.camera_pos

        self.screen_shake_value = 0
        self.cutscene_timer = 0
        self.cutscene_finish_camera_delay = 0
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
        self.stage_gold = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        self.stage_score = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        self.last_resurrect_stage_score = {1: 5000, 2: 5000, 3: 5000, 4: 5000, 5: 5000}  # start at 5000 to get next resurrect reserve
        self.reserve_resurrect_stage_score = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        self.base_cursor_pos = [0, 0]  # mouse pos on the map based on camera position
        mouse.set_pos(Vector2(self.camera_pos[0], 140 * self.screen_scale[1]))  # set cursor to midtop screen

        self.player_key_control = {player: self.config["USER"]["control player " + str(player)] for player in
                                   self.game.player_list}
        self.player_control_keyboard = {player: True for player in self.player_key_control if
                                        self.player_key_control[player] == "keyboard"}
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

        if self.start_cutscene:
            # play start cutscene
            self.cutscene_playing = deepcopy(self.start_cutscene)
            self.cutscene_playing_data = self.start_cutscene
            self.start_cutscene = []

        frame = 0
        while True:  # battle running
            frame += 1

            if frame % 30 == 0 and hasattr(self.game, "profiler"):  # Remove for stable release, along with dev key
                self.game.profiler.refresh()
                frame = 0

            key_state = pygame.key.get_pressed()
            esc_press = False
            self.cursor.scroll_down = False
            self.cursor.scroll_up = False

            self.player_key_press = {key: dict.fromkeys(self.player_key_press[key], False) for key in
                                     self.player_key_press}
            self.player_key_hold = {key: dict.fromkeys(self.player_key_hold[key], False) for key in
                                    self.player_key_hold}

            self.clock_time = self.clock.get_time()
            self.true_dt = self.clock_time / 1000  # dt before game_speed
            self.play_time += self.true_dt

            for player in self.player_objects:  # only check for active player
                if self.player_key_control[player] == "keyboard":
                    for key in self.player_key_press[player]:  # check for key holding
                        if type(self.player_key_bind[player][key]) == int and \
                                key_state[self.player_key_bind[player][key]]:
                            self.player_key_hold[player][key] = True
                else:
                    player_key_bind_name = self.player_key_bind_name[player]
                    # joystick = self.player_joystick[player]  # TODO rework this later, change id to object
                    for joystick_id, joystick in self.joysticks.items():  # TODO find way so no need to loop this
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
                                        vec = Vector2(joystick.get_axis(2), joystick.get_axis(3))
                                        radius, angle = vec.as_polar()
                                        adjusted_angle = (angle + 90) % 360
                                        new_pos = Vector2(self.current_cursor.pos[0] +
                                                          (self.clock_time * sin(radians(adjusted_angle))),
                                                          self.current_cursor.pos[1] -
                                                          (self.clock_time * cos(radians(adjusted_angle))))
                                        if new_pos[0] < 0:
                                            new_pos[0] = 0
                                        elif new_pos[0] > self.corner_screen_width:
                                            new_pos[0] = self.corner_screen_width
                                        if new_pos[1] < 0:
                                            new_pos[1] = 0
                                        elif new_pos[1] > self.corner_screen_height:
                                            new_pos[1] = self.corner_screen_height
                                        mouse.set_pos(new_pos)
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
                            break

            self.base_cursor_pos = Vector2(
                (self.main_player_battle_cursor.pos[0] - self.battle_camera_center[0] + self.camera_pos[0]),
                (self.main_player_battle_cursor.pos[1] - self.battle_camera_center[1] + self.camera_pos[
                    1]))  # mouse pos on the map based on camera position

            for event in pygame.event.get():  # get event that happen
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 4:  # Mouse scroll down
                        self.cursor.scroll_up = True
                    elif event.button == 5:  # Mouse scroll up
                        self.cursor.scroll_down = True

                elif event.type == QUIT:  # quit game
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
                    for player in self.player_control_keyboard:
                        if event_key_press in self.player_key_bind_name[player]:  # check for key press
                            self.player_key_press[player][self.player_key_bind_name[player][event_key_press]] = True

                    # FOR DEVELOPMENT
                    if event.key == K_F1:
                        self.drama_text.queue.append(("Hello and welcome to showcase video", "Cannon Shot Medium"))
                    elif event.key == K_F3:
                        for enemy in self.all_team_enemy[2]:
                            if not enemy.invincible and int(enemy.base_pos[0] / 1920) in \
                                    (self.battle_stage.spawn_check_scene - 1, self.battle_stage.spawn_check_scene):
                                enemy.health = 1
                    elif event.key == K_F4:
                        for character in self.player_objects.values():
                            character.cal_loss(None, 0, (50, -200), character.angle, (0, 0), False)
                    elif event.key == K_F5:
                        for enemy in self.all_chars:
                            if not enemy.invincible and enemy.team == 1:
                                enemy.health = 0
                        CharacterSpeechBox(self.player_objects[self.main_player],
                                           "Die")
                    elif event.key == K_F6:
                        for enemy in self.all_team_enemy[1]:
                            if not enemy.invincible and int(enemy.base_pos[0] / 1920) in \
                                    (self.battle_stage.spawn_check_scene - 1, self.battle_stage.spawn_check_scene):
                                enemy.health = 0
                        CharacterSpeechBox(self.player_objects[self.main_player],
                                           "Die")
                    elif event.key == K_F7:  # clear profiler
                        if hasattr(self.game, "profiler"):
                            self.game.profiler.clear()
                    elif event.key == K_F8:  # show/hide profiler
                        if not hasattr(self.game, "profiler"):
                            self.game.setup_profiler()
                        self.game.profiler.switch_show_hide()
                    # elif event_key_press == pygame.K_k:
                    #     if self.players:
                    #         for unit in self.players.alive_leader_follower:
                    #             unit.health -= unit.health
                    # self.players.health = 0

                elif event.type == JOYDEVICEADDED:
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

                elif event.type == JOYDEVICEREMOVED:
                    # Player unplug joystick
                    del self.joysticks[event.instance_id]
                    del self.joystick_name[event.instance_id]
                    for key, value in self.player_joystick.copy().items():
                        if value == event.instance_id:
                            self.player_joystick.pop(key)
                            self.joystick_player.pop(value)
                            break

            if not self.music_left.get_busy() and self.current_music:  # change if music finish playing
                self.music_left.play(self.current_music, fade_ms=100)
                self.music_left.set_volume(self.play_music_volume, 0)
                self.music_right.play(self.current_music, fade_ms=100)
                self.music_right.set_volume(0, self.play_music_volume)

            if self.player_key_press[self.main_player]["Menu/Cancel"]:
                # open/close menu
                esc_press = True

            self.ui_updater.update()  # update ui before more specific update

            return_state = self.state_process(esc_press)  # run code based on current state
            if return_state is not None:
                return return_state

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

        for key in self.player_objects:
            self.player_portraits[key].reset_value()
        self.realtime_ui_updater.remove(self.player_portraits.values(), self.player_wheel_uis.values(),
                                        self.player_trainings.values())

        for helper in self.player_trainings.values():
            helper.reset()
        self.music_left.stop()
        self.music_right.stop()
        self.stage_music_pool = {}
        self.current_music = None

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
        self.remove_ui_updater(self.drama_text)
