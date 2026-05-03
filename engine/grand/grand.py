import sys
from random import randint
from types import MethodType

import pygame
from pygame import Vector2, display, sprite, Surface, SRCALPHA
from pygame.locals import *
from pygame.mixer import Channel
from pygame.transform import rotate

from engine.army.army import Army
from engine.battle.add_sound_effect_queue import add_sound_effect_queue
from engine.battle.battle import set_start_load, set_done_load
from engine.battle.cal_shake_value import cal_shake_value
from engine.battle.drama_process import drama_process
from engine.battle.play_sound_effect import play_sound_effect
from engine.battle.shake_camera import shake_camera
from engine.camera.camera import Camera
from engine.constants import Route_Difficulty_Colour
from engine.game.activate_input_popup import activate_input_popup
from engine.game.change_pause_update import change_pause_update
from engine.grand.auto_battle_process import auto_battle_process
from engine.grand.cal_faction_culture import cal_faction_culture
from engine.grand.cal_faction_income import cal_faction_income
from engine.grand.cal_region_income import cal_region_income
from engine.grand.change_phase import change_phase
from engine.grand.change_turn import change_turn
from engine.grand.create_campaign_route_pathfinding import create_campaign_route_pathfinding
from engine.grand.create_new_army import create_new_army
from engine.grand.draw_route import draw_route
from engine.grand.fix_camera import fix_camera
from engine.grand.player_input import player_input_grand, battle_no_player_input_grand
from engine.grand.sort_player_army_list import sort_player_army_list
from engine.grand.state_grand_process import state_grand_process
from engine.grandactor.grandactor import GrandActor, GrandFactionActorCircle
from engine.grandmap.grandmap import GrandMap
from engine.grandobject.grandobject import GrandObject
from engine.uibattle.drama import TextDrama
from engine.uibattle.uibattle import FPSCount
from engine.uigrand.uigrand import (YesNo, PlayerGrandInteract, PlayerFactionResourceBar, PlayerFactionCultureList,
                                    PlayerArmyList, PlayerArmyListSortOption, MiniTimeOrb, MapSettingOption,
                                    TimeInfoBar, TimeSettingOption, EventImportantPopup,
                                    MenuBar, RegionManagement, EventNotification, ArmyInfo)
from engine.uimenu.uimenu import TextPopup, GrandMiniMap, UIScroll, PresetArmySetupUI, CharacterSelector
from engine.updater.updater import ReversedLayeredUpdates
from engine.utils.common import clean_group_object
from engine.utils.data_loading import load_image, load_images


