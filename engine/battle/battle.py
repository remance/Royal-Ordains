import sys
import time
from copy import deepcopy
from os import path
from random import choice, randint

import pygame
from pygame import Vector2, display, sprite, Surface, SRCALPHA
from pygame.locals import *
from pygame.mixer import Sound, Channel

from engine.aibattle.battle_commander_ai import BattleCommanderAI
from engine.camera.camera import Camera
from engine.character.character import Character
from engine.drama.drama import TextDrama
from engine.effect.effect import DamageEffect, Effect
from engine.scene.scene import Scene
from engine.stageobject.stageobject import StageObject
from engine.uibattle.uibattle import (FPSCount, BattleHelper, BattleCursor, YesNo, CharacterSpeechBox,
                                      CharacterCommandIndicator, PlayerBattleInteract, CharacterInteractPrompt,
                                      Command, TacticalMap, StrategySelect, ScreenFade)
from engine.uimenu.uimenu import TextPopup

from engine.game.activate_input_popup import activate_input_popup
from engine.battle.activate_strategy import activate_strategy
from engine.battle.add_sound_effect_queue import add_sound_effect_queue
from engine.battle.check_event import check_event
from engine.battle.cal_shake_value import cal_shake_value
from engine.battle.call_in_air_group import call_in_air_group
from engine.battle.change_game_state import change_game_state
from engine.game.change_pause_update import change_pause_update
from engine.battle.check_reinforcement import check_reinforcement
from engine.battle.drama_process import drama_process
from engine.battle.end_cutscene_event import end_cutscene_event
from engine.battle.escmenu_process import escmenu_process, back_to_battle_state
from engine.battle.fix_camera import fix_camera
from engine.battle.make_esc_menu import make_esc_menu
from engine.battle.player_input_battle import player_input_battle
from engine.battle.player_input_cutscene import player_input_cutscene
from engine.battle.play_sound_effect import play_sound_effect
from engine.battle.setup_team_characters import setup_team_characters
from engine.battle.state_battle_process import state_battle_process
from engine.battle.state_menu_process import state_menu_process
from engine.battle.shake_camera import shake_camera
from engine.battle.event_process import event_process
from engine.lorebook.lorebook import lorebook_process

from engine.constants import *
from engine.utils.common import clean_group_object
from engine.utils.data_loading import load_image, load_images, filename_convert_readable as fcv
from engine.weather.weather import Weather

script_dir = path.split(path.abspath(__file__))[0] + "/"

decision_route = {"yes": "a", "no": "b"}
team_list = range(3)
inf = float("inf")


def set_start_load(self, what):  # For output asset loading time in terminal
    globals()["load_timer"] = time.time()
    self.game.loading_screen("Loading " + what)  # change loading screen to display progress
    return "Loading {0}... ".format(what)


def set_done_load():
    duration = time.time() - globals()["load_timer"]
    return " DONE ({0}s)\n".format(duration)


