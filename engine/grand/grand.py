import configparser
import sys
from os.path import join
from types import MethodType

import pygame
from pygame import Vector2, display, sprite
from pygame.locals import *
from pygame.mixer import Channel

from engine.army.army import Army
from engine.battle.add_sound_effect_queue import add_sound_effect_queue
from engine.battle.battle import set_start_load, set_done_load
from engine.battle.change_game_state import change_game_state
from engine.battle.drama_process import drama_process
from engine.battle.play_sound_effect import play_sound_effect
from engine.battle.shake_camera import shake_camera
from engine.camera.camera import Camera
from engine.game.change_pause_update import change_pause_update
from engine.grand.activate_input_popup import activate_input_popup
from engine.grand.add_diplomacy_history_event import add_diplomacy_history_event
from engine.grand.auto_battle_process import auto_battle_process
from engine.grand.cal_faction_culture import cal_faction_culture
from engine.grand.cal_faction_income_recruit import cal_faction_income_recruit
from engine.grand.cal_region_income_recruit import cal_region_income_recruit
from engine.grand.cancel_building_construction_or_repair import cancel_building_construction_or_repair
from engine.grand.cancel_building_raze_or_pillage import cancel_building_raze_or_pillage
from engine.grand.change_phase import change_phase
from engine.grand.change_turn import change_turn
from engine.grand.check_region_building_available_upgrade import check_region_building_available_upgrade
from engine.grand.create_campaign_route_pathfinding import create_campaign_route_pathfinding
from engine.grand.create_new_army import create_new_army
from engine.grand.dismiss_faction_character import dismiss_faction_character
from engine.grand.draw_route import draw_route
from engine.grand.fix_camera import fix_camera
from engine.grand.give_faction_gift import give_faction_gift
from engine.grand.grand_process import grand_process
from engine.grand.make_esc_menu import make_esc_menu
from engine.grand.offer_faction_ally import offer_faction_ally
from engine.grand.player_input import player_input_grand, battle_no_player_input_grand
from engine.grand.sort_dot_army_occupation import sort_dot_army_occupation
from engine.grand.sort_player_army_list import sort_player_army_list
from engine.grand.start_battle_engagement import start_battle_engagement
from engine.grand.start_building_construction_or_repair import start_building_construction_or_repair
from engine.grand.start_building_raze_or_pillage import start_building_raze_or_pillage
from engine.grand.state_grand_process import state_grand_process
from engine.grand.state_menu_process import state_menu_process, back_to_grand_state
from engine.grandarmyactor.grandarmyactor import GrandArmyActor
from engine.grandobject.grandobject import GrandObject, SettlementObject
from engine.grandregion.grandregion import GrandRegion
from engine.uigrand.uigrand import (DotInfoBanner, DotInfoBannerArmy, DotInfoBannerSettlement, DotNameBannerSettlement)
from engine.uimenu.uimenu import TextPopup, GrandMiniMap, CustomPresetTitle
from engine.uiouterbattle.uiouterbattle import FPSCount
from engine.uioutergrand.cosmos import CosmosUI, MiniCosmosUI
from engine.uioutergrand.uioutergrand import (PlayerGrandInteract, PlayerTopBar,
                                              PlayerArmyList, PlayerArmyListSortOption, MapSettingOption,
                                              TimeSettingOption, EventDetailPopup, PlayerFactionCultureList,
                                              MenuBar, EventNotification, GrandTextDrama)
from engine.uioutergrand.uioutergrandcollapsible import (ArmyManagement, PresetArmyReserveSetup,
                                                         CourtManagement, CultureManagement,
                                                         DiplomacyManagement, PresetArmyGrandCharacterSelector,
                                                         RegionManagement, BuildingManagement, PresetArmyReserveList,
                                                         RegionManagementToggleButton, ArmyDeployToggleButton)
from engine.updater.updater import ReversedLayeredUpdates
from engine.utils.common import clean_group_object