class Grand:
    grand = None
    cursor = None

    activate_input_popup = activate_input_popup
    add_sound_effect_queue = add_sound_effect_queue
    auto_battle_process = auto_battle_process
    cal_faction_culture = cal_faction_culture
    cal_faction_income = cal_faction_income
    cal_region_income = cal_region_income
    cal_shake_value = cal_shake_value
    change_pause_update = change_pause_update
    change_phase = change_phase
    change_turn = change_turn
    create_campaign_route_pathfinding = create_campaign_route_pathfinding
    create_new_army = create_new_army
    drama_process = drama_process
    draw_route = draw_route
    fix_camera = fix_camera
    play_sound_effect = play_sound_effect
    shake_camera = shake_camera
    sort_player_army_list = sort_player_army_list
    state_grand_process = state_grand_process

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
        self.grand_camera_object_drawer = sprite.LayeredUpdates()
        self.grand_camera_ui_drawer = sprite.LayeredUpdates()  # this is drawer for ui in grand campaign, does not move alonge with camera
        self.outer_ui_updater = sprite.LayeredUpdates()
        self.ui_updater = ReversedLayeredUpdates()  # this is updater and drawer for ui, all image pos should be based on the screen
        self.ui_drawer = sprite.LayeredUpdates()
        self.grand_actor_updater = ReversedLayeredUpdates()  # updater for actor objects,
        self.grand_effect_updater = sprite.Group()  # updater for effect objects

        GrandActor.containers = self.grand_actor_updater, self.grand_camera_object_drawer
        GrandFactionActorCircle.containers = self.grand_actor_updater, self.grand_camera_object_drawer

        GrandObject.containers = self.grand_actor_updater, self.grand_camera_object_drawer

        # Music and sound player
        self.current_music = None
        self.current_ambient = None
        self.music_channel = self.game.music_channel
        self.ambient_channel = self.game.ambient_channel
        self.weather_ambient_channel = self.game.weather_ambient_channel
        self.button_sound_channel = self.game.button_sound_channel
        self.SONG_END = pygame.USEREVENT + 1

        self.effect_sound_channel = tuple([Channel(ch_num) for ch_num in range(4, 1000)])

        self.text_popup = TextPopup()

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
        # self.default_grand_music_pool = [Sound(self.music_pool[str(index)]) for index in range(1, 10)]
        self.stage_music_pool = {}  # pool for music already converted to pygame Sound

        self.weather_screen_adjust = self.screen_width / self.screen_height  # for weather sprite spawn position

        self.character_data = self.game.character_data
        self.character_list = self.game.character_list
        self.map_data = self.game.map_data
        self.weather_data = self.map_data.weather_data
        self.faction_list = self.map_data.faction_list
        self.building_list = self.character_data.building_list
        self.culture_list = self.character_data.culture_list

        self.sprite_data = self.game.sprite_data
        self.grand_ui_icons = self.sprite_data.grand_ui_icons
        self.character_animation_data = self.sprite_data.character_animation_data
        self.character_portraits = self.sprite_data.character_portraits
        self.effect_animation_pool = self.sprite_data.effect_animation_pool
        self.language = self.game.language
        self.localisation = self.game.localisation
        self.save_data = game.save_data
        self.main_story_profile = self.game.save_data.save_profile

        self.game_speed = 0
        self.phase_timer = 0
        self.show_route = True

        self.screen = self.game.screen

        # Create the game camera
        self.camera_pos = Vector2(500, 500)  # camera pos on scene
        self.shown_camera_topleft_pos = self.camera_pos  # pos of camera shown to player, in case of screen shaking or other effects

        self.camera = Camera(self.screen, (self.camera_width, self.camera_height))
        self.camera_w_center = self.camera.camera_w_center
        self.camera_h_center = self.camera.camera_h_center
        self.camera_x_shift = self.shown_camera_topleft_pos[0] - self.camera_w_center

        # Create map object
        GrandMap.grand = self
        GrandMap.image = Surface.subsurface(self.camera.image, (0, 0, self.camera.image.get_width(),
                                                                self.camera.image.get_height()))
        self.map_x_end = 0
        self.map_y_end = 0
        self.map_shown_to_actual_scale_width = 1
        self.map_shown_to_actual_scale_height = 1
        self.grand_map = GrandMap()

        Army.grand = self
        GrandActor.grand = self
        GrandFactionActorCircle.grand = self
        GrandObject.grand = self
        GrandFactionActorCircle.screen_scale = self.screen_scale
        GrandObject.screen_scale = self.screen_scale

        # Create grand ui
        self.travel_dot_images = {1: {}, 2: {}, 3: {}, 4: {}}  # get added during campaign prepare
        grand_ui_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                      subfolder=("ui", "grand_ui"))
        self.decision_select = YesNo(grand_ui_images)
        self.mini_map = GrandMiniMap((self.screen_width - ((796 / 2) * self.screen_scale_width),
                                      self.screen_height - (432 * self.screen_scale_height)),
                                     (796, 432), "grand")
        self.map_setting_option_ui = MapSettingOption()
        self.event_important_popup = EventImportantPopup()

        self.drama_text = TextDrama(self)  # message at the top of screen that show up for important event
        self.player_grand_interact = PlayerGrandInteract()

        self.player_grand_preset_army_setup = PresetArmySetupUI((self.screen_width * 0.4, self.screen_height * 0.2),
                                                                True)
        self.player_army_info_ui = ArmyInfo(self.player_grand_preset_army_setup.rect.topleft)
        self.player_grand_character_selector = CharacterSelector((self.screen_width * 0.78, self.screen_height * 0.2))

        self.player_faction_resource_bar_ui = PlayerFactionResourceBar()
        self.player_faction_culture_list_ui = PlayerFactionCultureList()
        self.mini_time_orb_ui = MiniTimeOrb()
        self.time_info_bar_ui = TimeInfoBar()
        self.time_setting_ui = TimeSettingOption()
        self.menu_bar_ui = MenuBar()
        self.player_army_list_sort_option_ui = PlayerArmyListSortOption()
        self.player_army_list_ui = PlayerArmyList()
        self.player_army_list_scroll = UIScroll(self.player_army_list_ui,
                                                self.player_army_list_ui.rect.topright)

        self.region_management_ui = RegionManagement()
        self.event_notification_ui = EventNotification()

        self.fps_count = FPSCount(self)  # FPS number counter
        if self.game.show_fps:
            self.outer_ui_updater.add(self.fps_count)

        self.clock_time = 0
        self.true_dt = 0
        self.dt = 0  # Realtime used for time calculation
        self.screen_shake_value = 0  # count for how long to shake camera

        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0

        self.base_cursor_pos = [0, 0]  # mouse base pos on the map based on camera position
        self.cursor_pos = [0, 0]

        self.player_selected_army = []
        self.player_selected_region = None
        self.campaign = None
        self.player_faction = None
        self.player_input = None
        self.current_campaign_state = {}
        self.dots_army_occupation = {}

        self.region_by_colour_list = {}
        self.region_list = {}
        self.route_list = {}
        self.route_dot_draw_array = {}

        self.always_ui = (self.player_grand_interact, self.mini_map, self.map_setting_option_ui,
                          self.mini_time_orb_ui, self.time_info_bar_ui,
                          self.time_setting_ui, self.menu_bar_ui, self.event_notification_ui)

        self.only_player_ui = (self.player_faction_resource_bar_ui, self.player_faction_culture_list_ui,
                               self.player_army_list_sort_option_ui, self.player_army_list_ui,
                               self.player_army_list_scroll)

        self.outer_ui_updater.add(self.always_ui)

    def prepare_new_campaign(self, campaign, player_faction, save_state_data=None):
        for message in self.inner_prepare_new_campaign(campaign, player_faction, save_state_data):
            self.game.error_log.write("Start Campaign:" + "." + str(campaign))
            print(message, end="")

    def inner_prepare_new_campaign(self, campaign, player_faction, save_state_data):
        self.campaign = campaign
        self.player_faction = player_faction
        self.current_campaign_state = save_state_data

        # Stop all sound
        for sound_ch in self.effect_sound_channel:
            if sound_ch.get_busy():
                sound_ch.stop()
        self.current_music = None
        self.current_ambient = None

        print("Start loading", campaign)
        yield set_start_load(self, "Campaign setup")
        self.game.loading_lore_text = self.localisation.grab_text(
            ("load", randint(0, len(self.localisation.text[self.language]["load"]) - 1), "Text"))

        self.map_x_end, self.map_y_end = self.grand_map.setup(self.map_data.world_map, load_image(
            self.data_dir, self.screen_scale, "grand.png", ("map", "world", campaign),
            no_alpha=True))

        self.map_shown_to_actual_scale_width = self.grand_map.map_shown_to_actual_scale_width
        self.map_shown_to_actual_scale_height = self.grand_map.map_shown_to_actual_scale_height

        self.faction_list = self.map_data.faction_list
        self.region_by_colour_list = self.map_data.region_by_colour_list
        self.region_list = self.map_data.region_list
        self.route_list = self.map_data.route_list

        travel_dot_images = {1: None, 2: None, 3: None, 4: None}
        for key in travel_dot_images:
            dot_image = Surface((20 * self.screen_scale_width, 30 * self.screen_scale_height), SRCALPHA)
            dot_image.fill((0, 0, 0))
            difficulty_part = Surface((10 * self.screen_scale_width, 15 * self.screen_scale_height), SRCALPHA)
            difficulty_part.fill(Route_Difficulty_Colour[key])
            dot_image.blit(difficulty_part, difficulty_part.get_rect(center=(dot_image.get_width() / 2,
                                                                             dot_image.get_height() / 2)))
            travel_dot_images[key] = dot_image

        route_dot_draw_array = {}
        map_data_route_dot_draw_array = self.map_data.route_dot_draw_array
        for x in map_data_route_dot_draw_array:
            scale_x = x * self.grand_map.map_shown_to_actual_scale_width
            route_dot_draw_array[scale_x] = {}
            for y in map_data_route_dot_draw_array[x]:
                scale_y = y * self.grand_map.map_shown_to_actual_scale_height
                angle = map_data_route_dot_draw_array[x][y]
                difficulty = self.map_data.dot_route_difficulty[(x, y)]
                if angle not in self.travel_dot_images[difficulty]:
                    self.travel_dot_images[difficulty][angle] = rotate(travel_dot_images[difficulty], angle)
                route_dot_draw_array[scale_x][scale_y] = self.travel_dot_images[difficulty][angle]
        self.route_dot_draw_array = route_dot_draw_array

        # load actor animation sprite
        self.sprite_data.setup_campaign()

        # create map of dots army occupation for battle engage checking
        self.dots_army_occupation = {value["Settlement POS"]: [] for value in self.map_data.region_list.values()}
        for route_data in self.map_data.route_list.values():
            for dot in route_data["Dots"]:
                self.dots_army_occupation[dot] = []

        # setup armies, replace dict with object
        for faction, faction_value in self.current_campaign_state["faction"].items():
            for index, army in enumerate(tuple(faction_value["army"])):
                self.create_new_army(faction_value["army"], army, index=index, sort=False)

        # create route graph for pathfinding
        if not self.current_campaign_state["pathfinding"]:
            self.create_campaign_route_pathfinding()

        # setup ui
        if self.player_faction:
            self.player_faction_culture_list_ui.culture_change()
        self.mini_map.change_grand_setup(self.map_data.world_map)
        self.mini_map.change_grand_faction(self.current_campaign_state["region"]["control"])

        campaign_building_state = self.current_campaign_state["region"]["buildings"]
        for region, region_objects in self.current_campaign_state["region"]["objects"].items():
            for key, region_object in region_objects.items():
                wonder = GrandObject(region_object[0], (region_object[1], region_object[2]), region_object[3])
                wonder.change_state(campaign_building_state[region][key][1])  # change based on its building state

        # setup camera position
        if self.current_campaign_state["player_camera_pos"]:
            self.camera_pos = self.current_campaign_state["player_camera_pos"]
        else:  # new game
            if player_faction:
                for region in self.region_list.values():
                    if region["Capital"] and region["Control"] == player_faction:
                        self.camera_pos = Vector2((region["Settlement POS"][0] *
                                                   self.grand_map.map_shown_to_actual_scale_width) - self.camera_center_x,
                                                  (region["Settlement POS"][1] *
                                                   self.grand_map.map_shown_to_actual_scale_height) - self.camera_center_y)
                        break
            else:  # no player faction, camera at center of grand map
                self.camera_pos = Vector2((self.grand_map.full_shown_map_image.get_width() / 2) - self.camera_center_x,
                                          (self.grand_map.full_shown_map_image.get_height() / 2) - self.camera_center_y)

        if player_faction:
            self.player_input = MethodType(player_input_grand, self)
            self.outer_ui_updater.add(self.only_player_ui)
            self.player_army_list_ui.reset_list()
        else:  # no player faction, camera at center
            self.player_input = MethodType(battle_no_player_input_grand, self)
            self.outer_ui_updater.remove(self.only_player_ui)

        for faction in self.faction_list:
            if faction != "free":
                self.cal_faction_culture(faction)

                for region in self.current_campaign_state["faction"][faction]["region"]:
                    self.cal_region_income(region)

                self.cal_faction_income(faction)

        self.event_notification_ui.update_image()
        self.fix_camera()

        self.input_popup = None  # no popup asking for user text input state
        self.drama_text.queue = []  # reset drama text popup queue

        self.music_channel.set_endevent(self.SONG_END)

        self.shown_camera_topleft_pos = self.camera_pos

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
        self.outer_ui_updater.add(self.cursor)

        yield set_done_load()

    def run_grand(self):
        frame = 0
        while True:  # grand running
            self.outer_ui_updater.remove(self.text_popup)
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
            self.cursor_pos = Vector2(self.cursor.pos[0] + self.camera_pos[0],
                                      self.cursor.pos[1] + self.camera_pos[1])
            self.base_cursor_pos = Vector2(  # mouse pos on the map based on camera position
                (self.cursor_pos[0] / self.map_shown_to_actual_scale_width,
                 self.cursor_pos[1] / self.map_shown_to_actual_scale_height))

            for event in pygame.event.get():  # get event that happen
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 4:  # Mouse scroll down
                        self.cursor.scroll_up = True
                    elif event.button == 5:  # Mouse scroll up
                        self.cursor.scroll_down = True
                # elif event.type == self.SONG_END: # whatever music end, pick random from default battle music
                #     self.music.play(choice(self.default_battle_music_pool), fade_ms=100)

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
                        self.drama_text.queue.append(True, ("Hello and welcome to showcase video", "Dollhi"))
                    # elif event.key == K_F2:
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

            if self.input_popup:  # currently, have input text pop up on screen, stop everything else until done.
                if self.input_ok_button.event_press:
                    done = True

                    if self.input_popup[1] in ("retreat", "retreat_assemble"):
                        # for army in self.player_selected_army:  # TODO finish retreat function here
                        # all army in the same battles retreat and lose battle
                        # for battle in self.current_campaign_state["battle"]["auto battles"]:
                        # for army in self.player_selected_army:
                        #     army.issue_move_command(self.input_popup[2])
                        pass
                    elif self.input_popup[1] == "assemble":
                        for army in self.player_selected_army:
                            army.issue_move_command(self.input_popup[2])

                    elif self.input_popup[1] == "quit":
                        pygame.time.wait(1000)
                        pygame.quit()
                        sys.exit()

                    if done:
                        self.change_pause_update(False)
                        self.input_box.render_text("")
                        self.input_popup = None
                        self.remove_from_ui_updater(self.all_input_popup_uis)

                elif self.input_cancel_button.event_press or self.input_close_button.event_press or self.esc_press:
                    self.change_pause_update(False)
                    self.input_box.render_text("")
                    self.input_popup = None
                    self.remove_from_ui_updater(self.all_input_popup_uis)

                # elif self.input_popup[0] == "text_input":
                #     if not self.text_delay:
                #         if key_press[self.input_box.hold_key]:
                #             self.input_box.player_input(None, key_press)
                #             self.text_delay = 0.15
                #     else:
                #         self.text_delay -= self.dt
                #         if self.text_delay < 0:
                #             self.text_delay = 0.
            else:
                # Update game time
                dt = self.true_dt * self.game_speed
                self.dt = dt  # apply dt with game_speed for calculation
                self.shown_camera_topleft_pos = self.camera_pos.copy()

                self.player_input()

                if dt:
                    if dt > 0.016:  # one frame update should not be longer than 0.016 second (60 fps) for calculation.
                        dt = 0.016  # make it so stutter and lag does not cause overtime issue.

                    self.state_grand_process(dt)

                    self.ui_timer += self.true_dt  # ui update by real time instead of self time to reduce workload.

                    # Screen shaking
                    if self.screen_shake_value:
                        decrease = 1000
                        if self.screen_shake_value > decrease:
                            decrease = self.screen_shake_value
                        self.screen_shake_value -= (dt * decrease)
                        if self.screen_shake_value < 0:
                            self.screen_shake_value = 0
                        else:
                            self.shake_camera()

                    if self.sound_effect_queue:
                        for key, value in self.sound_effect_queue.items():  # play each sound effect initiate in this loop
                            self.play_sound_effect(key, value)
                        self.sound_effect_queue = {}

                    self.drama_process()

                    if self.ui_timer >= 0.1:
                        self.ui_drawer.draw(self.screen)  # draw the UI
                        self.ui_timer -= 0.1

                # Object related updater
                self.grand_actor_updater.update(self.true_dt, dt)
                self.grand_effect_updater.update(self.true_dt)

                # update camera
                self.camera.camera_left_bound = self.shown_camera_topleft_pos[0]
                self.camera.camera_top_bound = self.shown_camera_topleft_pos[1]
                self.camera.camera_right_bound = self.camera.camera_left_bound + self.screen_width
                self.camera.camera_bottom_bound = self.camera.camera_top_bound + self.screen_height
                self.grand_map.update()
                if self.show_route:
                    # add route after map update draw to blit route dots on the map under other sprites.
                    self.draw_route()

            self.camera.update(self.grand_camera_object_drawer)
            self.ui_updater.update(dt)
            self.outer_ui_updater.update(dt)
            self.camera.update(self.grand_camera_ui_drawer)
            self.camera.out_update(self.outer_ui_updater)

            display.update()  # update game display, draw everything
            self.clock.tick(1000)  # clock update even if self pause

    def add_to_ui_updater(self, *args):
        self.ui_updater.add(*args)
        self.ui_drawer.add(*args)

    def remove_from_ui_updater(self, *args):
        self.ui_updater.remove(*args)
        self.ui_drawer.remove(*args)

    def exit_battle(self):
        # remove menu and ui
        self.remove_from_ui_updater(self.battle_menu_button.values(), self.esc_slider_menu.values(),
                                    self.esc_value_boxes.values(), self.esc_option_text.values(),
                                    self.scene_translation_text_popup)

        # stop all sounds
        for sound_ch in self.effect_sound_channel:
            if sound_ch.get_busy():
                sound_ch.stop()
        self.current_music = None
        self.current_ambient = None
        self.stage_music_pool = {}

        # remove all reference from battle object
        self.ai_process_list = []
        self.clean_character_group()

        clean_group_object((self.all_battle_characters, self.battle_character_updater, self.battle_effect_updater,
                            self.weather_matters,
                            self.player_leader_indicators))

        self.sound_effect_queue = {}

        self.drama_timer = 0  # reset drama text popup
        self.remove_from_ui_updater(self.drama_text)