class Battle:
    activate_input_popup = activate_input_popup
    activate_strategy = activate_strategy
    add_sound_effect_queue = add_sound_effect_queue
    check_event = check_event
    cal_shake_value = cal_shake_value
    call_in_air_group = call_in_air_group
    change_game_state = change_game_state
    change_pause_update = change_pause_update
    check_reinforcement = check_reinforcement
    drama_process = drama_process
    end_cutscene_event = end_cutscene_event
    back_to_battle_state = back_to_battle_state
    escmenu_process = escmenu_process
    fix_camera = fix_camera
    make_esc_menu = make_esc_menu
    player_input_battle = player_input_battle
    player_input_cutscene = player_input_cutscene
    play_sound_effect = play_sound_effect
    setup_team_characters = setup_team_characters
    state_battle_process = state_battle_process
    state_process = state_battle_process
    state_menu_process = state_menu_process
    shake_camera = shake_camera
    event_process = event_process
    lorebook_process = lorebook_process

    battle = None
    battle_cursor = None
    camera = None
    ui_updater = None
    ui_drawer = None
    screen = None
    camera_size = None
    camera_max = None
    start_camera_mode = "Free"

    process_list = {"battle": state_battle_process, "menu": state_menu_process}

    def __init__(self, game):
        self.game = game
        Battle.battle = self
        # TODO LIST
        # add enemy command AI, skirmish behaviour ai for ranged char/leader/group, commander
        # think how to deal center battle map start retreat point
        # add custom battle setup menu
        # link character to outside battle stat somewhere for when add grand strategy and results
        # finish Rodhinbar
        # add back hold function, for spear pike and stuff
        # add back battle cutscene
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
        self.player_key_bind = self.game.player_key_bind_list
        self.player_key_bind_name = {value: key for key, value in self.player_key_bind.items()}
        self.player_key_press = {key: False for key in self.player_key_bind}
        self.player_key_hold = {key: False for key in self.player_key_bind}
        self.screen_rect = game.screen_rect
        self.screen_width = self.screen_rect.width
        self.screen_height = self.screen_rect.height
        self.corner_screen_width = game.corner_screen_width
        self.corner_screen_height = game.corner_screen_height

        Battle.camera_size = (self.screen_width, self.screen_height)
        Battle.camera_max = (self.screen_width - 1, self.screen_height - 1)
        self.camera_center_x = self.camera_size[0] / 2
        self.camera_center_y = self.camera_size[1] / 2

        self.main_dir = game.main_dir
        self.data_dir = game.data_dir
        self.screen_scale = game.screen_scale
        self.battle_camera_object_drawer = game.battle_camera_object_drawer
        self.battle_camera_ui_drawer = game.battle_camera_ui_drawer
        Battle.ui_updater = game.battle_ui_updater
        Battle.ui_drawer = game.battle_ui_drawer

        self.character_updater = game.character_updater
        self.all_characters = game.all_characters
        self.speech_boxes = game.speech_boxes
        self.player_general_indicators = game.player_general_indicators
        self.stage_objects = game.stage_objects
        self.effect_updater = game.effect_updater
        self.battle_outer_ui_updater = game.battle_outer_ui_updater

        self.cursor = game.cursor

        self.button_ui = game.button_ui

        # Music and sound player
        self.current_music = None
        self.music_left = Channel(0)
        self.music_left.set_volume(self.play_music_volume, 0)
        self.music_right = Channel(1)
        self.music_right.set_volume(0, self.play_music_volume)
        self.current_ambient = None
        self.ambient = Channel(2)
        self.ambient.set_volume(self.play_effect_volume)
        self.weather_ambient = Channel(3)
        self.weather_ambient.set_volume(self.play_effect_volume)

        self.battle_sound_channel = tuple([Channel(ch_num) for ch_num in range(1000)])

        # Text popup
        self.text_popup = TextPopup()
        self.scene_translation_text_popup = TextPopup()  # popup box for text that translate background script

        self.input_box = game.input_box
        self.input_ui = game.input_ui
        self.input_ok_button = game.input_ok_button
        self.input_cancel_button = game.input_cancel_button
        self.input_ui_popup = game.input_ui_popup
        self.confirm_ui_popup = game.confirm_ui_popup
        self.all_input_ui_popup = game.all_input_ui_popup

        self.weather_matters = game.weather_matters

        # self.lorebook = game.lorebook
        # self.lore_name_list = game.lore_name_list
        # self.filter_tag_list = game.filter_tag_list
        # self.lore_buttons = game.lore_buttons
        # self.subsection_name = game.subsection_name
        # self.tag_filter_name = game.tag_filter_name

        # self.lorebook_stuff = game.lorebook_stuff

        self.music_pool = game.music_pool
        self.sound_effect_pool = game.sound_effect_pool
        self.ambient_pool = game.ambient_pool
        self.weather_ambient_pool = game.weather_ambient_pool
        self.sound_effect_queue = {}
        self.stage_music_pool = {}  # pool for music already converted to pygame Sound

        self.weather_screen_adjust = self.screen_width / self.screen_height  # for weather sprite spawn position
        self.right_corner = self.screen_width - (5 * self.screen_scale[0])
        self.bottom_corner = self.screen_height - (5 * self.screen_scale[1])

        self.character_data = self.game.character_data
        self.strategy_list = self.character_data.strategy_list
        self.battle_map_data = self.game.battle_map_data
        self.weather_data = self.battle_map_data.weather_data
        self.weather_matter_images = self.battle_map_data.weather_matter_images
        self.weather_list = self.battle_map_data.weather_list
        Weather.weather_data = self.weather_data
        Weather.weather_matter_images = self.weather_matter_images
        self.animation_data = self.game.sprite_data
        self.character_animation_data = self.game.character_animation_data
        self.character_portraits = self.game.character_portraits
        self.effect_animation_pool = self.game.effect_animation_pool
        self.language = self.game.language
        self.localisation = self.game.localisation
        self.save_data = game.save_data
        self.main_story_profile = self.game.save_data.save_profile

        self.game_speed = 1
        self.all_team_general = {index: sprite.Group() for index in team_list}
        self.all_team_ally = {index: sprite.Group() for index in team_list}
        self.all_team_enemy_check = {index: sprite.Group() for index in team_list}  # for victory check

        self.all_team_ground_enemy_collision_grids = {index: {} for index in team_list}
        self.all_team_air_enemy_collision_grids = {index: {} for index in team_list}
        self.last_grid = None

        self.player_input = self.player_input_battle
        self.player_damage = 0
        self.player_kill = 0
        self.battle_scale = []
        self.play_time = 0
        self.battle_time = 0.0
        self.team_stat = {team: {"strategy_resource": 0, "start_pos": 0, "air_group": [], "strategy": {}, "unit": {}} for
                          team in team_list}
        self.player_control_generals = []  # for command ui
        self.team_commander = {team: None for team in team_list}
        self.player_selected_generals = []  # for player order input
        self.player_selected_strategy = None

        self.later_reinforcement = {"weather": {}, "time": {}, "team": {team: {"air": [], "ground": {}} for team in team_list}}
        BattleCommanderAI.battle = self
        self.battle_team1_commander = BattleCommanderAI(1)
        self.battle_team2_commander = BattleCommanderAI(2)

        self.game_state = "battle"
        self.esc_menu_mode = "menu"

        self.mission = None

        self.best_depth = display.mode_ok(self.screen_rect.size, self.game.window_style,
                                          32)  # Set the display mode
        Battle.screen = display.set_mode(self.screen_rect.size, self.game.window_style,
                                         self.best_depth)  # set up self screen

        # Create the game camera
        self.camera_mode = "Follow"  # mode of game camera, follow player character or free observation
        self.camera_pos = Vector2(500, 500)  # camera pos on scene
        self.camera_left = (self.camera_pos[0] - self.camera_center_x)

        self.base_camera_left = (self.camera_pos[0] - self.camera_center_x) / self.screen_scale[0]

        self.shown_camera_pos = self.camera_pos  # pos of camera shown to player, in case of screen shaking or other effects

        Battle.camera = Camera(self.screen, self.camera_size)
        self.camera_w_center = self.camera.camera_w_center
        self.camera_h_center = self.camera.camera_h_center
        self.camera_left_shift = self.shown_camera_pos[0] - self.camera_w_center

        # Assign battle variable to some classes
        Character.collision_grid_width = self.screen_width / Collision_Grid_Per_Scene  # collision grid width based on screen scale
        Character.sound_effect_pool = self.sound_effect_pool
        DamageEffect.collision_grid_width = self.screen_width / Collision_Grid_Per_Scene
        Effect.sound_effect_pool = self.sound_effect_pool

        # Create battle ui
        Battle.battle_cursor = BattleCursor(load_images(self.data_dir,
                                                        subfolder=("ui", "cursor_battle")))  # no need to scale cursor

        battle_ui_images = self.game.battle_ui_images
        CharacterSpeechBox.images = battle_ui_images

        self.command_ui = Command()
        self.player_battle_interact = PlayerBattleInteract()
        self.tactical_map_ui = TacticalMap(battle_ui_images["tactical_selected"],
                                           battle_ui_images["tactical_commander_selected"])
        self.strategy_select_ui = StrategySelect(self.command_ui.rect.bottomleft, self.animation_data.strategy_icons)

        self.battle_timer_ui = BattleHelper(self.game.weather_icon_images, battle_ui_images["time_select"],
                                            battle_ui_images["time_selector"])
        self.battle_outer_ui_updater.add(self.command_ui, self.tactical_map_ui, self.strategy_select_ui,
                                         self.battle_timer_ui, self.player_battle_interact)
        self.character_command_indicator = tuple([CharacterCommandIndicator(
            index, 600 + (100 * index), battle_ui_images["player_order_move"], battle_ui_images["player_order_attack"])
            for index in range(5)])

        self.screen_fade = ScreenFade()
        self.speech_prompt = CharacterInteractPrompt(battle_ui_images["button_weak"])
        #
        # self.player_wheel_ui = WheelUI(battle_ui_images, self.command_ui.rect.midbottom)

        self.decision_select = YesNo(battle_ui_images)

        self.current_weather = Weather(1, 0, 0)

        TextDrama.images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                       subfolder=("ui", "popup_ui", "drama_text"))
        self.drama_text = TextDrama(self)  # message at the top of screen that show up for important event

        self.fps_count = FPSCount(self)  # FPS number counter
        if self.game.show_fps:
            self.battle_outer_ui_updater.add(self.fps_count)

        # Battle ESC menu
        esc_menu_dict = self.make_esc_menu()

        self.battle_menu_button = esc_menu_dict["battle_menu_button"]
        self.esc_option_menu_button = esc_menu_dict["esc_option_menu_button"]
        self.esc_slider_menu = esc_menu_dict["esc_slider_menu"]
        self.esc_value_boxes = esc_menu_dict["esc_value_boxes"]
        self.esc_option_text = esc_menu_dict["volume_texts"]
        self.dialogue_box = esc_menu_dict["dialogue_box"]
        self.esc_dialogue_button = esc_menu_dict["esc_dialogue_button"]

        self.clock_time = 0
        self.true_dt = 0
        self.dt = 0  # Realtime used for time calculation
        self.screen_shake_value = 0  # count for how long to shake camera

        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0  # This is timer for combat related function, use self time (realtime * game_speed)
        self.reinforcement_check_timer = 0

        self.base_cursor_pos = [0, 0]  # mouse base pos on the map based on camera position
        self.cursor_pos = [0, 0]

        # Battle map object
        Scene.image = Surface.subsurface(self.camera.image, (0, 0, self.camera.image.get_width(),
                                                             self.camera.image.get_height()))
        Scene.battle = self
        self.scene = Scene()

        self.empty_scene_image = Surface((self.screen_width, self.screen_height), SRCALPHA)

        self.base_stage_start = 0
        self.stage_start = 0
        self.stage_end = 0
        self.base_stage_end = 0

        self.start_cutscene = []
        self.reach_scene_event_list = {}  # cutscene that play when camera reach scene
        self.player_interact_event_list = {}
        self.end_delay = 0  # delay until scene end and continue to next one
        self.spawn_delay_timer = {}
        self.blit_culling_check = set()
        self.cutscene_in_progress = False
        self.cutscene_finish_camera_delay = 0  # delay before camera can move again after cutscene
        self.ai_battle_speak_timer = 0  # timer for follower talk based on their action
        self.ai_process_list = []
        self.cutscene_playing = None
        self.current_scene = 1

    def prepare_new_stage(self, mission, team_stat, ai_retreat):
        for message in self.inner_prepare_new_stage(mission, team_stat, ai_retreat):
            self.game.error_log.write("Start Stage:" + "." + str(mission))
            print(message, end="")

    def inner_prepare_new_stage(self, mission, team_stat, ai_retreat):
        """Setup stuff when start new battle"""
        self.mission = mission

        # Stop all sound
        for sound_ch in self.battle_sound_channel:
            if sound_ch.get_busy():
                sound_ch.stop()
        self.current_music = None
        self.current_ambient = None

        print("Start loading", self.mission)
        self.game.loading_lore_text = self.localisation.grab_text(
            ("load", randint(0, len(self.localisation.text[self.language]["load"]) - 1), "Text"))

        yield set_start_load(self, "stage setup")

        stage_data = self.game.preset_map_data[mission]

        stage_object_data = stage_data["data"]
        stage_event_data = deepcopy(stage_data["event"])

        loaded_item = []
        self.cutscene_playing = None
        self.base_stage_end = 0
        self.base_stage_start = 0
        self.stage_start = self.camera_center_x
        self.stage_end = -self.camera_center_x
        self.decision_select.selected = None
        self.end_delay = 0
        self.start_cutscene = []
        self.reach_scene_event_list = {}
        self.player_interact_event_list = {}
        self.stage_music_pool = {}
        self.speech_prompt.clear()
        for character_command_indicator in self.character_command_indicator:
            character_command_indicator.setup()

        for value in stage_object_data.values():
            if "scene" in value["Type"]:  # assign scene data
                if value["Object"] not in loaded_item:  # load image
                    image = self.empty_scene_image
                    if path.exists(path.join(self.data_dir, "map", "stage", "scene",
                                             fcv(str(value["Object"]), revert=True) + ".png")):
                        image = load_image(self.data_dir, self.screen_scale,
                                           fcv(str(value["Object"]), revert=True) + ".png",
                                           ("map", "stage", "scene"))
                    self.scene.images[value["Object"]] = image
                    loaded_item.append(value["Object"])
                self.scene.data[value["POS"]] = value["Object"]
            elif value["Type"] == "object":
                StageObject(value["Object"], value["POS"])

        if stage_event_data:  # add scene if event has a scene change event
            for value in stage_data["event_data"]:
                if value["Type"] == "bgchange":
                    image = self.empty_scene_image

                    images = self.scene.images

                    if value["Object"] not in images:
                        if path.exists(
                                path.join(self.data_dir, "map", "scene", fcv(value["Object"], revert=True) + ".png")):
                            image = load_image(self.data_dir, self.screen_scale,
                                               fcv(value["Object"], revert=True) + ".png",
                                               ("map", "scene"))  # no scaling yet
                        images[value["Object"]] = image

        stage_bg_data = {}
        for key in self.scene.data:
            if key != "event":
                stage_bg_data[key] = None
        stage_len = len(stage_bg_data)
        self.base_stage_end = stage_len * Default_Screen_Width
        self.stage_end = self.camera_center_x + ((stage_len - 1) * self.screen_width)
        self.tactical_map_ui.setup()  # setup tactical map ui to scale with stage size

        self.team_stat = team_stat

        for team_stat in self.team_stat.values():
            team_stat["start_pos"] *= self.base_stage_end
            # add available strategies to team stat
            if team_stat["main_army"]:
                commander_stat = self.character_data.character_list[team_stat["main_army"].commander_id]
                if commander_stat["Strategy"]:
                    team_stat["strategy_cooldown"][len(team_stat["strategy"])] = 0
                    team_stat["strategy"].append(commander_stat["Strategy"])
            retinue_list = []
            if team_stat["main_army"]:
                retinue_list += team_stat["main_army"].retinue
            if team_stat["garrison_army"]:
                retinue_list += team_stat["garrison_army"].retinue
            for retinue in retinue_list:
                team_stat["strategy_cooldown"][len(team_stat["strategy"])] = 0
                team_stat["strategy"].append(self.character_data.retinue_list[retinue]["Strategy"])

        self.strategy_select_ui.setup()

        self.last_char_game_id = 0
        self.spawn_delay_timer = {}

        yield set_done_load()

        yield set_start_load(self, "animation setup")
        character_list = [character["ID"] for character in stage_data["character"]]
        for team in self.team_stat:
            for strategy in self.team_stat[team]["strategy"]:
                if self.strategy_list[strategy]["Summon"]:
                    character_list += self.strategy_list[strategy]["Summon"]

        for team_value in self.team_stat.values():
            to_check = ([team_value["main_army"], team_value["garrison_army"]] + team_value["reinforcement_army"])
            to_check = [item for item in to_check if item]
            for value in to_check:
                for air_group in value.air_group:
                    character_list.append(tuple(air_group.keys())[0])
                for general, follower in value.generals.items():
                    character_list.append(general.char_id)
                    for follower_data in follower:
                        for follower_id in follower_data:
                            character_list.append(follower_id)

        already_check_char = set()
        character_list = list(set([char_id if "+" not in char_id else char_id.split("+")[0] for char_id in
                                    character_list]))
        while character_list:
            char_id = character_list[0]
            character_list.remove(char_id)
            if char_id not in already_check_char:
                already_check_char.add(char_id)
                if self.character_data.character_list[char_id]["Summon List"]:
                    character_list += (self.character_data.character_list[char_id]["Summon List"])
                if self.character_data.character_list[char_id]["Sub Characters"]:
                    character_list += set(self.character_data.character_list[char_id]["Sub Characters"])
                character_list = list(set([char_id if "+" not in char_id else char_id.split("+")[0] for char_id in
                                           character_list]))

        character_list = already_check_char

        if stage_event_data:  # add character if event has character create event
            for value in stage_data["event_data"]:
                if value["Type"] == "create" and value["Object"] not in character_list:
                    character_list.add(value["Object"])

        self.animation_data.load_character_animation(character_list, battle_only=True)

        yield set_done_load()

        yield set_start_load(self, "common setup")
        self.camera_mode = self.start_camera_mode

        self.clean_character_group()
        self.all_team_ground_enemy_collision_grids = {index: {} for index in team_list}
        self.all_team_air_enemy_collision_grids = {index: {} for index in team_list}
        for key in self.all_team_ground_enemy_collision_grids:
            for grid in range(int(stage_len * Collision_Grid_Per_Scene)):
                # divide grid per scene
                self.all_team_ground_enemy_collision_grids[key][grid] = sprite.Group()
                self.all_team_air_enemy_collision_grids[key][grid] = sprite.Group()
        self.last_grid = int(stage_len * Collision_Grid_Per_Scene) - 1

        for item in stage_data["character"]:
            if item["Arrive Condition"]:
                for key, value in item["Arrive Condition"].items():
                    # use only first condition
                    if value not in self.later_reinforcement[key]:
                        self.later_reinforcement[key][value] = []
                    self.later_reinforcement[key][value].append(item)
                    break

        for team in self.team_stat:
            team_reinforcement = {}
            for army in self.team_stat[team]["reinforcement_army"]:
                team_reinforcement |= army.generals
            if team_reinforcement:
                self.later_reinforcement["team"][team]["ground"] = team_reinforcement
            air_reinforcement = [air_group for army in self.team_stat[team]["reinforcement_army"] for air_group in army.air_group]
            if air_reinforcement:
                self.later_reinforcement["team"][team]["air"] = air_reinforcement

        self.setup_team_characters(stage_data)
        self.battle_team2_commander.__init__(2, can_retreat=ai_retreat)

        if stage_event_data:
            self.stage_music_pool = {key: Sound(self.music_pool[key]) for key in stage_event_data["music"] if
                                     key.lower() not in ("none", "resume", "pause")}
            for trigger, value in stage_event_data.items():
                if "char" in trigger:  # trigger depend on character
                    for key, value2 in value.items():
                        for this_char in self.all_characters:
                            if this_char.game_id == key:
                                if "in_camera" in trigger:  # reach camera event
                                    this_char.reach_camera_event = value2
                                break
                elif "start" in trigger:
                    for key, value2 in value.items():
                        for key3, value3 in value2.items():
                            if value3[0]["Type"]:  # check only parent event type data
                                self.start_cutscene = value3
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
                                    if "wind" in value3[0]["Property"]:
                                        wind_direction = value3[0]["Property"]["wind"]
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
        self.fix_camera()
        self.scene.setup()
        yield set_done_load()

    def run_game(self):
        # Create Starting Values
        self.input_popup = None  # no popup asking for user text input state
        self.drama_text.queue = []  # reset drama text popup queue

        self.camera_mode = self.start_camera_mode

        self.camera_pos = Vector2(500, self.camera_center_y)
        self.fix_camera()

        self.shown_camera_pos = self.camera_pos

        self.screen_shake_value = 0
        self.cutscene_in_progress = 0
        self.cutscene_finish_camera_delay = 0
        self.ai_battle_speak_timer = 0
        self.ui_timer = 0
        self.drama_timer = 0
        self.reinforcement_check_timer = 0
        self.dt = 0
        self.battle_cursor.shown = True
        self.player_damage = 0
        self.player_kill = 0
        self.battle_scale = []
        self.play_time = 0

        self.base_cursor_pos = [0, 0]  # mouse pos on the map based on camera position
        self.cursor_pos = [0, 0]
        # mouse.set_pos(Vector2(self.camera_pos[0], self.screen_scale[1] / 2))  # set cursor to center of screen

        self.player_key_bind = self.game.player_key_bind_list
        self.player_key_bind_name = {value: key for key, value in self.player_key_bind.items()}
        self.player_key_press = {key: False for key in self.player_key_bind}
        self.player_key_hold = {key: False for key in self.player_key_bind}

        self.screen.fill((0, 0, 0))
        self.battle_outer_ui_updater.add(self.battle_cursor)
        self.remove_ui_updater(self.cursor)

        if self.start_cutscene:
            # play start cutscene
            self.cutscene_playing = deepcopy(self.start_cutscene)
            self.start_cutscene = []

        frame = 0
        while True:  # battle running
            frame += 1

            if frame % 30 == 0 and hasattr(self.game, "profiler"):  # Remove for stable release, along with dev key
                self.game.profiler.refresh()
                frame = 0

            key_state = pygame.key.get_pressed()
            self.esc_press = False
            self.shift_press = False
            self.ctrl_press = False
            self.alt_press = False
            self.cursor.scroll_down = False
            self.cursor.scroll_up = False

            self.player_key_press = {key: False for key in self.player_key_press}
            self.player_key_hold = {key: False for key in self.player_key_hold}

            self.clock_time = self.clock.get_time()
            self.true_dt = self.clock_time / 1000  # dt before game_speed
            self.play_time += self.true_dt

            for key in self.player_key_press:  # check for key holding
                if type(self.player_key_bind[key]) is int and key_state[self.player_key_bind[key]]:
                    self.player_key_hold[key] = True
                elif key_state[pygame.K_LSHIFT] or key_state[pygame.K_RSHIFT]:
                    self.shift_press = True
                elif key_state[pygame.K_LALT] or key_state[pygame.K_RALT]:
                    self.alt_press = True
                elif key_state[pygame.K_LCTRL] or key_state[pygame.K_RCTRL]:
                    self.ctrl_press = True
            self.base_cursor_pos = Vector2(
                ((self.battle_cursor.pos[0] / self.screen_scale[0]) + self.base_camera_left),
                (self.battle_cursor.pos[1] / self.screen_scale[1]))  # mouse pos on the map based on camera position
            self.cursor_pos = Vector2(self.battle_cursor.pos[0] + self.camera_left,
                                      self.battle_cursor.pos[1])
            for event in pygame.event.get():  # get event that happen
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 4:  # Mouse scroll down
                        self.cursor.scroll_up = True
                    elif event.button == 5:  # Mouse scroll up
                        self.cursor.scroll_down = True

                elif event.type == QUIT:  # quit game
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    event_key_press = event.key
                    if event_key_press in self.player_key_bind_name:  # check for key press
                        self.player_key_press[self.player_key_bind_name[event_key_press]] = True
                    if event_key_press == K_ESCAPE or self.player_key_press["Menu/Cancel"]:  # accept esc button always
                        self.esc_press = True

                    # FOR DEVELOPMENT comment out later
                    if event.key == K_F1:
                        self.drama_text.queue.append(("Hello and welcome to showcase video", "Dollhi"))
                    elif event.key == K_F2:
                        self.drama_text.queue.append(("Show case: Neutral Enemy", None))
                    elif event.key == K_F3:
                        self.drama_text.queue.append(
                            ("In some maps, neutral animals may appear based on specific condition", None))
                    elif event.key == K_F4:
                        self.drama_text.queue.append(
                            ("Each can have a different behaviour, some just move around doing nothing", None))
                        # for enemy in self.player_control_generals:
                        #     for follower in enemy.followers:
                        #         follower.health = 0
                        # self.drama_text.queue.append(
                        #     ("They will return when out of resource and require rest to be ready again", None))
                    elif event.key == K_F5:
                        # self.drama_text.queue.append(("Maybe need to add clear unit selector around here", None))
                        # self.drama_text.queue.append(("Each has different role for fighting air/ground units.", None))
                        # self.drama_text.queue.append(("All dead.", None))
                        self.drama_text.queue.append(
                            ("Some may be curious like bear cub that will follow any coming close, very dangerous", None))
                        # for enemy in self.player_control_generals:
                        #     if not enemy.is_commander:
                        #         enemy.health = 0
                        #         break
                    elif event.key == K_F6:
                        self.drama_text.queue.append(
                            ("Some will even attack, buff, debuff or even summon enemies", None))
                        self.call_in_air_group(2, [index for index, _ in enumerate(self.team_stat[2]["air_group"])],
                                               500)
                        # self.screen_shake_value = 11111
                        # for enemy in self.player_control_generals:
                        #     enemy.broken = True
                    elif event.key == K_F7:
                        self.activate_strategy(2, "Spell_huge_stone", 1000)
                        # self.screen_shake_value = 11111
                        # for enemy in self.player_control_generals:
                        #     enemy.broken = True
                    elif event.key == K_F11:  # clear profiler
                        if hasattr(self.game, "profiler"):
                            self.game.profiler.clear()
                    elif event.key == K_F12:  # show/hide profiler
                        if not hasattr(self.game, "profiler"):
                            self.game.setup_profiler()
                        self.game.profiler.switch_show_hide()

            self.ui_updater.update()  # update ui before more specific update

            return_state = self.state_process()  # run code based on current state
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

    def clean_character_group(self):
        for this_group in self.all_team_ally.values():
            this_group.empty()
        for this_group in self.all_team_general.values():
            this_group.empty()
        for this_group in self.all_team_enemy_check.values():
            this_group.empty()

        # setup grid for collide check
        for collision_grids in (self.all_team_ground_enemy_collision_grids, self.all_team_air_enemy_collision_grids):
            for team in collision_grids.values():
                for grid in team.values():
                    grid.empty()

    def exit_battle(self):
        # remove menu and ui
        self.remove_ui_updater(self.battle_menu_button.values(), self.esc_slider_menu.values(),
                               self.esc_value_boxes.values(), self.esc_option_text.values(),
                               self.scene_translation_text_popup)

        self.battle_outer_ui_updater.remove(self.decision_select)
        self.battle_cursor.change_image("normal")

        self.command_ui.reset()

        # stop all sounds
        for sound_ch in self.battle_sound_channel:
            if sound_ch.get_busy():
                sound_ch.stop()
        self.current_music = None
        self.current_ambient = None
        self.stage_music_pool = {}

        # remove all reference from battle object
        self.team_stat = {team: {"strategy_resource": 0, "start_pos": 0, "air_group": [], "strategy": {}, "unit": {}} for
                          team in team_list}
        self.later_reinforcement = {"weather": {}, "time": {},
                                    "team": {team: {"air": [], "ground": {}} for team in team_list}}
        self.ai_process_list = []
        self.team_commander = {team: None for team in team_list}
        self.player_control_generals = []
        self.player_selected_generals = []
        self.player_selected_strategy = None
        self.tactical_map_ui.character_rect = {}
        self.speech_prompt.clear()  # clear speech prompt from updater to avoid being deleted
        for character_command_indicator in self.character_command_indicator:
            character_command_indicator.setup()
        self.blit_culling_check.clear()
        self.battle_team1_commander.clear()
        self.battle_team2_commander.clear()

        self.clean_character_group()

        clean_group_object((self.all_characters, self.character_updater, self.effect_updater, self.weather_matters,
                            self.player_general_indicators))

        self.sound_effect_queue = {}

        self.drama_timer = 0  # reset drama text popup
        self.ai_battle_speak_timer = 0
        self.battle_outer_ui_updater.remove(self.drama_text)
        self.remove_ui_updater(self.drama_text)
