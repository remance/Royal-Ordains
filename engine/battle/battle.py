import glob
import os
import sys
import time
from math import sin, cos, radians
from random import randint

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
from engine.uibattle.uibattle import FPSCount, BattleCursor, YesNo, CharacterSpeechBox
from engine.utils.common import clean_group_object
from engine.utils.data_loading import load_image, load_images
from engine.utils.text_making import number_to_minus_or_plus
from engine.weather.weather import Weather

script_dir = os.path.split(os.path.abspath(__file__))[0] + "/"


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

    from engine.battle.fix_camera import fix_camera
    fix_camera = fix_camera

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

    original_fall_gravity = 900

    def __init__(self, game):
        self.game = game
        Battle.battle = self

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
        self.all_damage_effects = game.all_damage_effects
        self.effect_updater = game.effect_updater
        self.realtime_ui_updater = game.realtime_ui_updater

        self.cursor = game.cursor
        self.joysticks = game.joysticks
        self.joystick_name = game.joystick_name

        self.button_ui = game.button_ui

        self.text_popup = game.text_popup
        self.esc_text_popup = game.esc_text_popup

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

        self.sound_effect_pool = game.sound_effect_pool
        self.sound_effect_queue = {}

        self.weather_screen_adjust = self.screen_rect.width / self.screen_rect.height  # for weather sprite spawn position
        self.right_corner = self.screen_rect.width - (5 * self.screen_scale[0])
        self.bottom_corner = self.screen_rect.height - (5 * self.screen_scale[1])

        # data specific to module
        self.character_data = self.game.character_data

        self.battle_map_data = self.game.battle_map_data
        self.weather_data = self.battle_map_data.weather_data
        self.weather_matter_images = self.battle_map_data.weather_matter_images
        self.weather_list = self.battle_map_data.weather_list
        self.stage_reward = self.battle_map_data.stage_reward
        self.reward_list = self.battle_map_data.reward_list

        self.character_animation_data = self.game.character_animation_data
        self.body_sprite_pool = self.game.body_sprite_pool
        self.effect_animation_pool = self.game.effect_animation_pool
        self.language = self.game.language
        self.localisation = self.game.localisation

        self.game_speed = 1
        self.day_time = "Day"
        self.old_day_time = self.day_time
        self.all_team_character = {1: pygame.sprite.Group(), 2: pygame.sprite.Group(),
                                   3: pygame.sprite.Group(), 4: pygame.sprite.Group()}
        self.all_team_enemy = {1: pygame.sprite.Group(), 2: pygame.sprite.Group(),
                               3: pygame.sprite.Group(), 4: pygame.sprite.Group()}
        self.all_team_enemy_part = {1: pygame.sprite.Group(), 2: pygame.sprite.Group(),
                                    3: pygame.sprite.Group(), 4: pygame.sprite.Group()}
        self.all_team_drop = {1: pygame.sprite.Group(), 2: pygame.sprite.Group(),
                              3: pygame.sprite.Group(), 4: pygame.sprite.Group()}

        self.players = {}  # player
        self.player_team_followers = {}
        self.player_objects = {}
        self.players_control_input = {1: None, 2: None, 3: None, 4: None}
        self.later_enemy = {}

        self.empty_portrait = pygame.Surface((150 * self.screen_scale[0], 150 * self.screen_scale[1]), pygame.SRCALPHA)
        pygame.draw.circle(self.empty_portrait, (20, 20, 20),
                           (self.empty_portrait.get_width() / 2, self.empty_portrait.get_height() / 2),
                           self.empty_portrait.get_width() / 2)

        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, self.game.window_style,
                                                 32)  # Set the display mode
        Battle.screen = pygame.display.set_mode(self.screen_rect.size, self.game.window_style,
                                                self.best_depth)  # set up self screen

        # Assign battle variable to some classes
        Character.sound_effect_pool = self.sound_effect_pool
        Effect.sound_effect_pool = self.sound_effect_pool

        # Create battle ui
        cursor_images = load_images(self.data_dir, subfolder=("ui", "cursor_battle"))  # no need to scale cursor
        self.player_1_battle_cursor = BattleCursor(cursor_images, self.player_key_control[1])

        self.fps_count = FPSCount(self)  # FPS number counter
        if self.game.show_fps:
            self.realtime_ui_updater.add(self.fps_count)

        battle_ui_images = load_images(self.data_dir, screen_scale=self.screen_scale, subfolder=("ui", "battle_ui"))
        CharacterSpeechBox.images = battle_ui_images

        battle_ui_dict = make_battle_ui(battle_ui_images)

        self.decision_select = YesNo(battle_ui_images)

        self.time_ui = battle_ui_dict["time_ui"]
        self.time_number = battle_ui_dict["time_number"]
        self.realtime_ui_updater.add((self.time_ui, self.time_number))
        self.player_1_portrait = battle_ui_dict["player_1_portrait"]
        self.player_2_portrait = battle_ui_dict["player_2_portrait"]
        self.player_3_portrait = battle_ui_dict["player_3_portrait"]
        self.player_4_portrait = battle_ui_dict["player_4_portrait"]
        self.player_portraits = (self.player_1_portrait, self.player_2_portrait,
                                 self.player_3_portrait, self.player_4_portrait)
        self.current_weather = Weather(self.time_ui, 4, 0, 0, None)

        TextDrama.images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                       subfolder=("ui", "popup_ui", "drama_text"))
        self.drama_text = TextDrama(
            self.battle_camera_size)  # message at the top of screen that show up for important event

        # Battle ESC menu
        esc_menu_dict = make_esc_menu(self.master_volume, self.music_volume, self.voice_volume, self.effect_volume)
        self.battle_menu = esc_menu_dict["battle_menu"]
        self.battle_menu_button = esc_menu_dict["battle_menu_button"]
        self.esc_option_menu_button = esc_menu_dict["esc_option_menu_button"]
        self.esc_slider_menu = esc_menu_dict["esc_slider_menu"]
        self.esc_value_boxes = esc_menu_dict["esc_value_boxes"]
        self.esc_option_text = esc_menu_dict["volume_texts"]

        # Create the game camera
        self.first_player = 1  # TODO need to add recheck later for when resurrect count run out
        self.camera_mode = "Follow"  # mode of game camera, follow player character or free observation
        self.camera_pos = Vector2(500, 500)  # camera pos on stage
        self.base_camera_begin = (self.camera_pos[0] - self.battle_camera_center[0]) / self.screen_scale[0]
        self.base_camera_end = (self.camera_pos[0] + self.battle_camera_center[0]) / self.screen_scale[0]

        self.shown_camera_pos = self.camera_pos  # pos of camera shown to player, in case of screen shaking or other effects

        self.screen_shake_value = 0  # count for how long to shake camera

        Battle.camera = Camera(self.screen, self.battle_camera_size)

        self.base_cursor_pos = [0, 0]  # mouse pos on the map based on camera position
        self.command_cursor_pos = [0, 0]  # with zoom and screen scale for character command

        self.show_cursor_timer = 0

        # music player
        self.music_left = pygame.mixer.Channel(0)
        self.music_left.set_volume(self.play_music_volume, 0)
        self.music_right = pygame.mixer.Channel(1)
        self.music_right.set_volume(0, self.play_music_volume)

        # Battle map object
        Stage.image = pygame.Surface.subsurface(self.camera.image,
                                                (0, 0, self.camera.image.get_width(),
                                                 self.camera.image.get_height()))
        self.battle_stage = Stage(1)
        self.frontground_stage = Stage(100000000000000000000000000000000000000000000000)

        Effect.battle_stage = self.battle_stage
        Character.battle_stage = self.battle_stage  # add battle map to character class
        self.base_stage_start = 0
        self.stage_start = 0
        self.base_stage_end = 0
        self.stage_end = 0
        self.base_stage_end_list = {}
        self.stage_end_list = {}
        self.stage_goal = 0
        self.end_delay = 0  # delay until stage end and continue to next one
        self.spawn_delay_timer = {}
        self.survive_timer = 0
        self.stage_end_choice = False

    def prepare_new_stage(self, chapter, mission, stage, players):

        for message in self.inner_prepare_new_stage(chapter, mission, stage, players):
            print(message, end="")

    def inner_prepare_new_stage(self, chapter, mission, stage, players):
        """Setup stuff when start new stage"""
        self.chapter = chapter
        self.chapter_sprite_ver = str(chapter)
        self.mission = mission
        self.stage = stage

        self.players = players

        # Random music played from list
        yield set_start_load(self, "music")
        if pygame.mixer:
            self.SONG_END = pygame.USEREVENT + 1
            self.music_list = glob.glob(os.path.join(self.data_dir, "sound", "music", "battle", "*.ogg"))
            picked_music = randint(0, len(self.music_list) - 1)

            music = pygame.mixer.Sound(self.music_list[picked_music])

            self.music_left.play(music, fade_ms=100)
            self.music_left.set_volume(self.play_music_volume, 0)
            self.music_right.play(music, fade_ms=100)
            self.music_right.set_volume(0, self.play_music_volume)

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
        yield set_done_load()

        yield set_start_load(self, "map events")
        # map_event_text = self.localisation.grab_text(("map", str(chapter), str(mission), str(stage), "eventlog"))
        # map_event = self.game.preset_map_data[chapter][mission][stage]["eventlog"]

        self.time_number.start_setup()
        yield set_done_load()

        yield set_start_load(self, "stage setup")
        self.current_weather.__init__(self.time_ui, 0, randint(0, 359), 0,
                                      self.weather_data)  # start weather with random

        stage_data = self.game.preset_map_data[chapter][mission][stage]
        stage_object_data = stage_data["data"]
        loaded_item = []
        later_enemy = {}
        self.stage_scene_lock = {}
        self.stage_end_choice = False
        for value in stage_object_data.values():
            if value["Object"] not in loaded_item:  # load image
                if "stage" in value["Type"]:
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
            elif "endpoint" in value["Type"]:
                self.stage_goal = value["POS"]
            elif "endchoice" in value["Type"]:
                self.stage_end_choice = True
            elif "lock" in value["Type"]:
                self.stage_scene_lock[value["POS"]] = value["Object"]

            elif value["Type"] == "object":
                StageObject(value["Object"], value["POS"])

        self.next_lock = None
        self.lock_objective = "none"
        if self.stage_scene_lock:
            self.next_lock = tuple(self.stage_scene_lock.keys())[0]
        self.base_stage_end = 0  # for object pos
        self.base_stage_start = 0  # for camera pos
        self.stage_start = self.battle_camera_center[0]
        self.stage_end = -self.battle_camera_center[0]
        self.base_stage_end_list = {}
        self.stage_end_list = {}
        for key, value in self.battle_stage.data.items():
            self.base_stage_end += 1920  # 1 scene width size always 1920
            self.stage_end += self.battle_stage.images[value].get_width()
            self.base_stage_end_list[key] = self.base_stage_end
            self.stage_end_list[key] = self.stage_end

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

        self.spawn_delay_timer = {}

        start_enemy = [item for item in stage_data["character"] if "camera_stage" not in item["Arrive Condition"]]
        self.later_enemy = {stage: [item for item in stage_data["character"] if
                                    "camera_stage" in item["Arrive Condition"] and
                                    int(item["POS"][0] / 1920) + 1 == stage] for stage in later_enemy}
        for stage, value in self.later_enemy.items():  # rearrange arrival list based on delay
            new_value = {}
            self.spawn_delay_timer[stage] = 0
            for item in value:
                if any("delay" in item2 for item2 in item["Arrive Condition"]):  # character has delay for arrival
                    for condition in item["Arrive Condition"]:
                        if "delay" in condition:
                            timer = float(condition.split("/")[-1])
                            if timer not in new_value:
                                new_value[timer] = []
                            new_value[timer].append(item)
                else:
                    if 0 not in new_value:
                        new_value[0] = []
                    new_value[0].append(item)
            self.later_enemy[stage] = new_value

        self.setup_battle_character(self.players, start_enemy)

        self.player_objects = {key: value["Object"] for key, value in self.players.items()}

        for player in self.player_objects:
            self.realtime_ui_updater.add(self.player_portraits[player - 1])

        yield set_done_load()

        # yield set_start_load(self, "character animation")
        # who_todo = []
        # for this_char in self.character_updater:
        #     new_check = [item[0] for item in who_todo]
        #     if this_char.sprite_id not in new_check:
        #         who_todo.append([this_char.sprite_id, this_char.sprite_ver, this_char.sprite_size, this_char.mode_list])
        # self.character_animation_pool = self.game.create_character_sprite_pool(who_todo)
        # yield set_done_load()

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
        self.first_player = tuple(self.player_objects.keys())[0]
        self.camera_pos = Vector2(500, self.battle_camera_center[1])
        self.fix_camera()

        self.shown_camera_pos = self.camera_pos

        self.player_unit_input_delay = 0
        self.text_delay = 0
        self.screen_shake_value = 0
        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0  # This is timer for combat related function, use self time (realtime * game_speed)
        self.dt = 0  # Realtime used for time calculation
        self.ui_dt = 0  # Realtime used for ui timer
        self.weather_spawn_timer = 0
        self.show_cursor_timer = 0
        self.player_1_battle_cursor.shown = True
        self.player_score = 0
        self.player_damage = {1: 0, 2: 0, 3: 0, 4: 0}

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
        self.realtime_ui_updater.add(self.player_1_battle_cursor)
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
                                                self.player_1_battle_cursor.pos[0] + (
                                                        self.true_dt * 1000 * sin(radians(adjusted_angle))),
                                                self.player_1_battle_cursor.pos[1] - (
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
                (self.player_1_battle_cursor.pos[0] - self.battle_camera_center[0] + self.camera_pos[0]),
                (self.player_1_battle_cursor.pos[1] - self.battle_camera_center[1] + self.camera_pos[
                    1]))  # mouse pos on the map based on camera position
            self.command_cursor_pos = Vector2(self.base_cursor_pos[0] / self.screen_scale[0],
                                              self.base_cursor_pos[1] / self.screen_scale[1])  # with screen scale

            for event in pygame.event.get():  # get event that happen
                if event.type == QUIT:  # quit game
                    if self.game_state != "menu":  # open menu first before add popup
                        self.game_state = "menu"
                        self.add_ui_updater(self.battle_menu,
                                            self.battle_menu_button,
                                            self.esc_text_popup)  # add menu and its buttons to drawer
                        self.add_ui_updater(self.cursor)
                    self.input_popup = ("confirm_input", "quit")
                    self.input_ui.change_instruction("Quit Game?")
                    self.add_ui_updater(self.confirm_ui_popup, self.cursor)

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
                        CharacterSpeechBox(self.player_objects[1], "test speech well done")
                    # elif event.key == K_F3:
                    #     self.drama_text.queue.append("New Medieval art style as shown in previous videos")
                    # elif event.key == K_F4:
                    #     self.drama_text.queue.append("Few more updates until demo release")
                    # elif event.key == K_F5:
                    #     self.drama_text.queue.append("Rushed to the English line, he fought valiantly alone")
                    # elif event.key == K_F6:
                    #     self.drama_text.queue.append("The Saxon swarmed him and left him death, that they shall atone")
                    elif event.key == K_F7:  # clear profiler
                        if hasattr(self.game, "profiler"):
                            self.game.profiler.clear()
                    elif event.key == K_F8:  # show/hide profiler
                        if not hasattr(self.game, "profiler"):
                            self.game.setup_profiler()
                        self.game.profiler.switch_show_hide()
                    elif event.key == pygame.K_1:
                        for character in self.player_objects.values():
                            character.cal_loss(0, (50, -200), {}, character.angle, (0, 0), False)
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

            if not self.music_left.get_busy():  # change if music finish playing
                picked_music = randint(0, len(self.music_list) - 1)
                music = pygame.mixer.Sound(self.music_list[picked_music])

                self.music_left.play(music, fade_ms=100)
                self.music_left.set_volume(self.play_music_volume, 0)
                self.music_right.play(music, fade_ms=100)
                self.music_right.set_volume(0, self.play_music_volume)

            if self.player_key_press[1]["Menu/Cancel"]:  # or self.player_key_press[2]["Menu/Cancel"]
                # open/close menu
                esc_press = True

            if self.player_unit_input_delay:  # delay for command input
                self.player_unit_input_delay -= self.dt
                if self.player_unit_input_delay < 0:
                    self.player_unit_input_delay = 0

            self.ui_updater.update()  # update ui before more specific update

            if esc_press:  # open/close menu
                if self.game_state == "battle":  # in battle
                    self.game_state = "menu"  # open menu
                    self.esc_text_popup.popup((self.screen_rect.centerx, self.screen_rect.height * 0.9),
                                              self.game.localisation.grab_text(
                                                  ("map", str(self.chapter), str(self.mission), str(self.stage),
                                                   "eventlog", self.battle_stage.current_frame, "Text")),
                                              width_text_wrapper=1000 * self.game.screen_scale[0])
                    self.add_ui_updater(self.battle_menu, self.cursor,
                                        self.battle_menu_button,
                                        self.esc_text_popup)  # add menu and its buttons to drawer
                    esc_press = False  # reset esc press, so it not stops esc menu when open
                    self.realtime_ui_updater.remove(self.player_1_battle_cursor)

            if self.game_state == "battle":  # game in battle state
                self.camera_process()

                pass_objective = True
                if self.lock_objective == "clear":
                    if len([enemy for enemy in self.all_team_enemy[1] if
                            self.base_stage_start <= enemy.base_pos[0] <= self.base_stage_end]):
                        pass_objective = False
                elif self.lock_objective == "survive":
                    self.survive_timer += self.dt
                    if self.survive_timer < 1:
                        pass_objective = False

                if pass_objective:  # can reach next scene, check for possible scene lock
                    if self.stage_scene_lock:  # update stage start and end from scene lock
                        if (type(self.next_lock) is int and self.battle_stage.current_frame == self.next_lock) or \
                                (type(self.next_lock) is tuple and self.battle_stage.current_frame in self.next_lock):
                            # player (camera) reach next lock
                            self.survive_timer = 0
                            if type(self.next_lock) is tuple:  # stage lock for multiple scene
                                self.base_stage_start = self.base_stage_end_list[self.next_lock[0]]
                                self.stage_start = self.stage_end_list[self.next_lock[0]] + (
                                        self.battle_camera_center[0] * 2)
                                self.base_stage_end = self.base_stage_end_list[self.next_lock[1]]
                                self.stage_end = self.stage_end_list[self.next_lock[1]]
                            else:  # stage lock for single scene
                                self.base_stage_start = (self.base_stage_end_list[self.battle_stage.current_frame - 1])
                                self.stage_start = self.stage_end_list[self.battle_stage.current_frame - 1] + (
                                        self.battle_camera_center[0] * 2)
                                self.base_stage_end = self.base_stage_end_list[self.battle_stage.current_frame]
                                self.stage_end = self.stage_end_list[self.battle_stage.current_frame]

                            self.lock_objective = self.stage_scene_lock[self.next_lock]
                            self.stage_scene_lock.pop(self.next_lock)

                            self.next_lock = False
                            if self.stage_scene_lock:
                                self.next_lock = tuple(self.stage_scene_lock.keys())[0]

                    elif self.next_lock is False:  # no more lock, make the stage_end the final stage position
                        self.next_lock = None  # assign None so no need to do below code in later update
                        self.survive_timer = 0
                        self.base_stage_end = self.base_stage_end_list[tuple(self.base_stage_end_list.keys())[-1]]
                        self.stage_end = self.stage_end_list[tuple(self.stage_end_list.keys())[-1]]

                if self.later_enemy[self.battle_stage.spawn_frame]:  # check for enemy arriving based on camera pos
                    self.spawn_delay_timer[self.battle_stage.spawn_frame] += self.dt
                    first_delay = tuple(self.later_enemy[self.battle_stage.spawn_frame].keys())[0]
                    if self.spawn_delay_timer[self.battle_stage.spawn_frame] >= first_delay:
                        # spawn based on delay timer
                        self.setup_battle_character((), self.later_enemy[self.battle_stage.spawn_frame][first_delay],
                                                    add_helper=False)
                        self.later_enemy[self.battle_stage.spawn_frame].pop(first_delay)

                for player_index, player_object in self.player_objects.items():
                    player_object.player_input(player_index, self.dt)

                if self.player_1_battle_cursor.pos_change:  # display cursor when have movement
                    self.show_cursor_timer = 0.1
                    self.player_1_battle_cursor.shown = True

                if self.show_cursor_timer:
                    self.show_cursor_timer += self.dt
                    if self.show_cursor_timer > 3:
                        self.show_cursor_timer = 0
                        self.player_1_battle_cursor.shown = False
                        self.player_1_battle_cursor.rect.topleft = (-100, -100)

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

                # Update game time
                self.dt = self.true_dt * self.game_speed  # apply dt with game_speed for calculation
                # if self.dt > 0.1:  # one frame update should not be longer than 0.01 second for calculation
                #     self.dt = 0.1  # make it so stutter and lag does not cause overtime issue

                self.ui_timer += self.dt  # ui update by real time instead of self time to reduce workload
                self.ui_dt = self.dt  # get ui timer before apply self

                if self.dt:  # Part that run when game not pause only
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
                    self.time_number.timer_update(self.dt)  # update battle time
                    self.battle_stage.update(self.shown_camera_pos[0])  # update stage first
                    self.character_updater.update(self.dt)
                    self.effect_updater.update(self.dt)
                    self.realtime_ui_updater.update()  # update UI
                    self.camera.update(self.shown_camera_pos, self.battle_camera, self.realtime_ui_updater)
                    self.frontground_stage.update(self.shown_camera_pos[0])  # update frontground stage last

                for key, value in self.sound_effect_queue.items():  # play each sound effect initiate in this loop
                    self.play_sound_effect(key, value)
                self.sound_effect_queue = {}

                if self.ui_timer >= 0.1:
                    for index, player in enumerate(self.player_objects.values()):
                        self.player_portraits[index].value_input(player)

                    self.ui_drawer.draw(self.screen)  # draw the UI
                    self.ui_timer -= 0.1

                if not self.all_team_enemy[1]:  # all enemies dead, end stage process
                    if not self.end_delay:
                        if self.decision_select not in self.realtime_ui_updater and self.stage_end_choice:
                            if "Victory" not in self.drama_text.queue:
                                self.drama_text.queue.append("Victory")
                            self.realtime_ui_updater.add(self.decision_select)
                        elif not self.stage_end_choice:
                            if "Victory" not in self.drama_text.queue:
                                self.drama_text.queue.append("Victory")

                        if self.decision_select.selected:
                            if self.decision_select.selected == "yes":
                                self.player_team_followers = self.stage_reward["yes"][self.chapter][self.mission][
                                    self.stage]
                            else:
                                pass
                                # self.player_equipment_store.append(self.stage_reward["no"][self.chapter][self.mission][self.stage])

                            for character in self.character_updater:
                                if character.is_boss:
                                    # start decision animation
                                    character.engage_combat()
                                    character.position = "Stand"  # enforce stand position
                                    if self.decision_select.selected == "yes":
                                        character.current_action = {"name": "Submit", "repeat": "True",
                                                                    "movable": "True"}
                                    else:
                                        character.current_action = {"name": "Execute", "movable": "True"}
                                    character.show_frame = 0
                                    character.frame_timer = 0
                                    character.pick_animation()
                                elif character == self.helper:  # helper
                                    pass

                            self.realtime_ui_updater.remove(self.decision_select)
                            self.decision_select.selected = None

                    if self.decision_select.selected or self.decision_select not in self.realtime_ui_updater:
                        #  player select decision or mission has no decision, count end delay

                        self.end_delay += self.dt

                        if self.end_delay >= 5:  # end battle
                            self.end_delay = 0
                            self.exit_battle()
                            if self.stage + 1 in self.game.preset_map_data[self.chapter][
                                self.mission]:  # has next stage
                                return True
                            else:
                                if self.mission + 1 in self.game.preset_map_data[self.chapter]:  # has next mission
                                    return True
                                else:
                                    return False

            elif self.game_state == "menu":  # Complete battle pause when open either esc menu or lorebook
                self.battle_stage.update(self.shown_camera_pos[0])  # update stage first
                # self.realtime_ui_updater.update()  # update UI
                self.camera.update(self.shown_camera_pos, self.battle_camera, self.realtime_ui_updater)
                self.frontground_stage.update(self.shown_camera_pos[0])  # update frontground stage last
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
                    if command == "end_battle":
                        return False

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

        self.remove_ui_updater(self.battle_menu, self.battle_menu_button, self.esc_slider_menu.values(),
                               self.esc_value_boxes.values(), self.esc_option_text.values(),
                               self.player_portraits, self.esc_text_popup)  # remove menu and ui

        self.music_left.stop()
        self.music_right.stop()

        # remove all reference from battle object
        self.players = {}
        self.player_objects = {}
        self.helper = None

        clean_group_object((self.all_chars, self.effect_updater, self.weather_matters))

        self.sound_effect_queue = {}

        self.battle_stage.clear_image()
        self.frontground_stage.clear_image()

        self.drama_timer = 0  # reset drama text popup
        self.realtime_ui_updater.remove(self.drama_text)
