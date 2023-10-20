import ast
import configparser
import glob
import os.path
import sys

import pygame
from pygame.locals import *

from engine.battle.battle import Battle
from engine.character.character import Character, BodyPart
from engine.data.datalocalisation import Localisation
from engine.data.datamap import BattleMapData
from engine.data.datasprite import AnimationData
from engine.data.datastat import CharacterData
from engine.drop.drop import Drop
from engine.effect.effect import Effect, DamageEffect
# Method in game.setup
from engine.game.setup.create_sound_effect_pool import create_sound_effect_pool
from engine.game.setup.make_input_box import make_input_box
from engine.game.setup.make_lorebook import make_lorebook
from engine.game.setup.make_option_menu import make_option_menu
from engine.lorebook.lorebook import Lorebook, SubsectionName, lorebook_process
from engine.menubackground.menubackground import MenuActor, MenuRotate, StaticImage
from engine.stageobject.stageobject import StageObject
from engine.uibattle.uibattle import Profiler, FPSCount, DamageNumber, CharacterTextBox, \
    CharacterIndicator
from engine.uimenu.uimenu import OptionMenuText, SliderMenu, MenuCursor, BoxUI, BrownMenuButton, \
    URLIconLink, MenuButton, TextPopup, MapTitle, CharacterSelector, CharacterStatAllocator
from engine.updater.updater import ReversedLayeredUpdates
from engine.utils.common import edit_config
from engine.utils.data_loading import load_image, load_images, csv_read, load_base_button
from engine.utils.text_making import number_to_minus_or_plus
from engine.weather.weather import MatterSprite, SpecialWeatherEffect, Weather

game_name = "Royal Ordains"  # Game name that will appear as game name


