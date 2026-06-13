import sys
import time
from copy import deepcopy
from os.path import join, abspath, split, exists
from random import choice, randint
from types import MethodType

import pygame
from pygame import Vector2, display, sprite, Surface, SRCALPHA
from pygame.event import get as get_event, clear as clear_event
from pygame.locals import *
from pygame.mixer import Sound, Channel

from engine.aibattle.battle_commander_ai import BattleCommanderAI
from engine.battle.activate_retreat import activate_retreat
from engine.battle.activate_strategy import activate_strategy
from engine.battle.add_new_army_joining import add_new_army_joining
from engine.battle.add_sound_effect_queue import add_sound_effect_queue
from engine.battle.cal_shake_value import cal_shake_value
from engine.battle.call_in_air_group import call_in_air_group
from engine.battle.call_reinforcement import call_reinforcement
from engine.battle.change_game_state import change_game_state
from engine.battle.check_battle_character_to_load import check_battle_character_to_load
from engine.battle.check_event import check_event
from engine.battle.check_reinforcement import check_reinforcement
from engine.battle.create_air_group import create_air_group
from engine.battle.drama_process import drama_process
from engine.battle.end_cutscene_event import end_cutscene_event
from engine.battle.event_process import event_process
from engine.battle.fix_camera import fix_camera
from engine.battle.make_esc_menu import make_esc_menu
from engine.battle.new_army_arrive_process import new_army_arrive_process
from engine.battle.play_sound_effect import play_sound_effect
from engine.battle.player_input_battle import player_input_battle, battle_no_player_input_battle
from engine.battle.player_input_cutscene import player_input_cutscene
from engine.battle.setup_team_characters import setup_team_characters
from engine.battle.shake_camera import shake_camera
from engine.battle.state_battle_process import state_battle_process
from engine.battle.state_menu_process import state_menu_process, back_to_battle_state
from engine.battle.state_result_process import state_result_process
from engine.battleobject.battleobject import StageObject
from engine.camera.camera import Camera
from engine.character.character import Character
from engine.constants import *
from engine.effect.effect import DamageEffect, Effect
from engine.game.activate_input_popup import activate_input_popup
from engine.game.change_pause_update import change_pause_update
from engine.scene.scene import Scene
from engine.uibattle.drama import TextDrama
from engine.uibattle.uibattle import (FPSCount, BattleHelper, BattleScale, BattleCursor, CharacterSpeechBox,
                                      CharacterCommandIndicator, DamageNumber, EventNotification,
                                      PlayerBattleInteract, CharacterInteractPrompt,
                                      Command, TacticalMap, StrategyIcon, StrategySelect, ScreenFade, BattleResult)
from engine.uimenu.uimenu import TextPopup, BrownMenuButton
from engine.updater.updater import ReversedLayeredUpdates
from engine.utils.common import clean_group_object, cutscene_update
from engine.utils.data_loading import load_image, load_images
from engine.weather.weather import Weather, MatterSprite