class Grand:
    grand = None
    cursor = None

    activate_input_popup = activate_input_popup
    add_diplomacy_history_event = add_diplomacy_history_event
    add_sound_effect_queue = add_sound_effect_queue
    auto_battle_process = auto_battle_process
    back_to_grand_state = back_to_grand_state
    cal_faction_culture = cal_faction_culture
    cal_faction_income_recruit = cal_faction_income_recruit
    cal_region_income_recruit = cal_region_income_recruit
    change_game_state = change_game_state
    change_pause_update = change_pause_update
    cancel_building_construction_or_repair = cancel_building_construction_or_repair
    cancel_building_raze_or_pillage = cancel_building_raze_or_pillage
    change_phase = change_phase
    change_turn = change_turn
    check_region_building_available_upgrade = check_region_building_available_upgrade
    create_campaign_route_pathfinding = create_campaign_route_pathfinding
    create_new_army = create_new_army
    dismiss_faction_character = dismiss_faction_character
    drama_process = drama_process
    draw_route = draw_route
    fix_camera = fix_camera
    give_faction_gift = give_faction_gift
    grand_process = grand_process
    make_esc_menu = make_esc_menu
    offer_faction_ally = offer_faction_ally
    play_sound_effect = play_sound_effect
    shake_camera = shake_camera
    sort_dot_army_occupation = sort_dot_army_occupation
    sort_player_army_list = sort_player_army_list
    start_battle_engagement = start_battle_engagement
    start_building_construction_or_repair = start_building_construction_or_repair
    start_building_raze_or_pillage = start_building_raze_or_pillage
    state_process = state_grand_process
    state_grand_process = state_grand_process
    state_menu_process = state_menu_process

    process_list = {"grand": state_grand_process, "menu": state_menu_process}

    def __init__(self, game):
        self.game = game
        self.battle = self.game.battle
        Grand.grand = self
        Grand.cursor = game.cursor

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

        # grand campaign object group
        self.grand_camera_region_drawer = sprite.LayeredUpdates()
        self.grand_camera_ui_updater = sprite.LayeredUpdates()  # for ui on grand map, all image pos should be based on the screen
        self.grand_camera_ui_drawer = sprite.LayeredUpdates()
        self.ui_menu_drawer = sprite.LayeredUpdates()

        self.outer_ui_updater = ReversedLayeredUpdates()  # updater for ui on screen, update from top to bottom ui layer
        self.outer_ui_drawer = sprite.LayeredUpdates()  # drawer for ui on screen, does not move along with camera

        self.ui_menu_updater = ReversedLayeredUpdates()

        self.grand_object_updater = ReversedLayeredUpdates()  # updater for actor objects
        self.grand_camera_object_drawer = sprite.LayeredUpdates()
        self.grand_effect_updater = sprite.Group()  # updater for effect objects
        self.grand_settlement_objects = sprite.Group()

        GrandArmyActor.containers = self.grand_object_updater, self.grand_camera_object_drawer
        DotInfoBanner.containers = self.grand_camera_ui_updater, self.grand_camera_ui_drawer

        GrandObject.containers = self.grand_object_updater, self.grand_camera_object_drawer
        SettlementObject.containers = self.grand_camera_object_drawer, self.grand_settlement_objects
        GrandRegion.containers = self.grand_object_updater, self.grand_camera_region_drawer

        # Music and sound player
        self.current_music = None
        self.current_ambient = None
        self.music_channel = self.game.music_channel
        self.ambient_channel = self.game.ambient_channel
        self.weather_ambient_channel = self.game.weather_ambient_channel
        self.button_sound_channel = self.game.button_sound_channel

        self.effect_sound_channels = tuple([Channel(ch_num) for ch_num in range(4, 1000)])

        self.text_popup = TextPopup(font_size=56)

        self.input_box = game.input_box
        self.input_ui = game.input_ui
        self.input_ok_button = game.input_ok_button
        self.input_cancel_button = game.input_cancel_button
        self.input_close_button = game.input_close_button
        self.input_popup_uis = game.input_popup_uis
        self.confirm_popup_uis = game.confirm_popup_uis
        self.all_input_popup_uis = game.all_input_popup_uis

        self.music_pool = game.music_pool
        self.sound_effect_pool = game.sound_effect_pool
        self.ambient_pool = game.ambient_pool
        self.weather_ambient_pool = game.weather_ambient_pool
        self.sound_effect_queue = {}
        self.default_grand_music_pool = [value for key, value in self.music_pool.items() if not key.isdigit() and key != "menu"]
        self.weather_screen_adjust = self.screen_width / self.screen_height  # for weather sprite spawn position

        self.stat_data = self.game.stat_data
        self.character_list = self.game.character_list
        self.map_data = self.game.map_data
        self.weather_data = self.map_data.weather_data
        self.faction_list = self.map_data.faction_list
        self.building_list = self.stat_data.building_list
        self.building_upgrade_list = self.stat_data.building_upgrade_list
        self.culture_list = self.stat_data.culture_list
        self.cosmic_event_list = self.stat_data.cosmic_event_list

        self.sprite_data = self.game.sprite_data
        self.building_portraits = self.sprite_data.building_portraits
        self.culture_coas = self.sprite_data.culture_coas
        self.character_animation_data = self.sprite_data.character_animation_data
        self.character_portraits = self.sprite_data.character_portraits
        self.effect_animation_pool = self.sprite_data.effect_animation_pool
        self.language = self.game.language
        self.localisation = self.game.localisation
        self.grab_text = self.localisation.grab_text
        self.save_data = game.save_data

        self.game_speed = 0
        self.phase_timer = 0
        self.show_route = True

        self.screen = self.game.screen

        # Create map object
        self.base_world_map = None
        self.map_x_end = 0
        self.map_y_end = 0
        self.shown_world_map_width = 1
        self.shown_world_map_height = 1
        self.map_shown_to_base_scale_width = 1
        self.map_shown_to_base_scale_height = 1
        self.army_move_line_width = int(24 * self.screen_scale_width)
        self.army_move_inner_line_width = int(12 * self.screen_scale_width)


        # Create the game camera
        self.camera_topleft_pos = Vector2(500, 500)  # camera topleft pos on scene
        self.base_camera_center_pos = Vector2(
            (self.camera_topleft_pos[0] / self.map_shown_to_base_scale_width) + self.camera_center_x,
            (self.camera_topleft_pos[1] / self.map_shown_to_base_scale_height) + self.camera_center_y)
        self.shown_camera_topleft_pos = self.camera_topleft_pos.copy()

        self.camera = Camera(self.screen, (self.camera_width, self.camera_height))
        self.camera_w_center = self.camera.camera_w_center
        self.camera_h_center = self.camera.camera_h_center

        # Assign grand variables to class
        Army.grand = self
        GrandArmyActor.grand = self
        GrandObject.grand = self
        GrandRegion.grand = self

        # initiate default variables
        self.clock_time = 0
        self.true_dt = 0
        self.dt = 0  # Realtime used for time calculation
        self.screen_shake_value = 0  # count for how long to shake camera

        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0

        self.base_cursor_pos = [0, 0]  # mouse base pos on the map based on camera position
        self.cursor_pos = [0, 0]

        self.game_state = "grand"
        self.esc_menu_mode = "menu"

        self.player_selected_army = []
        self.campaign = None
        self.player_faction = None
        self.player_input = None
        self.current_campaign_state = {"cosmic_event": ()}
        self.settlement_dots = {}
        self.dots_army_occupation = {}

        self.region_by_colour_index = {}
        self.region_by_pos_index = {}
        self.region_list = {}
        self.route_list = {}
        self.settlement_object_list = {}
        self.wonder_object_list = {}

        # Create grand ui
        self.dots_army_info_banners = {}
        self.dots_settlement_info_banners = {}
        self.dots_settlement_name_banners = {}
        self.travel_dot_images = {1: {}, 2: {}, 3: {}, 4: {}}  # get added during campaign prepare
        self.grand_ui_images = self.game.grand_ui_images
        self.cosmos_ui_images = self.game.cosmos_ui_images

        self.mini_map = GrandMiniMap((self.screen_width - ((796 / 2) * self.screen_scale_width),
                                      self.screen_height - (432 * self.screen_scale_height)),
                                     (796, 432), "grand", layer=4)
        self.map_setting_option_ui = MapSettingOption()
        self.event_detail_popup = EventDetailPopup()

        self.drama_text = GrandTextDrama(self)  # message at the top of screen that show up for important event
        self.player_interact = PlayerGrandInteract()

        self.player_grand_reserve_army_setup_ui = PresetArmyReserveSetup(
            (self.screen_width * 0.45, self.screen_height * 0.2),
            True)
        self.player_grand_reserve_army_list_ui = PresetArmyReserveList(
            self.player_grand_reserve_army_setup_ui.rect.topleft)
        self.player_grand_character_selector_ui = PresetArmyGrandCharacterSelector(
            (self.screen_width * 0.78, self.screen_height * 0.2))
        self.player_reserve_army_title = CustomPresetTitle((self.game.screen_width * 0.8, 80 * self.screen_scale_height),
                                                          (self.screen_rect.width / 2,
                                                           self.player_grand_reserve_army_setup_ui.rect.midtop[1]))

        self.player_army_reserve_setup_uis = (self.player_grand_reserve_army_list_ui,
                                              self.player_grand_reserve_army_list_ui.scroll,
                                              self.player_reserve_army_title,
                                              self.player_grand_reserve_army_setup_ui,
                                              self.player_grand_character_selector_ui,
                                              self.player_grand_character_selector_ui.scroll)

        self.player_top_bar_ui = PlayerTopBar()
        self.player_faction_culture_list_ui = PlayerFactionCultureList()
        self.time_setting_ui = TimeSettingOption()
        self.menu_bar_ui = MenuBar()
        self.cosmic_ui = CosmosUI()
        self.mini_cosmic_ui = MiniCosmosUI(self.game.cosmos_ui_images, self.cosmic_ui)

        self.player_army_list_sort_option_ui = PlayerArmyListSortOption()
        self.player_army_list_ui = PlayerArmyList()
        self.court_management_ui = CourtManagement()
        self.court_management_uis = (self.court_management_ui, self.court_management_ui.scroll)

        self.culture_management_ui = CultureManagement()
        self.culture_management_uis = (self.culture_management_ui, self.culture_management_ui.scroll)

        self.diplomacy_management_ui = DiplomacyManagement()
        self.diplomacy_management_uis = (self.diplomacy_management_ui, self.diplomacy_management_ui.scroll)

        self.region_management_ui = RegionManagement()

        region_manage_toggle_button = {"selected": self.grand_ui_images["selected_region_manage_button"],
                                       "unselected": self.grand_ui_images["unselected_region_manage_button"]}
        self.region_management_tab_button = RegionManagementToggleButton(region_manage_toggle_button,
                                                                         self.grab_text(("ui", "button_region_manage")),
                                                                         self.region_management_ui.rect.topleft)
        self.army_deploy_tab_button = ArmyDeployToggleButton(region_manage_toggle_button,
                                                             self.grab_text(("ui", "button_army_deploy")),
                                                             self.region_management_tab_button.rect.bottomright)

        self.player_region_management_uis = (self.region_management_ui, self.region_management_tab_button,
                                             self.army_deploy_tab_button)
        self.building_management_ui = BuildingManagement()

        self.army_management_ui = ArmyManagement()
        self.player_army_management_uis = (self.army_management_ui, self.army_deploy_tab_button)

        self.event_notification_ui = EventNotification()

        self.fps_count = FPSCount(self)  # FPS number counter

        # Battle ESC menu
        esc_menu_dict = self.make_esc_menu()

        self.grand_menu_button = esc_menu_dict["grand_menu_button"]
        self.esc_option_menu_button = esc_menu_dict["esc_option_menu_button"]
        self.esc_slider_menu = esc_menu_dict["esc_slider_menu"]
        self.esc_value_boxes = esc_menu_dict["esc_value_boxes"]
        self.esc_option_text = esc_menu_dict["volume_texts"]

        self.only_player_uis = (self.player_top_bar_ui, self.player_faction_culture_list_ui,
                                self.player_army_list_sort_option_ui, self.player_army_list_ui,
                                self.player_army_list_ui.scroll, self.event_notification_ui)

        self.player_collapsable_uis = (self.region_management_ui, self.region_management_tab_button,
                                       self.army_deploy_tab_button, self.building_management_ui,
                                       self.army_management_ui, self.army_deploy_tab_button,
                                       self.court_management_ui, self.court_management_ui.scroll,
                                       self.diplomacy_management_ui, self.diplomacy_management_ui.scroll,
                                       self.culture_management_ui, self.culture_management_ui.scroll, self.cosmic_ui)

        self.always_uis = (self.player_interact, self.mini_map, self.map_setting_option_ui,
                           self.mini_cosmic_ui, self.time_setting_ui, self.menu_bar_ui, self.cursor)

        self.add_to_outer_ui_menu_updater(self.always_uis)

    def prepare_new_campaign(self, campaign, player_faction, save_state_data=None):
        for message in self.inner_prepare_new_campaign(campaign, player_faction, save_state_data):
            self.game.error_log.write("Start Campaign:" + "." + str(campaign))
            print(message, end="")

    def inner_prepare_new_campaign(self, campaign, player_faction, save_state_data):
        self.campaign = campaign
        self.player_faction = player_faction
        self.current_campaign_state = save_state_data

        # Stop all effect sound
        for sound_ch in self.effect_sound_channels:
            if sound_ch.get_busy():
                sound_ch.stop()
        self.ambient_channel.stop()
        self.music_channel.stop()
        self.current_music = None
        self.current_ambient = None

        print("Start loading", campaign)
        yield set_start_load(self, "Campaign setup")
        if self.game.show_fps:
            self.add_to_outer_ui_menu_updater(self.fps_count)
        else:
            self.remove_from_outer_ui_menu_updater(self.fps_count)

        grand_config = configparser.ConfigParser()  # initiate config reader
        grand_config.read_file(open(join(self.data_dir, "map", "world", campaign, "grand.ini")))  # read config file
        self.shown_world_map_width = int(grand_config["MAP"]["map_width"]) * self.screen_scale_width
        self.shown_world_map_height = int(grand_config["MAP"]["map_height"]) * self.screen_scale_height

        self.base_world_map = self.map_data.base_world_map
        self.faction_list = self.map_data.faction_list
        self.region_by_colour_index = self.map_data.region_by_colour_index
        self.region_by_pos_index = self.map_data.region_by_pos_index
        self.region_list = self.map_data.region_list
        self.route_list = self.map_data.route_list

        self.map_shown_to_base_scale_width = self.shown_world_map_width / self.base_world_map.get_width()
        self.map_shown_to_base_scale_height = self.shown_world_map_height / self.base_world_map.get_height()

        self.map_x_end = self.shown_world_map_width - self.screen_width
        self.map_y_end = self.shown_world_map_height - self.screen_height

        self.sprite_data.load_region_sprite(self.map_data, self.grand_ui_images, self.map_shown_to_base_scale_width,
                                            self.map_shown_to_base_scale_height, campaign)

        # create map of dots army occupation for battle engage checking
        self.settlement_dots = {value["Settlement POS"]: key for key, value in self.map_data.region_list.items()}
        self.dots_army_occupation = {key: [] for key in self.settlement_dots}

        banner_offset = 200 * self.screen_scale_height
        for route_data in self.map_data.route_list.values():
            for dot in route_data["Dots"]:
                dot_pos_x = dot[0] * self.map_shown_to_base_scale_width
                dot_pos_y = dot[1] * self.map_shown_to_base_scale_height
                army_dot_pos_y_offset = (50 * self.screen_scale_height)
                if dot in self.settlement_dots:  # settlement dot
                    army_dot_pos_y_offset = (200 * self.screen_scale_height)
                    self.dots_settlement_name_banners[dot] = DotNameBannerSettlement(
                        dot, (dot_pos_x, (dot_pos_y - banner_offset)),
                        self.settlement_dots[dot])
                    self.dots_settlement_info_banners[dot] = DotInfoBannerSettlement(
                        dot, (dot_pos_x, (dot_pos_y + banner_offset)),
                        self.settlement_dots[dot])
                self.dots_army_occupation[dot] = []
                self.dots_army_info_banners[dot] = DotInfoBannerArmy(
                    dot, (dot_pos_x, dot_pos_y + army_dot_pos_y_offset))

        # setup armies, replace dict with object
        for faction, faction_state in self.current_campaign_state["faction"].items():
            for index, army in enumerate(tuple(faction_state["army"])):
                self.create_new_army(faction_state, army, index=index, sort=False, no_assemble=True)

        # create route graph for pathfinding
        if not self.current_campaign_state["pathfinding"]:
            self.create_campaign_route_pathfinding()

        # setup ui
        if self.player_faction:
            self.player_faction_culture_list_ui.culture_change()
            self.diplomacy_management_ui.reset()
        self.mini_map.region_control_data = {}
        self.mini_map.change_grand_setup(self.map_data.base_world_map)
        self.mini_map.change_grand_faction(self.current_campaign_state["region"])
        self.cosmic_ui.reset(self.current_campaign_state["cosmic_time"])
        self.mini_cosmic_ui.reset()

        self.settlement_object_list = {}
        self.wonder_object_list = {}
        for region, region_state in self.current_campaign_state["region"].items():
            region_buildings = self.current_campaign_state["region"][region]["building"]
            # create region objects
            GrandRegion(region, self.region_list[region]["Region POS"],
                        self.current_campaign_state["region"][region]["control"])

            # create wonder objects
            for key, region_object in region_state["object"].items():
                self.wonder_object_list[(region, key)] = GrandObject(region_object[0],
                                                                     (region_object[1], region_object[2]),
                                                                     region_buildings[key])

            # create settlement objects
            self.settlement_object_list[region] = (
                SettlementObject(region, self.region_list[region]["Settlement POS"], region_buildings[0]))

        # setup camera position
        self.mini_map.camera_pos = None
        if self.current_campaign_state["player_camera_pos"]:
            self.camera_topleft_pos = self.current_campaign_state["player_camera_pos"]
        else:  # new game
            if player_faction:
                for region in self.region_list.values():
                    if region["Capital"] and region["Control"] == player_faction:
                        self.camera_topleft_pos = Vector2((region["Settlement POS"][0] *
                                                           self.map_shown_to_base_scale_width) - self.camera_center_x,
                                                          (region["Settlement POS"][1] *
                                                           self.map_shown_to_base_scale_height) - self.camera_center_y)
                        break
            else:  # no player faction, camera at center of grand map
                self.camera_topleft_pos = Vector2((self.shown_world_map_width / 2) - self.camera_center_x,
                                                  (self.shown_world_map_height / 2) - self.camera_center_y)

        if player_faction:
            self.player_input = MethodType(player_input_grand, self)
            self.add_to_outer_ui_menu_updater(self.only_player_uis)
            self.player_army_list_ui.reset()
        else:  # no player faction, camera at center
            self.player_input = MethodType(battle_no_player_input_grand, self)
            self.remove_from_outer_ui_menu_updater(self.only_player_uis)

        self.change_turn(turn_change=False)
        self.sort_player_army_list()

        self.event_notification_ui.update_image()
        self.fix_camera()

        self.input_popup = None  # no popup asking for user text input state
        self.drama_text.queue = []  # reset drama text popup queue

        self.game_speed = 0  # always start new campaign with time pause
        self.show_route = True
        self.screen_shake_value = 0
        self.ui_timer = 0
        self.drama_timer = 0
        self.dt = 0
        self.phase_timer = 0

        self.base_cursor_pos = [0, 0]  # mouse pos on the map based on camera position
        self.cursor_pos = [0, 0]

        self.player_key_bind = self.game.player_key_bind_list
        self.player_key_bind_name = {value: key for key, value in self.player_key_bind.items()}
        self.player_key_press = {key: False for key in self.player_key_bind}
        self.player_key_hold = {key: False for key in self.player_key_bind}

        self.screen.fill((0, 0, 0))
        self.add_to_outer_ui_menu_updater(self.cursor)
        yield set_done_load()

    def run_grand(self):
        frame = 0
        while True:  # grand running
            self.screen.fill((120, 120, 200))  # draw sea
            self.remove_from_outer_ui_menu_updater(self.text_popup)

            frame += 1

            if frame >= 30 and hasattr(self.game, "profiler"):  # Remove for stable release, along with dev key
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
            self.cursor_pos = Vector2(self.cursor.pos[0] + self.camera_topleft_pos[0],
                                      self.cursor.pos[1] + self.camera_topleft_pos[1])
            self.base_cursor_pos = Vector2(  # mouse pos on the map based on camera position
                (self.cursor_pos[0] / self.map_shown_to_base_scale_width,
                 self.cursor_pos[1] / self.map_shown_to_base_scale_height))

            for event in pygame.event.get():  # get event that happen
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 4:  # Mouse scroll down
                        self.cursor.scroll_up = True
                    elif event.button == 5:  # Mouse scroll up
                        self.cursor.scroll_down = True
                elif event.type == pygame.KEYDOWN:
                    event_key_press = event.key
                    if event_key_press in self.player_key_bind_name:  # check for key press
                        self.player_key_press[self.player_key_bind_name[event_key_press]] = True
                    if event_key_press == K_ESCAPE or self.player_key_press["Menu/Cancel"]:  # accept esc button always
                        self.esc_press = True

                    # FOR DEVELOPMENT comment out later
                    if event.key == K_F1:
                        self.drama_text.queue.append((True, "Hello and welcome to showcase video", "dollhi"))
                    elif event.key == K_F2:
                        self.drama_text.queue.append((True, "Showcase: Grand strategy campaign development and cosmos system", None))
                    # elif event.key == K_F3:
                    # elif event.key == K_F6:
                    # self.screen_shake_value = 11111
                    # elif event.key == K_F7:
                    # self.screen_shake_value = 11111
                    elif event.key == K_F11:  # clear profiler
                        if hasattr(self.game, "profiler"):
                            self.game.profiler.clear()
                    elif event.key == K_F12:  # show/hide profiler
                        if not hasattr(self.game, "profiler"):
                            self.game.setup_profiler()
                        self.game.profiler.switch_show_hide()
                elif event.type == QUIT:  # quit game
                    pygame.quit()
                    sys.exit()

            return_state = self.state_process()  # run code based on current state
            if return_state is not None:
                self.exit_grand()
                return return_state

            display.update()  # update game display, draw everything
            self.clock.tick(1000)  # clock update even if self pause

    def add_to_ui_menu_updater(self, *args):
        self.ui_menu_updater.add(*args)
        self.ui_menu_drawer.add(*args)

    def remove_from_ui_menu_updater(self, *args):
        self.ui_menu_updater.remove(*args)
        self.ui_menu_drawer.remove(*args)

    def add_to_outer_ui_menu_updater(self, *args):
        self.outer_ui_updater.add(*args)
        self.outer_ui_drawer.add(*args)

    def remove_from_outer_ui_menu_updater(self, *args):
        self.outer_ui_updater.remove(*args)
        self.outer_ui_drawer.remove(*args)

    def exit_grand(self):
        # remove menu and ui
        self.remove_from_ui_menu_updater(self.grand_menu_button.values(), self.esc_slider_menu.values(),
                                         self.esc_value_boxes.values(), self.esc_option_text.values(),
                                         self.player_collapsable_uis)

        # stop all sounds
        self.music_channel.stop()
        self.ambient_channel.stop()
        for sound_ch in self.effect_sound_channels:
            if sound_ch.get_busy():
                sound_ch.stop()
        self.current_music = None
        self.current_ambient = None

        # remove all reference from battle object
        self.player_army_list_ui.reset()
        self.time_setting_ui.reset()
        self.player_selected_army = []
        self.campaign = None
        self.player_faction = None
        self.player_input = None
        self.current_campaign_state = {}
        self.settlement_dots = {}
        self.dots_army_occupation.clear()
        for dot in self.dots_army_info_banners:
            self.dots_army_info_banners[dot].kill()
        self.dots_army_info_banners.clear()
        for dot in self.dots_settlement_name_banners:
            self.dots_settlement_name_banners[dot].kill()
        self.dots_settlement_name_banners.clear()
        for dot in self.dots_settlement_info_banners:
            self.dots_settlement_info_banners[dot].kill()
        self.dots_settlement_info_banners.clear()

        self.region_by_colour_index = {}
        self.region_list = {}
        self.route_list = {}

        self.ai_process_list = []

        clean_group_object((self.grand_camera_ui_updater, self.grand_object_updater, self.grand_effect_updater))

        self.sound_effect_queue = {}

        self.drama_timer = 0  # reset drama text popup
        self.remove_from_ui_menu_updater(self.drama_text)