class Game:
    game = None
    battle = None
    main_dir = None
    data_dir = None
    font_dir = None
    ui_font = None
    font_texture = None
    language = None
    localisation = None
    cursor = None
    ui_updater = None
    ui_drawer = None
    battle_camera = None

    player_list = (1, 2, 3, 4)

    screen_rect = None
    screen_scale = (1, 1)
    screen_size = ()

    game_version = "0.1.4"
    joystick_bind_name = {"XBox": {0: "A", 1: "B", 2: "X", 3: "Y", 4: "-", 5: "Home", 6: "+", 7: "Start", 8: None,
                                   9: None, 10: None, 11: "D-Up", 12: "D-Down", 13: "D-Left", 14: "D-Right",
                                   15: "Capture", "axis-0": "L. Stick Left", "axis+0": "L. Stick R.",
                                   "axis-1": "L. Stick U.", "axis+1": "L. Stick D.",
                                   "axis-2": "R. Stick Left", "axis+2": "R. Stick R.",
                                   "axis-3": "R. Stick U.", "axis+3": "R. Stick D.",
                                   "hat-0": "L. Arrow", "hat+0": "R. Arrow",
                                   "hat-1": "U. Arrow", "hat+1": "D. Arrow", },
                          "Other": {0: "1", 1: "2", 2: "3", 3: "4", 4: "L1", 5: "R1", 6: "L2", 7: "R2", 8: "Select",
                                    9: "Start", 10: "L. Stick", 11: "R. Stick", 12: None, 13: None, 14: None, 15: None,
                                    "axis-0": "L. Stick L.", "axis+0": "L. Stick R.",
                                    "axis-1": "L. Stick U.", "axis+1": "L. Stick D.",
                                    "axis-2": "R. Stick Left", "axis+2": "R. Stick R.",
                                    "axis-3": "R. Stick U.", "axis+3": "R. Stick D.",
                                    "hat-0": "L. Arrow", "hat+0": "R. Arrow",
                                    "hat-1": "U. Arrow", "hat+1": "D. Arrow",
                                    },
                          "PS": {0: "X", 1: "O", 2: "□", 3: "△", 4: "Share", 5: "PS", 6: "Options", 7: None, 8: None,
                                 9: None, 10: None, 11: "D-Up", 12: "D-Down", 13: "D-Left", 14: "D-R.",
                                 15: "T-Pad", "axis-0": "L. Stick L.", "axis+0": "L. Stick R.",
                                 "axis-1": "L. Stick U.", "axis+1": "L. Stick D.",
                                 "axis-2": "R. Stick Left", "axis+2": "R. Stick R.",
                                 "axis-3": "R. Stick U.", "axis+3": "R. Stick D.",
                                 "hat-0": "L. Arrow", "hat+0": "R. Arrow",
                                 "hat-1": "U. Arrow", "hat+1": "D. Arrow"}}

    # import from game
    from engine.game.activate_input_popup import activate_input_popup
    activate_input_popup = activate_input_popup

    from engine.game.assign_key import assign_key
    assign_key = assign_key

    from engine.game.back_mainmenu import back_mainmenu
    back_mainmenu = back_mainmenu

    from engine.game.change_pause_update import change_pause_update
    change_pause_update = change_pause_update

    from engine.game.change_sound_volume import change_sound_volume
    change_sound_volume = change_sound_volume

    from engine.game.create_config import create_config
    create_config = create_config

    from engine.game.loading_screen import loading_screen
    loading_screen = loading_screen

    from engine.game.menu_char import menu_char
    menu_char = menu_char

    from engine.game.menu_keybind import menu_keybind
    menu_keybind = menu_keybind

    from engine.game.menu_main import menu_main
    menu_main = menu_main

    from engine.game.menu_option import menu_option
    menu_option = menu_option

    from engine.game.start_battle import start_battle
    start_battle = start_battle

    lorebook_process = lorebook_process

    resolution_list = ("3200 x 1800", "2560 x 1440", "1920 x 1080", "1600 x 900", "1360 x 768",
                       "1280 x 720", "1024 x 576", "960 x 540", "854 x 480")

    def __init__(self, main_dir, error_log):

        Game.game = self
        Game.main_dir = main_dir
        Game.data_dir = os.path.join(self.main_dir, "data")
        Game.font_dir = os.path.join(self.data_dir, "font")

        self.config_path = os.path.join(self.main_dir, "configuration.ini")

        pygame.init()  # Initialize pygame

        pygame.mouse.set_visible(False)  # set mouse as not visible, use in-game mouse sprite

        self.error_log = error_log
        self.error_log.write("Game Version: " + self.game_version)

        save_folder_path = os.path.join(self.main_dir, "save")
        if not os.path.isdir(save_folder_path):
            os.mkdir(save_folder_path)

        # Read config file
        config = configparser.ConfigParser()  # initiate config reader
        try:
            config.read_file(open(self.config_path))  # read config file
        except FileNotFoundError:  # Create config file if not found with the default
            print('hmm')
            config = self.create_config()

        try:
            self.config = config
            self.show_fps = int(self.config["USER"]["fps"])
            self.screen_width = int(self.config["USER"]["screen_width"])
            self.screen_height = int(self.config["USER"]["screen_height"])
            self.full_screen = int(self.config["USER"]["full_screen"])
            self.master_volume = float(self.config["USER"]["master_volume"])
            self.music_volume = float(self.config["USER"]["music_volume"])
            self.play_music_volume = self.master_volume * self.music_volume / 10000  # convert volume into percentage
            self.effect_volume = float(self.config["USER"]["effect_volume"])
            self.play_effect_volume = self.master_volume * self.effect_volume / 10000
            self.voice_volume = float(self.config["USER"]["voice_volume"])
            self.play_voice_volume = self.master_volume * self.voice_volume / 10000
            self.language = str(self.config["USER"]["language"])
            self.player_key_bind_list = {player: ast.literal_eval(self.config["USER"]["keybind player " + str(player)])
                                         for player in self.player_list}
            self.player_key_control = {player: self.config["USER"]["control player " + str(player)] for player in
                                       self.player_list}
            if self.game_version != self.config["VERSION"]["ver"]:  # remake config as game version change
                raise KeyError  # cause KeyError to reset config file
        except (KeyError, TypeError, NameError):  # config error will make the game recreate config with default
            config = self.create_config()
            self.config = config
            self.show_fps = int(self.config["USER"]["fps"])
            self.screen_width = int(self.config["USER"]["screen_width"])
            self.screen_height = int(self.config["USER"]["screen_height"])
            self.full_screen = int(self.config["USER"]["full_screen"])
            self.master_volume = float(self.config["USER"]["master_volume"])
            self.music_volume = float(self.config["USER"]["music_volume"])
            self.play_music_volume = self.master_volume * self.music_volume / 10000
            self.effect_volume = float(self.config["USER"]["effect_volume"])
            self.play_effect_volume = self.master_volume * self.effect_volume / 10000
            self.voice_volume = float(self.config["USER"]["voice_volume"])
            self.play_voice_volume = self.master_volume * self.voice_volume / 10000
            self.language = str(self.config["USER"]["language"])
            self.player_key_bind_list = {player: ast.literal_eval(self.config["USER"]["keybind player " + str(player)])
                                         for player in self.player_list}
            self.player_key_control = {player: self.config["USER"]["control player " + str(player)] for player in
                                       self.player_list}

        Game.language = self.language

        # Set the display mode
        # game default screen size is 1920 x 1080, other resolution get scaled from there
        Game.screen_scale = (self.screen_width / 1920, self.screen_height / 1080)
        Game.screen_size = (self.screen_width, self.screen_height)

        self.window_style = 0
        if self.full_screen == 1:
            self.window_style = pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(self.screen_size, self.window_style)
        Game.screen_rect = self.screen.get_rect()

        Character.screen_scale = self.screen_scale
        Effect.screen_scale = self.screen_scale
        StageObject.screen_scale = self.screen_scale

        self.clock = pygame.time.Clock()  # set get clock

        self.loading = load_image(self.data_dir, self.screen_scale, "loading.png", ("ui", "mainmenu_ui"))
        self.loading = pygame.transform.scale(self.loading, self.screen_rect.size)

        self.joysticks = {}
        self.joystick_name = {}

        self.player_key_control = {player: self.config["USER"]["control player " + str(player)] for player in
                                   self.player_list}
        self.player_key_bind = {player: self.game.player_key_bind_list[player][self.player_key_control[player]] for
                                player in self.player_list}
        self.player_key_bind_name = {player: {value: key for key, value in self.player_key_bind[player].items()} for
                                     player in self.player_list}
        self.player_key_press = {player: {key: False for key in self.player_key_bind[player]} for player in
                                 self.player_list}
        self.player_key_hold = {player: {key: False for key in self.player_key_bind[player]} for player in
                                self.player_list}  # key that consider holding

        Game.ui_font = csv_read(self.data_dir, "ui_font.csv", ("ui",), header_key=True)
        for item in Game.ui_font:  # add ttf file extension for font data reading.
            Game.ui_font[item] = os.path.join(self.font_dir, Game.ui_font[item]["Font"] + ".ttf")
        Game.font_texture = load_images(self.data_dir, screen_scale=self.screen_scale,
                                        subfolder=("font", "texture"), as_pillow_image=True)

        # Decorate game icon window
        # icon = load_image(self.data_dir, "sword.jpg")
        # icon = pygame.transform.scale(icon, (32, 32))
        # pygame.display.set_icon(icon)

        # Initialise groups
        Game.ui_updater = ReversedLayeredUpdates()  # main drawer for ui in main menu
        Game.ui_drawer = pygame.sprite.LayeredUpdates()

        # game start menu group
        self.menu_icon = pygame.sprite.Group()  # mostly for option icon like volume or screen resolution
        self.menu_slider = pygame.sprite.Group()

        # lorebook group
        self.subsection_name = pygame.sprite.Group()  # subsection name objects group in lorebook blit on lore_name_list
        self.tag_filter_name = pygame.sprite.Group()  # tag filter objects group in lorebook blit on filter_name_list

        # battle object group
        Game.battle_camera = pygame.sprite.LayeredUpdates()  # layer drawer battle camera, all image pos should be based on the map not screen
        self.battle_ui_updater = ReversedLayeredUpdates()  # this is updater and drawer for ui, all image pos should be based on the screen
        self.battle_ui_drawer = pygame.sprite.LayeredUpdates()
        self.battle_cursor_drawer = pygame.sprite.LayeredUpdates()

        self.character_updater = pygame.sprite.Group()  # updater for character objects
        self.realtime_ui_updater = pygame.sprite.Group()  # for UI stuff that need to be updated in real time like drama and weather objects, also used as drawer
        self.effect_updater = pygame.sprite.Group()  # updater for effect objects (e.g. range attack sprite)

        self.all_chars = pygame.sprite.Group()  # group to keep all character object for cleaning
        self.all_effects = pygame.sprite.Group()

        self.button_ui = pygame.sprite.Group()  # ui button group in battle

        self.ui_boxes = pygame.sprite.Group()

        self.slider_menu = pygame.sprite.Group()  # volume slider in esc option menu

        self.unit_icon = pygame.sprite.Group()  # Character icon object group in selector ui
        self.weather_matters = pygame.sprite.Group()  # sprite of weather effect group such as rain sprite
        self.weather_effect = pygame.sprite.Group()  # sprite of special weather effect group such as fog that cover whole screen

        # Assign containers
        OptionMenuText.containers = self.menu_icon
        SliderMenu.containers = self.menu_slider, self.slider_menu

        MenuRotate.containers = self.ui_updater, self.ui_drawer
        MenuActor.containers = self.ui_updater, self.ui_drawer

        SubsectionName.containers = self.ui_updater, self.ui_drawer, self.battle_ui_updater, self.battle_ui_drawer

        # battle containers
        CharacterTextBox.containers = self.effect_updater, self.battle_camera
        CharacterIndicator.containers = self.effect_updater, self.battle_camera
        Drop.containers = self.effect_updater, self.battle_camera
        DamageNumber.containers = self.effect_updater, self.battle_camera
        BodyPart.containers = self.effect_updater, self.battle_camera
        Effect.containers = self.effect_updater, self.battle_camera
        StageObject.containers = self.effect_updater, self.battle_camera
        DamageEffect.containers = self.all_effects, self.effect_updater, self.battle_camera

        MenuCursor.containers = self.ui_updater, self.ui_drawer

        MatterSprite.containers = self.weather_matters, self.realtime_ui_updater
        SpecialWeatherEffect.containers = self.weather_effect, self.battle_ui_updater, self.battle_ui_drawer

        Character.containers = self.character_updater, self.all_chars

        # Create game cursor, make sure it is the first object in ui to be created, so it is always update first
        cursor_images = load_images(self.data_dir, subfolder=("ui", "cursor_menu"))  # no need to scale cursor
        self.cursor = MenuCursor(cursor_images)
        Game.cursor = self.cursor

        self.game_intro(False)  # run intro

        # Load game localisation data

        self.localisation = Localisation()
        Game.localisation = self.localisation

        # Battle related data
        self.character_data = CharacterData()
        self.battle_map_data = BattleMapData()

        Weather.weather_icons = self.battle_map_data.weather_icon

        self.preset_map_folder = self.battle_map_data.preset_map_folder
        self.battle_campaign = self.battle_map_data.battle_campaign  # for reference to preset campaign
        self.preset_map_data = self.battle_map_data.preset_map_data

        Character.character_data = self.character_data
        Character.status_list = self.character_data.status_list
        Character.effect_list = self.character_data.effect_list

        Drop.drop_item_list = self.character_data.drop_item_list

        Effect.effect_list = self.character_data.effect_list

        self.animation_data = AnimationData()
        self.character_animation_data = self.animation_data.character_animation_data  # animation data pool
        self.body_sprite_pool = self.animation_data.body_sprite_pool  # body sprite pool
        self.stage_object_animation_pool = self.animation_data.stage_object_animation_pool
        self.effect_sprite_pool = self.animation_data.effect_sprite_pool  # effect sprite pool
        self.effect_animation_pool = self.animation_data.effect_animation_pool  # effect sprite animation pool

        BodyPart.body_sprite_pool = self.body_sprite_pool
        Drop.effect_sprite_pool = self.effect_sprite_pool
        Effect.effect_sprite_pool = self.effect_sprite_pool
        Effect.effect_animation_pool = self.effect_animation_pool
        StageObject.stage_object_animation_pool = self.stage_object_animation_pool

        # Load sound effect
        self.sound_effect_pool = create_sound_effect_pool(self.data_dir)

        # Music player
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        if pygame.mixer:
            pygame.mixer.set_num_channels(1000)
            pygame.mixer.music.set_volume(self.play_music_volume)
            self.SONG_END = pygame.USEREVENT + 1
            self.music_list = glob.glob(self.data_dir + "/sound/music/menu.ogg")
            pygame.mixer.music.load(self.music_list[0])
            pygame.mixer.music.play(-1)

        # Main menu interface
        self.fps_count = FPSCount(self)  # FPS number counter
        if self.show_fps:
            self.add_ui_updater(self.fps_count)

        base_button_image_list = load_base_button(self.data_dir, self.screen_scale)

        main_menu_buttons_box = BoxUI((400, 500), parent=self.screen)

        f = 0.68
        self.start_game_button = BrownMenuButton((0, -0.6 * f), key_name="main_menu_start_game",
                                                 parent=main_menu_buttons_box)
        self.lore_button = BrownMenuButton((0, -0.2 * f), key_name="main_menu_lorebook", parent=main_menu_buttons_box)
        self.option_button = BrownMenuButton((0, 0.2 * f), key_name="game_option", parent=main_menu_buttons_box)
        self.quit_button = BrownMenuButton((0, 0.6 * f), key_name="game_quit", parent=main_menu_buttons_box)

        main_menu_button_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                              subfolder=("ui", "mainmenu_ui"))

        self.discord_button = URLIconLink(main_menu_button_images["discord"], (self.screen_width, 0),
                                          "https://discord.gg/q7yxz4netf")
        self.youtube_button = URLIconLink(main_menu_button_images["youtube"], self.discord_button.rect.topleft,
                                          "https://www.youtube.com/channel/UCgapwWog3mYhkEKIGW8VZtw")
        self.github_button = URLIconLink(main_menu_button_images["github"], self.youtube_button.rect.topleft,
                                         "https://github.com/remance/Royal-Ordains")

        self.mainmenu_button = (self.start_game_button, self.lore_button, self.option_button, self.quit_button,
                                self.discord_button, self.youtube_button)

        # Battle map select menu button
        self.map_title = MapTitle((self.screen_rect.width / 2, 0))

        # self.map_preview = MapPreview(self.preset_map_list_box.rect.topright)

        # UIScroll(self.unit_selector, self.unit_selector.rect.topright)  # scroll bar for character pick

        bottom_height = self.screen_rect.height - base_button_image_list[0].get_height()
        self.select_button = MenuButton(base_button_image_list,
                                        (self.screen_rect.width - base_button_image_list[0].get_width(), bottom_height),
                                        key_name="select_button")

        # Option menu button
        option_menu_dict = make_option_menu(base_button_image_list, self.config["USER"],
                                            self.player_key_bind_list[1])
        self.back_button = option_menu_dict["back_button"]
        self.keybind_button = option_menu_dict["keybind_button"]
        self.default_button = option_menu_dict["default_button"]
        self.resolution_drop = option_menu_dict["resolution_drop"]
        self.resolution_bar = option_menu_dict["resolution_bar"]
        self.resolution_text = option_menu_dict["resolution_text"]
        self.option_menu_sliders = option_menu_dict["volume_sliders"]
        self.value_boxes = option_menu_dict["value_boxes"]
        self.volume_texts = option_menu_dict["volume_texts"]
        self.fullscreen_box = option_menu_dict["fullscreen_box"]
        self.fullscreen_text = option_menu_dict["fullscreen_text"]
        self.fps_box = option_menu_dict["fps_box"]
        self.fps_text = option_menu_dict["fps_text"]
        self.keybind_text = option_menu_dict["keybind_text"]
        self.keybind_icon = option_menu_dict["keybind_icon"]
        self.control_switch = option_menu_dict["control_switch"]
        self.control_player_next = option_menu_dict["control_player_next"]
        self.control_player_back = option_menu_dict["control_player_back"]

        self.option_text_list = tuple(
            [self.resolution_text, self.fullscreen_text, self.fps_text] +
            [value for value in self.volume_texts.values()])
        self.option_menu_button = (
            self.back_button, self.default_button, self.keybind_button, self.resolution_drop,
            self.fullscreen_box, self.fps_box)

        # Character select menu button
        self.start_button = MenuButton(base_button_image_list,
                                       (self.screen_rect.width / 1.5, self.screen_rect.height / 1.05),
                                       key_name="start_button")
        self.char_back_button = MenuButton(base_button_image_list,
                                           (self.screen_rect.width / 4, self.screen_rect.height / 1.05),
                                           key_name="back_button")

        char_selector_images = load_images(self.data_dir, screen_scale=self.screen_scale,
                                           subfolder=("ui", "charselect_ui"), key_file_name_readable=True)
        self.player1_char_selector = CharacterSelector((self.screen_width / 8, self.screen_height / 2.1),
                                                       char_selector_images)
        self.player1_char_stat = CharacterStatAllocator(self.player1_char_selector.rect.center, 1)
        self.player2_char_selector = CharacterSelector((self.screen_width / 2.7, self.screen_height / 2.1),
                                                       char_selector_images)
        self.player2_char_stat = CharacterStatAllocator(self.player2_char_selector.rect.center, 2)
        self.player3_char_selector = CharacterSelector((self.screen_width / 1.6, self.screen_height / 2.1),
                                                       char_selector_images)
        self.player3_char_stat = CharacterStatAllocator(self.player3_char_selector.rect.center, 3)
        self.player4_char_selector = CharacterSelector((self.screen_width / 1.15, self.screen_height / 2.1),
                                                       char_selector_images)
        self.player4_char_stat = CharacterStatAllocator(self.player4_char_selector.rect.center, 4)
        self.player_char_selectors = {1: self.player1_char_selector, 2: self.player2_char_selector,
                                      3: self.player3_char_selector, 4: self.player4_char_selector}
        self.player_char_stats = {1: self.player1_char_stat, 2: self.player2_char_stat,
                                  3: self.player3_char_stat, 4: self.player4_char_stat}
        self.char_menu_button = (self.player1_char_selector, self.player2_char_selector, self.player3_char_selector,
                                 self.player4_char_selector, self.char_back_button, self.start_button)

        # User input popup ui
        input_ui_dict = make_input_box(self.data_dir, self.screen_scale, self.screen_rect,
                                       load_base_button(self.data_dir, self.screen_scale))
        self.input_ui = input_ui_dict["input_ui"]
        self.input_ok_button = input_ui_dict["input_ok_button"]
        self.input_close_button = input_ui_dict["input_close_button"]
        self.input_cancel_button = input_ui_dict["input_cancel_button"]
        self.input_box = input_ui_dict["input_box"]
        self.input_ui_popup = (self.input_ok_button, self.input_cancel_button, self.input_ui, self.input_box)
        self.confirm_ui_popup = (self.input_ok_button, self.input_cancel_button, self.input_ui)
        self.inform_ui_popup = (self.input_close_button, self.input_ui, self.input_box)
        self.all_input_ui_popup = (self.input_ok_button, self.input_cancel_button, self.input_close_button,
                                   self.input_ui, self.input_box)

        # Text popup
        self.text_popup = TextPopup()  # popup box that show text when mouse over something

        # Encyclopedia interface
        Lorebook.history_lore = self.localisation.create_lore_data("history")
        Lorebook.character_lore = self.localisation.create_lore_data("character")
        Lorebook.enemy_lore = self.localisation.create_lore_data("enemy")
        Lorebook.equipment_lore = self.localisation.create_lore_data("item")
        Lorebook.status_lore = self.localisation.create_lore_data("status")
        Lorebook.event_lore = self.localisation.create_lore_data("event")

        Lorebook.character_data = self.character_data

        self.lorebook, self.lore_name_list, self.filter_tag_list, self.lore_buttons = make_lorebook(self)

        self.lorebook_stuff = (self.lorebook, self.lore_name_list, self.filter_tag_list,
                               self.lore_name_list.scroll, self.filter_tag_list.scroll, self.lore_buttons.values())

        self.battle = Battle(self)

        Game.battle = self.battle
        Character.battle = self.battle
        Drop.battle = self.battle
        BodyPart.battle = self.battle
        Effect.battle = self.battle
        StageObject.battle = self.battle

        # Background image
        self.background_image = load_images(self.data_dir, screen_scale=self.screen_scale,
                                            subfolder=("ui", "mainmenu_ui", "background"))
        self.atlas = MenuRotate((self.screen_width / 2, self.screen_height / 2), self.background_image["atlas"], 5)
        self.hide_background = StaticImage((self.screen_width / 2, self.screen_height / 2),
                                           self.background_image["hide"])
        self.menu_actor_data = csv_read(self.data_dir, "menu_actor.csv", ("ui",), header_key=True)
        self.menu_actors = []
        # for stuff in self.menu_actor_data.values():
        #     if stuff["Type"] == "character":
        #         if "-" in stuff["ID"]:
        #             who_todo = {key: value for key, value in self.leader_data.leader_list.items() if key == stuff["ID"]}
        #         else:
        #             who_todo = {key: value for key, value in self.character_data.troop_list.items() if key == stuff["ID"]}
        #         sprite_direction = rotation_dict[min(rotation_list, key=lambda x: abs(
        #             x - stuff["Angle"]))]  # find closest in list of rotation for sprite direction
        #         preview_sprite_pool, _ = self.create_character_sprite_pool(who_todo, preview=True,
        #                                                                specific_preview=(stuff["Animation"],
        #                                                                                  None,
        #                                                                                  sprite_direction),
        #                                                                max_preview_size=stuff["Size"])
        #
        #         self.menu_actors.append(MenuActor((float(stuff["POS"].split(",")[0]) * self.screen_width,
        #                                            float(stuff["POS"].split(",")[1]) * self.screen_height),
        #                                           preview_sprite_pool[stuff["ID"]]))

        # self.background = self.background_image["main"]

        # Starting script
        self.player_char_select = {1: None, 2: None, 3: None, 4: None}

        self.dt = 0
        self.text_delay = 0
        self.url_delay = 0
        self.add_ui_updater(self.mainmenu_button)

        self.menu_state = "main_menu"
        self.input_popup = None  # popup for text input state

        self.loading_screen("end")

        self.run()

    def game_intro(self, intro):
        timer = 0
        while intro:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    intro = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            pygame.display.update()
            self.clock.tick(1000)
            timer += 1
            if timer == 1000:
                intro = False

        self.loading_screen("start")

        pygame.display.set_caption(game_name)  # set the self name on program border/tab

    def add_ui_updater(self, *args):
        self.ui_updater.add(*args)
        self.ui_drawer.add(*args)

    def remove_ui_updater(self, *args):
        self.ui_updater.remove(*args)
        self.ui_drawer.remove(*args)

    def setup_profiler(self):
        self.profiler = Profiler()
        self.profiler.enable()
        self.battle.realtime_ui_updater.add(self.profiler)

    def run(self):
        while True:
            # Get user input
            self.dt = self.clock.get_time() / 1000  # dt before game_speed
            self.cursor.scroll_down = False
            self.cursor.scroll_up = False
            esc_press = False

            self.player_key_press = {key: dict.fromkeys(self.player_key_press[key], False) for key in
                                     self.player_key_press}
            self.player_key_hold = {key: dict.fromkeys(self.player_key_hold[key], False) for key in
                                    self.player_key_hold}

            key_press = pygame.key.get_pressed()

            if self.url_delay:
                self.url_delay -= self.dt
                if self.url_delay < 0:
                    self.url_delay = 0

            if self.config["USER"]["control player 1"] == "joystick" and self.input_popup[0] == "keybind_input":
                for joystick in self.joysticks.values():  # TODO change this when has multiplayer
                    for i in range(joystick.get_numaxes()):
                        if joystick.get_axis(i):
                            if i not in (2, 3):  # prevent right axis from being assigned
                                axis_name = "axis" + number_to_minus_or_plus(joystick.get_axis(i)) + str(i)
                                self.assign_key(axis_name)

                    for i in range(joystick.get_numhats()):
                        if joystick.get_hat(i)[0]:
                            hat_name = "hat" + number_to_minus_or_plus(joystick.get_axis(i)) + str(0)
                            self.assign_key(hat_name)
                        elif joystick.get_hat(i)[1]:
                            hat_name = "hat" + number_to_minus_or_plus(joystick.get_axis(i)) + str(1)
                            self.assign_key(hat_name)

            key_state = pygame.key.get_pressed()

            for player, key_set in self.player_key_press.items():
                if self.player_key_control[player] == "keyboard":
                    for key in key_set:  # check for key holding
                        if type(self.player_key_bind[player][key]) == int and key_state[
                            self.player_key_bind[player][key]]:
                            self.player_key_hold[player][key] = True

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 4:  # Mouse scroll down
                        self.cursor.scroll_up = True
                    elif event.button == 5:  # Mouse scroll up
                        self.cursor.scroll_down = True

                elif event.type == pygame.JOYBUTTONUP:
                    joystick = event.instance_id
                    if self.config["USER"]["control player 1"] == "joystick" and self.input_popup[0] == "keybind_input":
                        # check for button press
                        self.assign_key(event.button)

                elif event.type == pygame.KEYDOWN:
                    event_key_press = event.key
                    if self.input_popup:  # event update to input box

                        if event.key == pygame.K_ESCAPE:
                            esc_press = True

                        elif self.input_popup[0] == "keybind_input" and \
                                self.config["USER"]["control player 1"] == "keyboard":
                            self.assign_key(event.key)

                        elif self.input_popup[0] == "text_input":
                            self.input_box.player_input(event, key_press)
                            self.text_delay = 0.1
                    else:
                        for player in self.player_key_control:
                            if self.player_key_control[player] == "keyboard" and \
                                    event_key_press in self.player_key_bind_name[player]:  # check for key press
                                self.player_key_press[player][self.player_key_bind_name[player][event_key_press]] = True

                        if event.key == pygame.K_ESCAPE:
                            esc_press = True

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

                elif event.type == pygame.JOYDEVICEREMOVED:
                    # Player unplug joystick
                    del self.joysticks[event.instance_id]
                    del self.joystick_name[event.instance_id]

                elif event.type == QUIT:
                    esc_press = True

            self.remove_ui_updater(self.text_popup)
            self.ui_updater.update()

            # Reset screen
            self.screen.fill((220, 220, 180))
            # self.screen.blit(self.background, (0, 0))  # blit background over instead of clear() to reset screen

            if self.input_popup:  # currently, have input text pop up on screen, stop everything else until done
                if self.input_ok_button.event_press or key_press[pygame.K_RETURN] or key_press[pygame.K_KP_ENTER]:
                    done = True
                    if "replace key" in self.input_popup[1]:
                        old_key = self.player_key_bind[1][self.config["USER"]["control player 1"]][
                            self.input_popup[1][1]]
                        self.player_key_bind[1][self.config["USER"]["control player 1"]][
                            self.input_popup[1][1]] = self.player_key_bind[1][self.config["USER"]["control player 1"]][
                            self.input_popup[1][2]]
                        self.player_key_bind[1][self.config["USER"]["control player 1"]][
                            self.input_popup[1][2]] = old_key
                        edit_config("USER", "keybind player 1", self.player_key_bind[1],
                                    self.config_path, self.config)
                        for key, value in self.keybind_icon.items():
                            if key == self.input_popup[1][1]:
                                if self.joysticks:
                                    value.change_key(self.config["USER"]["control player 1"],
                                                     self.player_key_bind[1][self.config["USER"]["control player 1"]][
                                                         self.input_popup[1][1]],
                                                     self.joystick_bind_name[
                                                         self.joystick_name[tuple(self.joystick_name.keys())[0]]])
                                else:
                                    value.change_key(self.config["USER"]["control player 1"],
                                                     self.player_key_bind[1][self.config["USER"]["control player 1"]][
                                                         self.input_popup[1][1]], None)

                            elif key == self.input_popup[1][2]:
                                if self.joysticks:
                                    value.change_key(self.config["USER"]["control player 1"],
                                                     self.player_key_bind[1][self.config["USER"]["control player 1"]][
                                                         self.input_popup[1][2]],
                                                     self.joystick_bind_name[
                                                         self.joystick_name[tuple(self.joystick_name.keys())[0]]])
                                else:
                                    value.change_key(self.config["USER"]["control player 1"],
                                                     self.player_key_bind[1][self.config["USER"]["control player 1"]][
                                                         self.input_popup[1][2]], None)

                        self.player_key_bind_name = {1: {value: key for key, value in self.player_key_bind[1].items()}}
                        self.player_key_press = {key: dict.fromkeys(self.player_key_bind[key], False) for key in
                                                 self.player_key_bind}
                        self.player_key_hold = {key: dict.fromkeys(self.player_key_bind[key], False) for key in
                                                self.player_key_bind}

                    elif self.input_popup[1] == "quit":
                        pygame.time.wait(1000)
                        if pygame.mixer:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.unload()
                        pygame.quit()
                        sys.exit()

                    if done:
                        self.change_pause_update(False)
                        self.input_box.text_start("")
                        self.input_popup = None
                        self.remove_ui_updater(self.all_input_ui_popup)

                elif self.input_cancel_button.event_press or self.input_close_button.event_press or esc_press:
                    self.change_pause_update(False)
                    self.input_box.text_start("")
                    self.input_popup = None
                    self.remove_ui_updater(self.all_input_ui_popup)

                elif self.input_popup[0] == "text_input":
                    if self.text_delay == 0:
                        if key_press[self.input_box.hold_key]:
                            self.input_box.player_input(None, key_press)
                            self.text_delay = 0.1
                    else:
                        self.text_delay += self.dt
                        if self.text_delay >= 0.3:
                            self.text_delay = 0

            elif not self.input_popup:
                if self.menu_state == "main_menu":
                    self.menu_main(esc_press)

                elif self.menu_state == "char":
                    self.menu_char(esc_press)

                elif self.menu_state == "option":
                    self.menu_option(esc_press)

                elif self.menu_state == "keybind":
                    self.menu_keybind(esc_press)

                elif self.menu_state == "lorebook":
                    command = self.lorebook_process(esc_press)
                    if esc_press or command == "exit":
                        self.menu_state = "main_menu"  # change menu back to default 0

            self.ui_drawer.draw(self.screen)
            pygame.display.update()
            self.clock.tick(300)