script_dir = split(abspath(__file__))[0] + "/"

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
    activate_retreat = activate_retreat
    add_new_army_joining = add_new_army_joining
    add_sound_effect_queue = add_sound_effect_queue
    back_to_battle_state = back_to_battle_state
    cal_shake_value = cal_shake_value
    call_in_air_group = call_in_air_group
    call_reinforcement = call_reinforcement
    change_game_state = change_game_state
    change_pause_update = change_pause_update
    check_battle_character_to_load = check_battle_character_to_load
    check_event = check_event
    check_reinforcement = check_reinforcement
    create_air_group = create_air_group
    drama_process = drama_process
    end_cutscene_event = end_cutscene_event
    event_process = event_process
    fix_camera = fix_camera
    make_esc_menu = make_esc_menu
    player_input_cutscene = player_input_cutscene
    new_army_arrive_process = new_army_arrive_process
    play_sound_effect = play_sound_effect
    setup_team_characters = setup_team_characters
    state_battle_process = state_battle_process
    state_process = state_battle_process
    state_menu_process = state_menu_process
    state_result_process = state_result_process
    shake_camera = shake_camera

    battle = None
    battle_cursor = None

    process_list = {"battle": state_battle_process, "menu": state_menu_process, "result": state_result_process}

    def __init__(self, game):
        self.game = game
        Battle.battle = self
        # TODO LIST
        # add back battle cutscene
        # rework scene to use common paper background for same area (upto 14 pages?)
        # finish main menu
        # link grand to battle, auto battle, enter manual, leave manual, auto process,
        # Future idea
        # espionage, morale,

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

        self.camera_width = self.screen_width
        self.camera_height = self.screen_height
        self.camera_center_x = self.camera_width / 2
        self.camera_center_y = self.camera_height / 2

        self.main_dir = game.main_dir
        self.data_dir = game.data_dir
        self.screen_scale = game.screen_scale
        self.screen_scale_width = game.screen_scale_width
        self.screen_scale_height = game.screen_scale_height

        self.load_sprite_background_threads = self.game.load_sprite_background_threads

        # battle object group
        self.battle_camera_object_drawer = sprite.LayeredUpdates()
        self.battle_camera_ui_drawer = sprite.LayeredUpdates()  # this is drawer for ui in battle, does not move alonge with camera
        self.ui_menu_updater = ReversedLayeredUpdates()
        self.ui_menu_drawer = sprite.LayeredUpdates()

        self.battle_character_updater = ReversedLayeredUpdates()  # updater for character objects,
        # higher layer characters got update first for the purpose of blit culling check
        self.battle_character_updater.cutscene_update = MethodType(cutscene_update, self.battle_character_updater)
        # for battle UI stuff that need to be updated in real time like drama and weather objects, also used as drawer
        # all image pos should be based on the screen
        self.outer_ui_updater = sprite.LayeredUpdates()
        self.battle_effect_updater = sprite.Group()  # updater for effect objects (e.g. range attack sprite)
        self.battle_effect_updater.cutscene_update = MethodType(cutscene_update, self.battle_effect_updater)

        self.all_battle_characters = sprite.Group()  # group for all character objects for cleaning
        self.battle_stage_objects = sprite.Group()  # group for all scene objects for event delete check
        self.player_leader_indicators = sprite.Group()  # group for select check of all indicator of player leader

        self.weather_matters = sprite.Group()  # group for all sprite of weather effect group such as rain sprite

        self.button_uis = sprite.Group()  # ui button group in battle

        self.speech_boxes = sprite.Group()

        # Assign containers
        CharacterSpeechBox.containers = self.battle_effect_updater, self.battle_camera_ui_drawer, self.speech_boxes
        CharacterCommandIndicator.containers = self.battle_effect_updater
        DamageNumber.containers = self.battle_effect_updater, self.battle_camera_ui_drawer
        Effect.containers = self.battle_effect_updater
        StageObject.containers = self.battle_effect_updater, self.battle_stage_objects, self.battle_camera_object_drawer
        StrategyIcon.containers = self.battle_effect_updater, self.battle_camera_ui_drawer
        DamageEffect.containers = self.battle_effect_updater
        MatterSprite.containers = self.weather_matters, self.outer_ui_updater
        Character.containers = self.battle_character_updater, self.all_battle_characters

        self.cursor = game.cursor

        # Music and sound player
        self.current_music = None
        self.current_ambient = None
        self.music_channel = self.game.music_channel
        self.ambient_channel = self.game.ambient_channel
        self.weather_ambient_channel = self.game.weather_ambient_channel
        self.button_sound_channel = self.game.button_sound_channel
        self.SONG_END = pygame.USEREVENT + 1

        self.effect_sound_channels = tuple([Channel(ch_num) for ch_num in range(4, 1000)])

        # Text popup
        self.text_popup = TextPopup()
        self.scene_translation_text_popup = TextPopup()  # popup box for text that translate background script

        self.input_box = game.input_box
        self.input_ui = game.input_ui
        self.input_ok_button = game.input_ok_button
        self.input_cancel_button = game.input_cancel_button
        self.input_popup_uis = game.input_popup_uis
        self.confirm_popup_uis = game.confirm_popup_uis
        self.all_input_popup_uis = game.all_input_popup_uis

        self.music_pool = game.music_pool
        self.sound_effect_pool = game.sound_effect_pool
        self.ambient_pool = game.ambient_pool
        self.weather_ambient_pool = game.weather_ambient_pool
        self.sound_effect_queue = {}
        self.default_battle_music_pool = [Sound(self.music_pool[str(index)]) for index in range(1, 10)]
        self.stage_music_pool = {}  # pool for music already converted to pygame Sound

        self.weather_screen_adjust = self.screen_width / self.screen_height  # for weather sprite spawn position

        self.character_data = self.game.character_data
        self.character_list = self.character_data.character_list
        self.strategy_list = self.character_data.strategy_list
        self.can_cure_status_list = self.character_data.can_cure_status_list
        self.can_clarity_status_list = self.character_data.can_clarity_status_list
        self.sprite_data = self.game.sprite_data
        self.map_data = self.game.map_data
        self.weather_data = self.map_data.weather_data
        Weather.weather_data = self.weather_data
        Weather.weather_matter_images = self.sprite_data.weather_matter_images
        self.character_animation_data = self.game.character_animation_data
        self.character_portraits = self.game.character_portraits
        self.effect_animation_pool = self.game.effect_animation_pool
        self.language = self.game.language
        self.localisation = self.game.localisation
        self.grab_text = self.localisation.grab_text
        self.save_data = game.save_data
        self.main_story_profile = self.game.save_data.save_profile

        self.game_speed = 1
        self.all_team_ally = {index: sprite.Group() for index in team_list}
        self.all_team_enemy_check = {index: sprite.Group() for index in team_list}  # for victory check

        self.all_team_ground_enemy_collision_grids = {index: () for index in team_list}
        self.all_team_air_enemy_collision_grids = {index: () for index in team_list}
        self.last_grid = None

        self.player_team = None
        self.winner_team = None
        self.player_enemy_team = None
        self.player_input = None
        self.player_damage = 0
        self.player_kill = 0
        self.battle_scale = []
        self.battle_time = 0.0

        self.team_state = {team: {"faction": None, "culture": None, "strategy_resource": 0, "supply_resource": 0,
                                  "supply_reserve": 0, "total_supply": 0, "leadership": 0, "start_pos": 0,
                                  "leader_call_list": [], "troop_call_list": [],
                                  "air_group": [], "strategy": {}} for
                           team in team_list}
        self.team_commander = {team: None for team in team_list}
        self.team_deployed = {team: 0 for team in team_list}
        self.team_loss = {team: 0 for team in team_list}
        self.player_commander = None
        self.player_culture = None
        self.player_selected_strategy = None

        self.current_weather = Weather(1, 0, 0)

        self.later_reinforcement = {"weather": {}, "time": {},
                                    "team": {team: {"air": [], "ground": []} for team in team_list}}
        self.team1_call_leader_cooldown_reinforcement = {}
        self.team1_call_troop_cooldown_reinforcement = {}
        self.team2_call_leader_cooldown_reinforcement = {}
        self.team2_call_troop_cooldown_reinforcement = {}
        self.awaiting_armies = {}
        BattleCommanderAI.battle = self
        self.battle_ai_commander1 = BattleCommanderAI(1)
        self.battle_ai_commander2 = BattleCommanderAI(2)
        self.all_battle_ai_commanders = []

        self.game_state = "battle"
        self.esc_menu_mode = "menu"

        self.grand = None
        self.campaign = self.game.campaign
        self.stage = None

        self.screen = self.game.screen

        # Create the game camera
        self.camera_pos = Vector2(500, 500)  # camera pos on scene
        self.camera_left_bound = (self.camera_pos[0] - self.camera_center_x)

        self.base_camera_left_bound = (self.camera_pos[0] - self.camera_center_x) / self.screen_scale_width
        self.base_camera_pos = Vector2(self.camera_pos[0] / self.screen_scale_width,
                                       self.camera_pos[1] / self.screen_scale_height)
        self.shown_camera_center_pos = self.camera_pos  # pos of camera shown to player, in case of screen shaking or other effects

        self.camera = Camera(self.screen, (self.camera_width, self.camera_height))
        self.camera_w_center = self.camera.camera_w_center
        self.camera_h_center = self.camera.camera_h_center
        self.camera_x_shift = self.shown_camera_center_pos[0] - self.camera_w_center

        # Assign battle variable to some classes
        Character.collision_grid_width = self.screen_width / Collision_Grid_X_Per_Battle_Scene  # collision grid size based on screen scale
        Character.collision_grid_height = self.screen_height / Collision_Grid_Y_Per_Battle_Scene
        Character.sound_effect_pool = self.sound_effect_pool
        DamageEffect.collision_grid_width = self.screen_width / Collision_Grid_X_Per_Battle_Scene
        DamageEffect.collision_grid_height = self.screen_height / Collision_Grid_Y_Per_Battle_Scene
        Effect.sound_effect_pool = self.sound_effect_pool

        # Create battle ui
        Battle.battle_cursor = BattleCursor(load_images(self.data_dir,
                                                        subfolder=("ui", "cursor_battle")))  # no need to scale cursor
        EventNotification.event_icons = self.sprite_data.grand_ui_icons

        battle_ui_images = self.game.battle_ui_images
        self.battle_ui_images = battle_ui_images
        CharacterSpeechBox.images = battle_ui_images

        StrategyIcon.strategy_icons = self.sprite_data.strategy_icons
        self.command_ui = Command(battle_ui_images["call_count"], battle_ui_images["air_count"])
        self.player_interact = PlayerBattleInteract()
        self.tactical_map_ui = TacticalMap(battle_ui_images["tactic_alert"])

        self.battle_helper_ui = BattleHelper(self.game.weather_icon_images,
                                             battle_ui_images["helperui"],
                                             battle_ui_images["helperui_base"],
                                             self.game.helper_images,
                                             (battle_ui_images["time_pause"],
                                              battle_ui_images["time_slow"],
                                              battle_ui_images["time_normal"],
                                              battle_ui_images["time_fast"]),
                                             (battle_ui_images["time_select"],
                                              battle_ui_images["time_unselect"])
                                             )
        self.battle_scale_ui = BattleScale(self.tactical_map_ui.rect.bottomleft)
        self.strategy_select_ui = StrategySelect(self.battle_scale_ui.rect.midbottom,
                                                 self.sprite_data.strategy_icons)

        self.grand_event_notification = EventNotification(self.command_ui.rect.bottomleft)

        self.always_command_ui = (self.tactical_map_ui, self.battle_helper_ui, self.battle_scale_ui,
                                  self.grand_event_notification)
        self.only_player_command_ui = (self.command_ui, self.strategy_select_ui, self.player_interact)

        self.character_command_indicator = CharacterCommandIndicator(600, battle_ui_images["player_order_move"],
                                                                     battle_ui_images["player_order_attack"])

        self.screen_fade = ScreenFade()
        self.speech_prompt = CharacterInteractPrompt(battle_ui_images["button_weak"])
        self.battle_result_ui = BattleResult()
        self.out_of_battle_result_button = BrownMenuButton((.15, 0.1), (0, 0.8), key_name="button_end_battle",
                                                           parent=self.battle_result_ui)

        TextDrama.images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                       subfolder=("ui", "popup_ui", "drama_text"))
        self.drama_text = TextDrama(self)  # message at the top of screen that show up for important event

        self.fps_count = FPSCount(self)  # FPS number counter

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

        self.base_cursor_pos = [0, 0]  # mouse base pos on the map based on camera position
        self.cursor_pos = [0, 0]

        # Battle map object
        Scene.image = Surface.subsurface(self.camera.image, self.camera.image.get_rect())
        Scene.battle = self
        Scene.camera = self.camera
        self.scene = Scene()

        self.empty_scene_image = Surface((self.screen_width, self.screen_height), SRCALPHA)

        self.base_stage_start = 0
        self.stage_start = 0
        self.stage_end = 0
        self.base_stage_end = 0
        self.effect_base_stage_end = 0

        self.start_cutscene = []
        self.event_list = {}  # cutscene that play when camera reach scene
        self.player_interact_event_list = {}
        self.end_delay = 0  # delay until scene end and continue to next one
        self.spawn_delay_timer = {}
        self.blit_culling_check = set()
        self.cutscene_in_progress = False
        self.cutscene_finish_camera_delay = 0  # delay before camera can move again after cutscene
        self.ai_battle_speak_timer = 0  # timer for character talk based on their action
        self.ai_process_list = []
        self.cutscene_playing = None
        self.current_scene = 1

    def setup_battle_start(self, campaign, stage, full_team_state):
        self.map_data.read_map_data(campaign, stage)
        stage_len = len(
            [value for value in self.game.preset_map_data[stage]["data"].values() if "scene" in value["Type"]])
        base_stage_end = stage_len * Default_Screen_Width

        for team_state in full_team_state.values():
            team_state["leader_call_list"] = []
            team_state["troop_call_list"] = []
            team_state["supply_resource"] = 0
            team_state["supply_reserve"] = 0
            team_state["total_supply"] = 0
            team_state["leadership"] = 0
            team_state["start_pos"] *= base_stage_end
            team_state["active_retinue"] = []
            # add available strategies to team stat
            if team_state["main_army"] and team_state["main_army"].commander_id:  # army exist
                main_army = team_state["main_army"]
                team_state["supply_resource"] = main_army.supply * 0.1
                team_state["supply_reserve"] = main_army.supply * 0.9
                team_state["total_supply"] = main_army.supply
                team_state["leader_call_list"] = [
                    [item, self.character_list[item]["Capacity"], self.character_list[item]["Supply"]] for item in
                    main_army.leader_group]
                team_state["troop_call_list"] = [
                    [item, self.character_list[item]["Capacity"], self.character_list[item]["Supply"]] for item in
                    main_army.ground_group]
                commander_stat = self.character_list[main_army.commander_id]
                team_state["leadership"] += commander_stat["Leadership"]
                if commander_stat["Strategy"]:
                    team_state["strategy_cooldown"][len(team_state["strategy"])] = 0
                    team_state["strategy"].append(commander_stat["Strategy"])
                retinue_list = []

                retinue_list += main_army.retinue
                if len(retinue_list) < 3:  # check for retinue in reinforcement armies until can get full 3
                    for army in team_state["reinforcement_army"]:
                        if army.retinue:
                            retinue_list += army.retinue[:3 - len(retinue_list)]
                            if len(retinue_list) == 3:
                                break

                for retinue in retinue_list:
                    team_state["leadership"] += (self.character_list[retinue]["Leadership"] *
                                                 Retinue_Leadership_Add_Modifier)
                    team_state["strategy_cooldown"][len(team_state["strategy"])] = 0
                    team_state["strategy"].append(self.character_list[retinue]["Strategy"])

                team_state["active_retinue"] = retinue_list
            team_state["strategy_resource"] = team_state["leadership"]
            team_state["strategy_regen"] = team_state["leadership"] / 100

            for army in team_state["reinforcement_army"]:
                if army.commander_id:
                    team_state["supply_reserve"] += army.supply
                    team_state["total_supply"] += army.supply
                    team_state["leader_call_list"].append([army.commander_id, 1, self.character_list[army.commander_id][
                        "Supply"]])  # add reinforcement commander as leader
                    team_state["leader_call_list"] += [
                        [item, self.character_list[item]["Capacity"], self.character_list[item]["Supply"]] for item in
                        army.leader_group]
                    team_state["troop_call_list"] += [
                        [item, self.character_list[item]["Capacity"], self.character_list[item]["Supply"]] for item in
                        army.ground_group]

    def prepare_new_stage(self, attach_grand, campaign, stage, team_state, player_team,
                          custom_stage_data, ai_retreat):
        for message in self.inner_prepare_new_stage(attach_grand, campaign, stage, team_state, player_team,
                                                    custom_stage_data, ai_retreat):
            self.game.error_log.write("Start Stage:" + "." + str(stage))
            print(message, end="")

    def inner_prepare_new_stage(self, attach_grand, campaign, stage, team_state, player_team,
                                custom_stage_data=None, ai_retreat=False):
        """Setup stuff when start new battle"""
        self.team_state = team_state
        stage_len = len(
            [value for value in self.game.preset_map_data[stage]["data"].values() if "scene" in value["Type"]])
        self.base_stage_end = stage_len * Default_Screen_Width
        self.grand = attach_grand
        self.campaign = campaign
        self.stage = stage
        self.player_team = player_team
        self.winner_team = None
        self.player_enemy_team = None
        # add common battle ui
        if self.game.show_fps:
            self.outer_ui_updater.add(self.fps_count)
        else:
            self.outer_ui_updater.remove(self.fps_count)
        self.outer_ui_updater.add(self.always_command_ui)
        if self.player_team:
            self.player_enemy_team = (0, 2, 1)[self.player_team]
            self.player_culture = team_state[self.player_team]["culture"]
            self.player_input = MethodType(player_input_battle, self)
            self.outer_ui_updater.add(self.only_player_command_ui)
        else:  # no player in battle, use another method that does not allow some hotkey input
            self.player_input = MethodType(battle_no_player_input_battle, self)
            self.player_culture = Custom_Default_Culture
            self.outer_ui_updater.remove(self.only_player_command_ui)

        # Stop all sound
        self.music_channel.set_volume(0)
        self.music_channel.stop()
        self.ambient_channel.set_volume(0)
        self.ambient_channel.stop()
        self.weather_ambient_channel.set_volume(0)
        self.weather_ambient_channel.stop()

        for sound_ch in self.effect_sound_channels:
            if sound_ch.get_busy():
                sound_ch.set_volume(0)
                sound_ch.stop()
        self.current_music = None
        self.current_ambient = None

        print("Start loading", self.stage)
        self.game.loading_lore_text = self.grab_text(
            ("load", randint(0, len(self.localisation.text[self.language]["load"]) - 1), "Text"))

        yield set_start_load(self, "stage setup")

        stage_data = self.game.preset_map_data[stage]

        stage_object_data = stage_data["data"]
        stage_event_data = deepcopy(stage_data["event"])

        loaded_item = []
        self.cutscene_playing = None
        self.base_stage_end = 0
        self.effect_base_stage_end = 0
        self.base_stage_start = 0
        self.stage_start = self.camera_center_x
        self.stage_end = -self.camera_center_x
        self.end_delay = 0
        self.start_cutscene = []
        self.event_list = {}
        self.player_interact_event_list = {}
        self.stage_music_pool = {}
        self.speech_prompt.clear()
        self.character_command_indicator.setup()

        for value in stage_object_data.values():
            if "scene" in value["Type"]:  # assign scene data
                if value["Object"] not in loaded_item:  # load image
                    image = self.empty_scene_image
                    if exists(join(self.data_dir, "map", "scene", str(value["Object"] + ".png"))):
                        image = load_image(self.data_dir, self.screen_scale,
                                           str(value["Object"]) + ".png", ("map", "scene"))
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
                        if exists(join(self.data_dir, "map", "scene", value["Object"] + ".png")):
                            image = load_image(self.data_dir, self.screen_scale, value["Object"] + ".png",
                                               ("map", "scene"))  # no scaling yet
                        images[value["Object"]] = image

        stage_len = len(
            [value for value in self.game.preset_map_data[stage]["data"].values() if "scene" in value["Type"]])
        self.base_stage_end = stage_len * Default_Screen_Width
        self.effect_base_stage_end = self.base_stage_end + 20000
        self.stage_end = self.camera_center_x + ((stage_len - 1) * self.screen_width)

        self.last_char_game_id = 0
        self.spawn_delay_timer = {}

        yield set_done_load()

        yield set_start_load(self, "animation setup")
        battle_character_list = [character["ID"] for character in stage_data["character"]]
        for effect in self.character_data.effect_list.values():
            if "summon" in effect["Property"]:
                battle_character_list.append(effect["Property"]["summon"])  # add all summon for all effects

        for team_value in self.team_state.values():
            for strategy in team_value["strategy"]:
                if self.strategy_list[strategy]["Summon"]:
                    battle_character_list += list(self.strategy_list[strategy]["Summon"].keys())
            if "unit" in team_value and team_value["unit"]:
                for unit in team_value["unit"]:
                    if unit["ID"] not in battle_character_list:
                        battle_character_list.append(unit["ID"])

            to_check = ([team_value["main_army"]] + team_value["reinforcement_army"])
            to_check = [item for item in to_check if item]
            for value in to_check:
                battle_character_list.append(value.commander_id)
                for air_group in value.air_group:
                    battle_character_list.append(air_group)
                for character in value.ground_group:
                    battle_character_list.append(character)
                for character in value.leader_group:
                    battle_character_list.append(character)

        battle_character_list = self.check_battle_character_to_load(battle_character_list)

        if stage_event_data:  # add character if event has character create event
            for value in stage_data["event_data"]:
                if value["Type"] == "create" and value["Object"] not in battle_character_list:
                    battle_character_list.add(value["Object"])

        self.sprite_data.load_character_animation(battle_character_list)
        print(self.load_sprite_background_threads, self.game.load_sprite_background_threads, "what")
        for thread in tuple(self.load_sprite_background_threads):  # must finish any loading thread before start battle
            print(thread, self.effect_animation_pool, "hmm")
            thread.join()
            self.load_sprite_background_threads.remove(thread)
        yield set_done_load()

        yield set_start_load(self, "common setup")

        self.clean_character_group()
        # grids for collision are kept in y, x metrix
        # the last y grid is used strategy/range collision for ALL characters where height play no part, so + 1 grid y per
        self.all_team_ground_enemy_collision_grids = {index: [[sprite.Group() for _ in
                                                               range(
                                                                   int(stage_len * Collision_Grid_X_Per_Battle_Scene))]
                                                              for
                                                              _ in range(Collision_Grid_Y_Per_Battle_Scene + 1)] for
                                                      index in team_list}
        self.all_team_air_enemy_collision_grids = {index: [[sprite.Group() for _ in
                                                            range(int(stage_len * Collision_Grid_X_Per_Battle_Scene))]
                                                           for
                                                           _ in range(Collision_Grid_Y_Per_Battle_Scene + 1)] for index
                                                   in team_list}

        self.last_grid = int(stage_len * Collision_Grid_X_Per_Battle_Scene)

        for item in stage_data["character"]:
            if item["Arrive Condition"]:
                for key, value in item["Arrive Condition"].items():
                    # use only first condition
                    if value not in self.later_reinforcement[key]:
                        self.later_reinforcement[key][value] = []
                    self.later_reinforcement[key][value].append(item)
                    break

        for team in self.team_state:
            air_reinforcement = [air_group for army in self.team_state[team]["reinforcement_army"] for air_group in
                                 army.air_group]
            if air_reinforcement:
                self.later_reinforcement["team"][team]["air"] = air_reinforcement

        self.setup_team_characters(stage_data)
        self.all_battle_ai_commanders = []
        if (self.player_team == 1 or not self.player_team) and self.battle.team_commander[2]:
            # commander exist for team 2
            self.battle_ai_commander2.__init__(2, can_retreat=ai_retreat)
            self.all_battle_ai_commanders.append(self.battle_ai_commander2)
        if (self.player_team == 2 or not self.player_team) and self.battle.team_commander[1]:
            # commander exist for team 1
            self.battle_ai_commander1.__init__(1, can_retreat=ai_retreat)
            self.all_battle_ai_commanders.append(self.battle_ai_commander1)
        self.all_battle_ai_commanders = tuple(self.all_battle_ai_commanders)

        if stage_event_data:
            self.stage_music_pool = {key: Sound(self.music_pool[key]) for key in stage_event_data["music"] if
                                     key.lower() not in ("none", "resume", "pause")}
            for trigger, value in stage_event_data.items():
                if "char" in trigger:  # trigger depend on character
                    for key, value2 in value.items():
                        for this_char in self.all_battle_characters:
                            if this_char.game_id == key:
                                if "in_camera" in trigger:  # reach camera event
                                    this_char.reach_camera_event = value2
                                break
                elif "start" in trigger:
                    for key, value2 in value.items():
                        for key3, value3 in value2.items():
                            if value3[0]["Type"]:  # check only parent event type data
                                self.start_cutscene = value3
                elif "time" in trigger:  # trigger depend on time
                    for key, value2 in value.items():
                        for key3, value3 in value2.items():
                            if key not in self.event_list:
                                self.event_list[key] = {}
                            if value3[0]["Type"] == "cutscene":  # check only parent event type data
                                if "cutscene" not in self.event_list[key]:
                                    self.event_list[key]["cutscene"] = []
                                self.event_list[key]["cutscene"].append(value3)
                            elif value3[0]["Type"] == "weather":
                                weather_strength = 0
                                wind_direction = randint(0, 359)
                                if "strength" in value3[0]["Property"]:
                                    weather_strength = value3[0]["Property"]["strength"]
                                if "wind" in value3[0]["Property"]:
                                    wind_direction = value3[0]["Property"]["wind"]
                                self.event_list[key]["weather"] = (
                                    value3[0]["Object"], wind_direction, weather_strength)
                            elif value3[0]["Type"] == "music":
                                if value3[0]["Object"] != "stop":
                                    self.event_list[key]["music"] = str(value3[0]["Object"])
                                else:
                                    self.event_list[key]["music"] = None
                            elif value3[0]["Type"] == "sound":
                                if "sound" not in self.event_list[key]:
                                    self.event_list[key]["sound"] = []
                                # sound effect must have sound distance and shake value in property
                                self.event_list[key]["sound"].append(
                                    (choice(self.sound_effect_pool[str(value3[0]["Object"])]),
                                     value3[0]["Property"]["sound distance"],
                                     value3[0]["Property"]["shake value"]))

        if custom_stage_data:
            if "weather" in custom_stage_data:  # add custom battle weather
                if 0 not in self.event_list:
                    self.event_list[0] = {}
                self.event_list[0]["weather"] = (custom_stage_data["weather"][0], randint(145, 215),
                                                 custom_stage_data["weather"][1])

        if self.player_team:
            self.camera_pos = Vector2(self.team_state[self.player_team]["start_pos"] * self.screen_scale_width,
                                      self.camera_center_y)
        else:  # no player, camera at center
            self.camera_pos = Vector2((self.base_stage_end / 2) * self.screen_scale_width,
                                      self.camera_center_y)

        # start with default music, will play other music based on event later
        self.music_channel.set_volume(self.play_music_volume)
        self.music_channel.play(choice(self.default_battle_music_pool), fade_ms=100)

        self.fix_camera()

        self.shown_camera_center_pos = self.camera_pos
        self.scene.setup()
        self.tactical_map_ui.setup()  # setup tactical map ui to scale with stage size
        self.command_ui.setup()
        self.strategy_select_ui.setup()
        self.battle_helper_ui.setup()

        # Create Starting Values
        self.input_popup = None  # no popup asking for user text input state
        self.drama_text.queue = []  # reset drama text popup queue

        self.screen_shake_value = 0
        self.cutscene_in_progress = 0
        self.cutscene_finish_camera_delay = 0
        self.ai_battle_speak_timer = 0
        self.ui_timer = 0
        self.drama_timer = 0
        self.dt = 0
        self.battle_cursor.shown = True
        self.player_damage = 0
        self.player_kill = 0
        self.battle_scale = []

        self.base_cursor_pos = [0, 0]  # mouse pos on the map based on camera position
        self.cursor_pos = [0, 0]
        # mouse.set_pos(Vector2(self.camera_pos[0], self.screen_scale_height / 2))  # set cursor to center of screen

        self.player_key_bind = self.game.player_key_bind_list
        self.player_key_bind_name = {value: key for key, value in self.player_key_bind.items()}
        self.player_key_press = {key: False for key in self.player_key_bind}
        self.player_key_hold = {key: False for key in self.player_key_bind}

        self.screen.fill((0, 0, 0))
        self.outer_ui_updater.add(self.battle_cursor)
        self.remove_from_ui_menu_updater(self.cursor)

        if self.start_cutscene:
            # play start cutscene
            self.cutscene_playing = deepcopy(self.start_cutscene)
            self.start_cutscene = []
        yield set_done_load()

    def run_battle(self):
        frame = 0
        clear_event()
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
                ((self.battle_cursor.pos[0] / self.screen_scale_width) + self.base_camera_left_bound),
                (self.battle_cursor.pos[1] / self.screen_scale_height))  # mouse pos on the map based on camera position
            self.cursor_pos = Vector2(self.battle_cursor.pos[0] + self.camera_left_bound,
                                      self.battle_cursor.pos[1])
            for event in get_event():  # get event that happen
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 4:  # Mouse scroll down
                        self.cursor.scroll_up = True
                    elif event.button == 5:  # Mouse scroll up
                        self.cursor.scroll_down = True
                elif event.type == self.SONG_END:  # whatever music end, pick random from default battle music
                    self.music_channel.set_volume(self.play_music_volume)
                    self.music_channel.play(choice(self.default_battle_music_pool), fade_ms=100)

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
                    if event.key == K_KP_1:
                        self.drama_text.queue.append((False, "Hello and welcome to showcase video", "Dollhi"))
                        # self.screen_shake_value += 1000
                        # test_army = Army("test", "castle",
                        #                  "castle",
                        #                  "leader_champion",
                        #                  ["leader_vraesier", "castle_human_leader_jester"],
                        #                  ["castle_human_militia_spear", "castle_human_militia_bow"],
                        #                  ["castle_cat_air_rocket_bomb"],
                        #                  ["castle_human_leader_lord", "castle_human_leader_jester"],
                        #                  supply=1000, max_supply=1000)
                        # self.new_army_arrive_process(test_army, 1)
                    elif event.key == K_KP_2:
                        self.drama_text.queue.append((True, "Show case: Reworked battle system.", None))
                        for enemy in self.all_battle_characters:
                            enemy.health = 0
                    elif event.key == K_KP_3:
                        self.drama_text.queue.append((
                            False, "In some maps, neutral animals may appear based on specific condition", None))
                        self.team_commander[1].health = 0
                    elif event.key == K_KP_4:
                        self.drama_text.queue.append((
                            False, "Each can have a different behaviour, some just move around doing nothing", None))
                        for enemy in self.all_battle_characters:
                            if enemy.alive:
                                enemy.health -= 100
                        self.drama_text.queue.append((
                            False, "They will return when out of resource and require rest to be ready again", None))
                    elif event.key == K_KP_5:
                        self.grand_event_notification.add_event(("bad", "test"))
                    elif event.key == K_KP_6:
                        self.grand_event_notification.add_event(("good", "test"))
                    elif event.key == K_KP_7:
                        self.activate_strategy(2, "Spell_huge_stone", 1000)
                    elif event.key == K_KP_8:  # clear profiler
                        if hasattr(self.game, "profiler"):
                            self.game.profiler.clear()
                    elif event.key == K_KP_9:  # show/hide profiler
                        if not hasattr(self.game, "profiler"):
                            self.game.setup_profiler()
                        self.game.profiler.switch_show_hide()

            return_state = self.state_process()  # run code based on current state
            if return_state is not None:
                return return_state

            display.update()  # update game display, draw everything
            self.clock.tick(1000)  # clock update even if self pause

    def add_to_ui_menu_updater(self, *args):
        self.ui_menu_updater.add(*args)
        self.ui_menu_drawer.add(*args)

    def remove_from_ui_menu_updater(self, *args):
        self.ui_menu_updater.remove(*args)
        self.ui_menu_drawer.remove(*args)

    def clean_character_group(self):
        for character in self.all_battle_characters:
            character.erase()

        for this_group in self.all_team_ally.values():
            this_group.empty()
        for this_group in self.all_team_enemy_check.values():
            this_group.empty()

        # setup grid for collide check
        for team in self.all_team_ground_enemy_collision_grids.values():
            for grid_y in team:
                for grid_x in grid_y:
                    grid_x.empty()

        for team in self.all_team_air_enemy_collision_grids.values():
            for grid_y in team:
                for grid_x in grid_y:
                    grid_x.empty()

    def exit_battle(self):
        # remove menu and ui
        self.remove_from_ui_menu_updater(self.battle_menu_button.values(), self.esc_slider_menu.values(),
                                         self.esc_value_boxes.values(), self.esc_option_text.values(),
                                         self.scene_translation_text_popup)

        self.battle_cursor.change_image("normal")

        self.command_ui.reset()
        self.grand_event_notification.reset()

        # stop all sounds
        self.music_channel.set_volume(0)
        self.music_channel.stop()
        self.ambient_channel.set_volume(0)
        self.ambient_channel.stop()
        self.weather_ambient_channel.set_volume(0)
        self.weather_ambient_channel.stop()

        for sound_ch in self.effect_sound_channels:
            if sound_ch.get_busy():
                sound_ch.stop()
        self.current_music = None
        self.current_ambient = None
        self.stage_music_pool = {}

        # remove all reference from battle object
        self.scene.images = {}
        self.scene.data = {}
        self.team_state = {team: {"faction": None, "culture": None, "strategy_resource": 0,
                                  "supply_resource": 0, "supply_reserve": 0, "total_supply": 0, "leadership": 0,
                                  "start_pos": 0, "leader_call_list": [], "troop_call_list": [],
                                  "air_group": [], "strategy": {}} for
                           team in team_list}
        self.team1_call_leader_cooldown_reinforcement = {}
        self.team1_call_troop_cooldown_reinforcement = {}
        self.team2_call_leader_cooldown_reinforcement = {}
        self.team2_call_troop_cooldown_reinforcement = {}
        self.all_battle_ai_commanders = []

        self.later_reinforcement = {"weather": {}, "time": {},
                                    "team": {team: {"air": [], "ground": []} for team in team_list}}
        self.ai_process_list = []
        self.team_commander = {team: None for team in team_list}
        self.player_commander = None
        self.player_culture = None
        self.player_selected_strategy = None
        self.tactical_map_ui.character_rect = {}
        self.speech_prompt.clear()  # clear speech prompt from updater to avoid being deleted
        self.character_command_indicator.setup()
        self.blit_culling_check.clear()
        self.battle_ai_commander1.clear()
        self.battle_ai_commander2.clear()

        self.clean_character_group()

        clean_group_object((self.all_battle_characters, self.battle_character_updater, self.battle_effect_updater,
                            self.weather_matters,
                            self.player_leader_indicators))

        self.sound_effect_queue = {}

        self.drama_timer = 0  # reset drama text popup
        self.ai_battle_speak_timer = 0
        self.outer_ui_updater.remove(self.drama_text)
